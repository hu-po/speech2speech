import asyncio
import io
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Union, Tuple

import sounddevice as sd
import soundfile as sf
from elevenlabslib import ElevenLabsUser, ElevenLabsVoice

from .utils import timeit

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

USER = None

def set_elevenlabs_key(elevenlabs_api_key_textbox=None):
    global USER
    log.info(f"Setting ElevenLabs key.")
    if elevenlabs_api_key_textbox is not None:
        os.environ["ELEVENLABS_API_KEY"] = elevenlabs_api_key_textbox
    try:
        USER = ElevenLabsUser(os.environ["ELEVENLABS_API_KEY"])
    except KeyError as e:
        USER = None
        log.warning("ELEVENLABS_API_KEY not found in environment variables.")
        pass

set_elevenlabs_key()

@dataclass
class Speaker:
    name: str
    voice: ElevenLabsVoice
    color: str
    description: str = None


async def text_to_speechbytes_async(text, speaker, loop):
    with ThreadPoolExecutor() as executor:
        speech_bytes = await loop.run_in_executor(executor, text_to_speechbytes, text, speaker.voice)
    return speech_bytes


async def play_history(history: List[Tuple[Speaker, str]]):
    loop = asyncio.get_event_loop()

    # Create a list of tasks for all text_to_speechbytes function calls
    tasks = [text_to_speechbytes_async(
        text, speaker, loop) for speaker, text in history]

    # Run tasks concurrently, waiting for the first one to complete
    for speech_bytes in await asyncio.gather(*tasks):
        audioFile = io.BytesIO(speech_bytes)
        soundFile = sf.SoundFile(audioFile)
        sd.play(soundFile.read(), samplerate=soundFile.samplerate, blocking=True)


async def save_history(history: List[Tuple[Speaker, str]], audio_savepath: str):
    loop = asyncio.get_event_loop()

    # Create a list of tasks for all text_to_speechbytes function calls
    tasks = [text_to_speechbytes_async(
        text, speaker, loop) for speaker, text in history]

    # Run tasks concurrently, waiting for the first one to complete
    all_speech_bytes = await asyncio.gather(*tasks)

    # Combine all audio bytes into a single audio file
    concatenated_audio = io.BytesIO(b''.join(all_speech_bytes))

    # Save the combined audio file to disk
    with sf.SoundFile(concatenated_audio, mode='r') as soundFile:
        with sf.SoundFile(
            audio_savepath, mode='w',
            samplerate=soundFile.samplerate,
            channels=soundFile.channels,
        ) as outputFile:
            outputFile.write(soundFile.read())


def check_voice_exists(voice: Union[ElevenLabsVoice, str]) -> Union[ElevenLabsVoice, None]:
    if USER is None:
        log.warning(
            "No ElevenLabsUser found, have you set the ELEVENLABS_API_KEY environment variable?")
        return None
    log.info(f"Getting voice {voice}...")
    _available_voices = USER.get_voices_by_name(voice)
    if _available_voices:
        log.info(f"Voice {voice} already exists, found {_available_voices}.")
        return _available_voices[0]
    return None


@timeit
def get_make_voice(voice: Union[ElevenLabsVoice, str], audio_path: List[str] = None) -> ElevenLabsVoice:
    if USER is None:
        log.warning(
            "No ElevenLabsUser found, have you set the ELEVENLABS_API_KEY environment variable?")
        return None
    _voice = check_voice_exists(voice)
    if _voice is not None:
        return _voice
    else:
        if USER.get_voice_clone_available():
            assert audio_path is not None, "audio_path must be provided"
            assert isinstance(audio_path, list), "audio_path must be a list"
            log.info(f"Cloning voice {voice}...")
            _audio_source_dict = {
                # Audio path is a PosixPath
                _.name: open(_, "rb").read() for _ in audio_path
            }
            newVoice = USER.clone_voice_bytes(voice, _audio_source_dict)
            return newVoice
    raise ValueError(
        f"Voice {voice} does not exist and cloning is not available.")


@timeit
def text_to_speech(text: str, voice: ElevenLabsVoice):
    log.info(f"Generating audio using voice {voice}...")
    time_start = time.time()
    voice.generate_and_play_audio(text, playInBackground=False)
    duration = time.time() - time_start
    return duration


@timeit
def text_to_speechbytes(text: str, voice: ElevenLabsVoice):
    log.info(f"Generating audio for voice {voice} text {text}...")
    audio_bytes = voice.generate_audio_bytes(text)
    return audio_bytes
