import logging
import os
import time

import gradio as gr
import openai
from elevenlabslib import ElevenLabsUser

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def text_to_speech(text: str, voice_name: str = "Hugo"):
    log.info(f"Generating audio using voice {voice_name}...")
    time_start = time.time()
    user = ElevenLabsUser(os.environ["ELEVENLABS_API_KEY"])
    voice = user.get_voices_by_name(voice_name)[0]
    voice.generate_and_play_audio(text, playInBackground=False)
    log.info(f"Audio duration: {time.time() - time_start:.2f} seconds")


def run(audio, context):
    request = speech_to_text(audio)
    response = request_to_response(request, context)
    text_to_speech(response)
    return response


def speech_to_text(audio_path):
    log.info("Transcribing audio...")
    time_start = time.time()
    transcript = openai.Audio.transcribe("whisper-1", open(audio_path, "rb"))
    text = transcript["text"]
    log.info(f"Transcription duration: {time.time() - time_start:.2f} seconds")
    log.info(f"Transcript: \n\t{text}")

    return text


def request_to_response(request, context, model="gpt-3.5-turbo"):
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
        temperature=0,
        n=1,
        max_tokens=20,
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
    ],
    [
        gr.Textbox(lines=2, label="Output")
    ],
    title="Maiself",
    description="Chat with yourself using OpenAI Whisper, OpenAI GPT-3 and ElevenLabs Voices",
)

if __name__ == "__main__":
    interface.launch()
