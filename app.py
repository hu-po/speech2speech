import asyncio
import logging
import os
import random
from typing import Dict, List, Tuple
import glob

import gradio as gr
import yaml

from src.elevenlabs import (Speaker, check_voice_exists, get_make_voice,
                            play_history, save_history)
from src.openailib import top_response, speech_to_text
from src.tube import extract_audio

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class ConversationState:
    COLORS: list = ['#FFA07A', '#F08080', '#AFEEEE', '#B0E0E6', '#DDA0DD',
                    '#FFFFE0', '#F0E68C', '#90EE90', '#87CEFA', '#FFB6C1']
    YAML_FILEPATH: str = os.path.join(os.path.dirname(__file__), 'voices.yaml')
    AUDIO_SAVEDIR: str = os.path.join(
        os.path.dirname(__file__), 'audio_export')

    def __init__(self,
                 names: list = None,
                 iam: str = None,
                 model: str = "gpt-3.5-turbo",
                 max_tokens: int = 15,
                 temperature: float = 0.5,
                 history: list = None):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        # Make sure save dir exists, make any necessary directories
        os.makedirs(self.AUDIO_SAVEDIR, exist_ok=True)
        self.audio_savepath = os.path.join(
            self.AUDIO_SAVEDIR, 'conversation.wav')
        log.info(f"Resetting conversation")
        with open(self.YAML_FILEPATH, 'r') as file:
            self.characters_yaml = file.read()
            file.seek(0)
            self.characters_dict = yaml.safe_load(file)
            self.all_characters = [
                name for name in self.characters_dict.keys()]
        self.names = names or random.choices(self.all_characters, k=2)
        self.iam = iam or random.choice(self.names)
        assert self.iam in self.names, f"{self.iam} not in {self.names}"
        log.info(f"Loading voices")
        self.speakers: Dict[str, Speaker] = {}
        self.speakers_descriptions: str = ''
        for i, name in enumerate(self.names):
            assert check_voice_exists(
                name) is not None, f"Voice {name} does not exist"
            _speaker = Speaker(
                name=name,
                voice=get_make_voice(name),
                color=self.COLORS[i % len(self.COLORS)],
                description=self.characters_dict[name].get(
                    "description", None),
            )
            self.speakers[name] = _speaker
            if _speaker.description is not None:
                self.speakers_descriptions += f"{_speaker.name}: {_speaker.description}.\n"
        # System is fed into OpenAI to condition the prompt
        self.system = f"You create funny conversation dialogues."
        self.system += f"This conversation is between {', '.join(self.names)}."
        self.system += "Do not introduce new characters."
        self.system += "Only return the script itself, every line must start with a character name."
        self.system += "Descriptions for each of the characters are:\n"
        for speaker in self.speakers.values():
            self.system += f"{speaker.name}: {speaker.description}\n"
        # History is fed in at every step
        self.step = 0
        if history is None:
            self.history: List[Tuple[Speaker, str]] = []

    def add_to_history(self, text: str, speaker: Speaker = None):
        if speaker is None:
            speaker = self.speakers[self.iam]
        self.history.append((speaker, text))

    def history_to_prompt(self) -> str:
        prompt: str = ''
        for speaker, text in self.history:
            prompt += f"{speaker.name}:{text}\n"
        return prompt

    def html_history(self) -> str:
        history_html: str = ''
        for speaker, text in self.history:
            _bubble = f"<div style='background-color: {speaker.color}; border-radius: 5px; padding: 5px; margin: 5px;'>{speaker.name}: {text}</div>"
            history_html += _bubble
        return history_html


# Storing state in the global scope like this is bad, but
# perfect is the enemy of good enough and gradio is kind of shit
STATE = ConversationState()


def reset(names, iam, model, max_tokens, temperature):
    # Push new global state to the global scope
    global STATE
    STATE = ConversationState(
        names=names,
        iam=iam,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return STATE.html_history()


def step_mic(audio):
    global STATE
    try:
        request = speech_to_text(audio)
        STATE.add_to_history(request)
    except TypeError as e:
        log.warning(e)
        pass
    return STATE.html_history()


def step_continue():
    global STATE
    response = top_response(STATE.history_to_prompt(),
                            system=STATE.system,
                            model=STATE.model,
                            max_tokens=STATE.max_tokens,
                            temperature=STATE.temperature,
                            )
    for line in response.splitlines():
        try:
            # TODO: Add any filters here as assertion errors
            if not line:
                continue
            assert ":" in line, f"Line {line} does not have a colon"
            name, text = line.split(":")
            assert name in STATE.all_characters, f"Name {name} is not in {STATE.all_characters}"
            speaker = STATE.speakers[name]
            assert len(text) > 0, f"Text {text} is empty"
            STATE.add_to_history(text, speaker=speaker)
        except AssertionError as e:
            log.warning(e)
            continue
    return STATE.html_history()


def save_audio():
    global STATE
    log.info(f"Saving audio")
    asyncio.run(save_history(STATE.history, STATE.audio_savepath))
    return STATE.html_history()


def play_audio():
    global STATE
    log.info(f"Playing audio")
    asyncio.run(play_history(STATE.history))
    return STATE.html_history()


def make_voices(voices_yaml: str):
    global STATE
    try:
        STATE.characters_dict = yaml.safe_load(voices_yaml)
        for name, metadata in STATE.characters_dict.items():
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


# Define the main GradIO UI
with gr.Blocks() as demo:
    with gr.Tab("Conversation"):
        gr_convo_output = gr.HTML()
        with gr.Row():
            with gr.Column():
                gr_mic = gr.Audio(
                    label="Record audio into conversation",
                    source="microphone",
                    type="filepath",
                    # streaming=True,
                )
                gr_add_button = gr.Button(value="Add to conversation")
                gr_reset_button = gr.Button(value="Reset conversation")
                gr_saveaudio_button = gr.Button(value="Export audio")
                gr_playaudio_button = gr.Button(value="Play audio")
            with gr.Column():
                gr_chars = gr.CheckboxGroup(
                    STATE.all_characters, label="Characters", value=STATE.names)
                gr_iam = gr.Dropdown(choices=STATE.names,
                                     label="I am", value=STATE.iam)
            with gr.Accordion("Settings", open=False):
                gr_model = gr.Dropdown(choices=["gpt-3.5-turbo", "gpt-4"],
                                       label='GPT Model behind conversation', value=STATE.model)
                gr_max_tokens = gr.Slider(minimum=1, maximum=500, value=STATE.max_tokens,
                                          label="Max tokens", step=1)
                gr_temperature = gr.Slider(
                    minimum=0.0, maximum=1.0, value=STATE.temperature, label="Temperature (randomness in conversation)")
    with gr.Tab("New Characters"):
        gr_make_voice_button = gr.Button(value="Update Characters")
        gr_voice_data = gr.Textbox(
            lines=25, label="Character YAML config", value=STATE.characters_yaml)
        gr_make_voice_output = gr.Textbox(
            lines=2, label="Character creation logs...")

    # Buttons and actions
    gr_mic.change(step_mic, gr_mic, gr_convo_output)
    gr_add_button.click(step_continue, None, gr_convo_output)
    gr_reset_button.click(
        reset,
        inputs=[gr_chars, gr_iam, gr_model, gr_max_tokens, gr_temperature],
        outputs=[gr_convo_output],
    )
    gr_saveaudio_button.click(save_audio, None, None)
    gr_playaudio_button.click(play_audio, None, None)
    gr_make_voice_button.click(
        make_voices, inputs=gr_voice_data, outputs=gr_make_voice_output,
    )

if __name__ == "__main__":
    demo.launch()
