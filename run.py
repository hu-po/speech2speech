import logging
import os
import time

import gradio as gr
import openai
from elevenlabslib import ElevenLabsUser

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def text_to_speech(text: str, voice: str = "Hugo"):
    log.info(f"Generating audio using voice {voice}...")
    time_start = time.time()
    user = ElevenLabsUser(os.environ["ELEVENLABS_API_KEY"])
    _voice = user.get_voices_by_name(voice)[0]
    _voice.generate_and_play_audio(text, playInBackground=False)
    log.info(f"Audio duration: {time.time() - time_start:.2f} seconds")


def run(audio, context, model, max_tokens, temperature, voice):
    request = speech_to_text(audio)
    response = request_to_response(
        request, context, model, max_tokens, temperature)
    text_to_speech(response, voice)
    return f"--Request--\n{request}\n\n--Response--\n{response}"


def speech_to_text(audio_path):
    log.info("Transcribing audio...")
    time_start = time.time()
    transcript = openai.Audio.transcribe("whisper-1", open(audio_path, "rb"))
    text = transcript["text"]
    log.info(f"Transcription duration: {time.time() - time_start:.2f} seconds")
    log.info(f"Transcript: \n\t{text}")
    return text


def request_to_response(request, context, model="gpt-3.5-turbo", max_tokens=20, temperature=0.5):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    time_start = time.time()
    log.info(f"GPT-3 Starting")
    _response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": context,
            },
            {
                "role": "user",
                "content": request,
            },
        ],
        temperature=temperature,
        n=1,
        max_tokens=max_tokens,
    )
    response: str = _response['choices'][0]['message']['content']
    log.info(f"GPT-3 duration: {time.time() - time_start:.2f} seconds")
    log.info(f" Response: \n\t{response}")
    return response


# Create interface
interface = gr.Interface(
    run,
    [
        gr.Audio(source="microphone", type="filepath"),
        gr.Textbox(lines=2, label="Context",
                   value="You are helpful and kind, you chat with people and help them understand themselves."),
        gr.Dropdown(choices=["gpt-3.5-turbo"], value="gpt-3.5-turbo"),
        gr.Slider(minimum=1, maximum=100, value=20, label="Max tokens", step=1),
        gr.Slider(minimum=0.0, maximum=1.0, value=0.5, label="Temperature"),
        gr.Dropdown(choices=["Hugo", "Adam", "Rachel"], value="Hugo"),
    ],
    [
        gr.Textbox(lines=2, label="Output")
    ],
    title="Maiself",
    description="Chat with yourself using OpenAI Whisper, OpenAI GPT-3 and ElevenLabs Voices",
)

if __name__ == "__main__":
    interface.launch()
