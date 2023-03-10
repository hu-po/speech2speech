import logging
import os
import time

import gradio as gr

from openailib import speech_to_text, respond_with_system_context
from elevenlabs import text_to_speech

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def run(audio, context, model, max_tokens, temperature, voice):
    request = speech_to_text(audio)
    response = respond_with_system_context(
        request, context, model, max_tokens, temperature)
    text_to_speech(response, voice)
    return f"--Request--\n{request}\n\n--Response--\n{response}"


# Create interface
interface = gr.Interface(
    run,
    [
        gr.Audio(source="microphone", type="filepath"),
        gr.Textbox(lines=2, label="Context",
                   value="You are helpful and kind, you chat with people and help them understand themselves."),
        gr.Dropdown(choices=["gpt-3.5-turbo"], value="gpt-3.5-turbo"),
        gr.Slider(minimum=1, maximum=100, value=20,
                  label="Max tokens", step=1),
        gr.Slider(minimum=0.0, maximum=1.0, value=0.5, label="Temperature"),
        gr.Dropdown(choices=["don", "barry", "joe",
                    "Hugo", "Adam", "Rachel"], value="don"),
    ],
    [
        gr.Textbox(lines=2, label="Output")
    ],
    title="Maiself",
    description="Chat with yourself using OpenAI Whisper, OpenAI GPT-3 and ElevenLabs Voices",
)

if __name__ == "__main__":
    interface.launch()
