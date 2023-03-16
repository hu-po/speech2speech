import logging
import os

from .utils import timeit

import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@timeit
def speech_to_text(audio_path):
    log.info("Transcribing audio...")
    transcript = openai.Audio.transcribe("whisper-1", open(audio_path, "rb"))
    text = transcript["text"]
    log.info(f"Transcript: \n\t{text}")
    return text


@timeit
def top_response(prompt, system=None, model="gpt-3.5-turbo", max_tokens=20, temperature=0.8):
    _prompt = [
        {
            "role": "user",
            "content": prompt,
        },
    ]
    if system:
        _prompt = [
            {
                "role": "system",
                "content": system,
            },
        ] + _prompt
    log.info(f"API call to {model} with prompt: \n\n\t{_prompt}\n\n")
    _response = openai.ChatCompletion.create(
        model=model,
        messages=_prompt,
        temperature=temperature,
        n=1,
        max_tokens=max_tokens,
    )
    log.info(f"API reponse: \n\t{_response}")
    response: str = _response['choices'][0]['message']['content']
    return response
