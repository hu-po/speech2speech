import logging
import os
import time
from typing import List

from utils import timeit

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
def top_response(prompt, model="gpt-3.5-turbo", max_tokens=20, temperature=0.8):
    log.info(f"GPT-3 Starting")
    _response = openai.ChatCompletion.create(
        model=model,
        messages=prompt,
        temperature=temperature,
        n=1,
        max_tokens=max_tokens,
    )
    response: str = _response['choices'][0]['message']['content']
    log.info(f" Response: \n\t{response}")
    return response


@timeit
def respond_with_system_context(request, context, **kwargs):
    prompt = [
        {
            "role": "system",
            "content": context,
        },
        {
            "role": "user",
            "content": request,
        },
    ],
    return top_response(prompt, **kwargs)


@timeit
def fake_conversation(speakers, dialogue, iam: str, request: str, **kwargs):
    names_as_sentence = ', '.join([speaker.name for speaker in speakers])
    if not dialogue:
        dialogue = []
        for speaker in speakers:
            if speaker.description:
                dialogue += [f"{speaker.name}: {speaker.description}."]
    dialogue += [f"{iam}: {request}."]
    prompt = [
        {
            "role": "system",
            "content": f"You create funny conversation dialogues. This conversation is between {names_as_sentence}. Do not introduce new characters. Only return the script itself, every line must start with a character name.",
        },
        {
            "role": "user",
            "content": '\n'.join(dialogue),
        },
    ]
    return top_response(prompt, **kwargs)
