import asyncio
import logging
import os
import random
from dataclasses import dataclass
from typing import Dict

import gradio as gr
import yaml

from src.elevenlabs import (Speaker, check_voice_exists, get_make_voice,
                            play_history)
from src.openailib import fake_conversation, speech_to_text
from src.tube import extract_audio

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

COLORS = ['#FFA07A', '#F08080', '#AFEEEE', '#B0E0E6', '#DDA0DD',
          '#FFFFE0', '#F0E68C', '#90EE90', '#87CEFA', '#FFB6C1']
YAML_FILEPATH = os.path.join(os.path.dirname(__file__), 'voices.yaml')

with open(YAML_FILEPATH, 'r') as file:
    DEFAULT_VOICES_STR = file.read()
with open(YAML_FILEPATH, 'r') as file:
    VOICES = yaml.safe_load(file)
    NAMES = [name for name in VOICES.keys()]
DEFAULT_VOICES = random.choices(NAMES, k=2)
DEFAULT_IAM = random.choice(DEFAULT_VOICES)


def conversation(names, iam, audio, model, max_tokens, temperature, timeout, samplerate, channels):
    global VOICES
    assert iam in names, f"{iam} is not in {names}"
    speakers: Dict[str, Speaker] = {}
    for i, name in enumerate(names):
        assert check_voice_exists(
            name) is not None, f"Voice {name} does not exist"
        speakers[name] = Speaker(
            name=name,
            voice=get_make_voice(name),
            color=COLORS[i % len(COLORS)],
            description=VOICES[name].get("description", None),
        )
    request = speech_to_text(audio)

    # Add request to history for output printint
    history_html = []
    _bubble = f"<div style='background-color: {speakers[iam].color}; border-radius: 5px; padding: 5px; margin: 5px;'>{request}</div>"
    history_html.append(_bubble)

    history = []
    _speakers = [s for s in speakers.values()]
    response = fake_conversation(_speakers, history, iam, request, model=model, max_tokens=max_tokens, temperature=temperature)
    for line in response.splitlines():
        try:
            # TODO: Add any filters here as assertion errors
            if not line:
                continue
            assert ":" in line, f"Line {line} does not have a colon"
            name, text = line.split(":")
            assert name in NAMES, f"Name {name} is not in {NAMES}"
            speaker = speakers[name]
            assert len(text) > 0, f"Text {text} is empty"
            history.append((speaker, text))
            _bubble = f"<div style='background-color: {speaker.color}; border-radius: 5px; padding: 5px; margin: 5px;'>{text}</div>"
            history_html.append(_bubble)
        except AssertionError as e:
            log.warning(e)
            continue
    asyncio.run(play_history(history))
    return ''.join(history_html)


def make_voices(voices_yaml: str):
    global VOICES
    try:
        VOICES = yaml.safe_load(voices_yaml)
        for name, metadata in VOICES.items():
            videos = metadata['references']
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

        gr_chars = gr.CheckboxGroup(
            NAMES, label="Characters", value=DEFAULT_VOICES)
        gr_iam = gr.Dropdown(choices=NAMES, label="I am", value=DEFAULT_IAM)
        gr_mic = gr.Audio(
            source="microphone",
            # value=poll_audio,
            # every=3,
            type="filepath",
        )
        with gr.Accordion("Settings", open=False):
            gr_model = gr.Dropdown(choices=["gpt-3.5-turbo", "gpt-4"],
                                   label='model', value="gpt-3.5-turbo")
            gr_max_tokens = gr.Slider(minimum=1, maximum=500, value=75,
                                      label="Max tokens", step=1)
            gr_temperature = gr.Slider(
                minimum=0.0, maximum=1.0, value=0.5, label="Temperature")
            gr_timeout = gr.Slider(minimum=1, maximum=60, value=10,
                                   label="Timeout on individual agents", step=1)
            gr_samplerate = gr.Slider(minimum=1, maximum=48000, value=48000,
                                      label="Samplerate", step=1)
            gr_channels = gr.Slider(minimum=1, maximum=2, value=1,
                                    label="Channels", step=1)
        gr_convo_button = gr.Button(label="Start conversation")
        gr_convo_output = gr.HTML()
    with gr.Tab("Make Voices"):
        gr_voice_data = gr.Textbox(
            lines=25, label="YAML for voices", value=DEFAULT_VOICES_STR)
        gr_make_voice_button = gr.Button(label="Make voice")
        gr_make_voice_output = gr.Textbox(lines=2, label="Output")

    gr_convo_button.click(conversation,
                          inputs=[gr_chars, gr_iam, gr_mic, gr_model, gr_max_tokens,
                                  gr_temperature, gr_timeout, gr_samplerate, gr_channels],
                          outputs=[gr_convo_output],
                          )
    gr_make_voice_button.click(
        make_voices, inputs=gr_voice_data, outputs=gr_make_voice_output)

if __name__ == "__main__":
    demo.launch()
