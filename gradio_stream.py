import os
import logging
import yaml
from typing import Dict, List

import gradio as gr

from openailib import speech_to_text, fake_conversation
from elevenlabs import text_to_speech, get_make_voice, check_voice_exists
from tube import extract_audio

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# TODO: better way to do this
YAML_FILEPATH = os.path.join(os.path.dirname(__file__), "voices.yaml")
with open(YAML_FILEPATH, 'r') as file:
    VOICES_YAML = file.read()
with open(YAML_FILEPATH, 'r') as file:
    _dict = yaml.safe_load(file)
    NAMES = [name for name in _dict.keys()]


def conversation(voices, iam, audio, model, max_tokens, temperature):
    for voice in voices:
        assert get_make_voice(
            voice) is not None, f"Voice {voice} does not exist"
    assert iam in voices, f"I am {iam} but I don't have a voice"
    request = speech_to_text(audio)
    response = fake_conversation(
        voices, iam, request, model=model, max_tokens=max_tokens, temperature=temperature)
    for line in response.splitlines():
        for name in NAMES:
            if line.startswith(name):
                character, text = line.split(":")
                text_to_speech(text, character)
    return ''


def make_voices(voices_yaml: str):
    try:
        voice_dict: Dict = yaml.safe_load(voices_yaml)
        for name, videos in voice_dict.items():
            assert isinstance(name, str), f"Name {name} is not a string"
            assert isinstance(videos, list), f"Videos {videos} is not a list"
            if check_voice_exists(name):
                continue
            audio_paths = []
            for i, video in enumerate(videos):
                assert isinstance(video, Dict), f"Video {video} is not a dict"
                assert 'url' in video, f"Video {video} does not have a url"
                url = video['url']
                start_minute = video.get('start_minute', 0)
                duration = video.get('duration', 120)
                label = f"audio.{name}.{i}"
                output_path = extract_audio(url, label, start_minute, duration)
                audio_paths.append(output_path)
            get_make_voice(name, audio_paths)
    except Exception as e:
        raise e
        # return f"Error: {e}"
    return "Success"


with gr.Blocks() as demo:
    with gr.Tab("Conversation"):
        gr_chars = gr.CheckboxGroup(NAMES, label="Characters")
        gr_iam = gr.Dropdown(choices=NAMES, label="I am")
        gr_mic = gr.Audio(source="microphone", type="filepath")
        with gr.Accordion("Settings", open=False):
            gr_model = gr.Dropdown(choices=["gpt-3.5-turbo"],
                                   label='model', value="gpt-3.5-turbo")
            gr_max_tokens = gr.Slider(minimum=1, maximum=500, value=75,
                                      label="Max tokens", step=1)
            gr_temperature = gr.Slider(
                minimum=0.0, maximum=1.0, value=0.5, label="Temperature")
        gr_convo_button = gr.Button(label="Start conversation")
        gr_convo_output = gr.Textbox(lines=2, label="Output")
    with gr.Tab("Make Voices"):
        gr_voice_data = gr.Textbox(
            lines=25, label="YAML for voices", value=VOICES_YAML)
        gr_make_voice_button = gr.Button(label="Make voice")
        gr_make_voice_output = gr.Textbox(lines=2, label="Output")

    gr_convo_button.click(conversation,
                          inputs=[gr_chars, gr_iam, gr_mic, gr_model,
                                  gr_max_tokens, gr_temperature],
                          outputs=[gr_convo_output],
                          )
    gr_make_voice_button.click(
        make_voices, inputs=gr_voice_data, outputs=gr_make_voice_output)

if __name__ == "__main__":
    demo.launch()
