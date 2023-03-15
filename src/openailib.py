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
    log.info(f"API call to {model} with prompt: \n\t{_prompt}")
    _response = openai.ChatCompletion.create(
        model=model,
        messages=prompt,
        temperature=temperature,
        n=1,
        max_tokens=max_tokens,
    )
    log.info(f"API reponse: \n\t{_response}")
    response: str = _response['choices'][0]['message']['content']
    return response


@timeit
def fake_conversation(speakers, dialogue, iam: str, request: str, **kwargs):
    if not dialogue:
        dialogue = []
        for speaker in speakers:
            if speaker.description:
                dialogue += [f"{speaker.name}: {speaker.description}."]
    dialogue += [f"{iam}: {request}."]
    system = f"You create funny conversation dialogues. This conversation is between {', '.join([speaker.name for speaker in speakers])}. Do not introduce new characters. Only return the script itself, every line must start with a character name."
    return top_response('\n'.join(dialogue), system=system, **kwargs)
