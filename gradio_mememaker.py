import logging
import os
import time

import gradio as gr

from openailib import speech_to_text, fake_conversation
from elevenlabs import text_to_speech, get_make_voice

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

NAMES = ["Joe", "Barry", "Don", "Hugo", "Lex", "Elon"]


def run(voices, iam, audio, model, max_tokens, temperature):
    for voice in voices:
        assert get_make_voice(voice) is not None, f"Voice {voice} does not exist"
    assert iam in voices, f"I am {iam} but I don't have a voice"
    request = speech_to_text(audio)
    response = fake_conversation(
        voices, iam, request, model=model, max_tokens=max_tokens, temperature=temperature)
    for line in response.splitlines():
        for name in NAMES:
            if line.startswith(name):
                character, text = line.split(":")
                text_to_speech(text, character)
    return f"--Request--\n{request}\n\n--Response--\n{response}"

# Create interface
interface = gr.Interface(
    run,
    [
        gr.CheckboxGroup(NAMES, label="Characters"),
        gr.Dropdown(choices=NAMES, label="I am"),
        gr.Audio(source="microphone", type="filepath"),
        gr.Dropdown(choices=["gpt-3.5-turbo"],
                    label='model', value="gpt-3.5-turbo"),
        gr.Slider(minimum=1, maximum=500, value=100,
                  label="Max tokens", step=1),
        gr.Slider(minimum=0.0, maximum=1.0, value=0.5, label="Temperature"),
    ],
    [
        gr.Textbox(lines=2, label="Output")
    ],
    title="Meme generator",
)

if __name__ == "__main__":
    interface.launch()
