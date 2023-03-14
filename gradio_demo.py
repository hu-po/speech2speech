import io
import logging
import os
import random
import time
from typing import Dict, List

import gradio as gr
import sounddevice as sd
import soundfile as sf
import yaml

from elevenlabs import (ElevenLabsVoice, check_voice_exists, get_make_voice,
                        text_to_speechbytes)
from openailib import fake_conversation, speech_to_text
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
DEFAULT_VOICES = random.choices(NAMES, k=2)
DEFAULT_IAM = random.choice(DEFAULT_VOICES)

def poll_audio(audio):
    return ''

def conversation(names, iam, audio, model, max_tokens, temperature, timeout):
    assert iam in names, f"I am {iam} but I don't have a voice"
    loaded_voices: Dict[str, ElevenLabsVoice] = {}
    for name in names:
        assert check_voice_exists(
            name) is not None, f"Voice {name} does not exist"
        loaded_voices[name] = get_make_voice(name)
    request = speech_to_text(audio)
    response = fake_conversation(names, iam, request, model=model, max_tokens=max_tokens, temperature=temperature)
    
    history = []
    for line in response.splitlines():
        try:
            # check if line is empty
            if not line:
                continue
            assert ":" in line, f"Line {line} does not have a colon"
            name, text = line.split(":")
            assert name in NAMES, f"Name {name} is not in {NAMES}"
            voice = loaded_voices[name]
            assert len(text) > 0, f"Text {text} is empty"
            history.append((voice, text))
        except AssertionError as e:
            log.warning(e)
            continue

    for voice, text in history:
        speech_bytes: bytes = text_to_speechbytes(text, voice)
        audioFile = io.BytesIO(speech_bytes)
        soundFile = sf.SoundFile(audioFile)
        sd.play(soundFile.read(), samplerate=soundFile.samplerate, blocking=True)
        # Interrupt buffer
        time.sleep(random.uniform(1, 0.5))

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
        
        gr_chars = gr.CheckboxGroup(NAMES, label="Characters", value=DEFAULT_VOICES)
        gr_iam = gr.Dropdown(choices=NAMES, label="I am", value=DEFAULT_IAM)
        gr_mic = gr.Audio(
            source="microphone",
            # value=poll_audio,
            # every=3,
            type="filepath",
            )
        with gr.Accordion("Settings", open=False):
            gr_model = gr.Dropdown(choices=["gpt-3.5-turbo"],
                                   label='model', value="gpt-3.5-turbo")
            gr_max_tokens = gr.Slider(minimum=1, maximum=500, value=75,
                                      label="Max tokens", step=1)
            gr_temperature = gr.Slider(
                minimum=0.0, maximum=1.0, value=0.5, label="Temperature")
            gr_timeout = gr.Slider(minimum=1, maximum=60, value=10,
                                   label="Timeout on individual agents", step=1)
            gr_samplerate = gr.Slider(minimum=1, maximum=48000, value=48000,
                                      label="Samplerate", step=1),
            gr_channels = gr.Slider(minimum=1, maximum=2, value=1,
                                    label="Channels", step=1),
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
