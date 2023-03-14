import argparse
import logging
import os
import time
from typing import List, Union

from elevenlabslib import ElevenLabsUser, ElevenLabsVoice

from utils import timeit

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

USER = ElevenLabsUser(os.environ["ELEVENLABS_API_KEY"])


def check_voice_exists(voice: Union[ElevenLabsVoice, str]) -> Union[ElevenLabsVoice, None]:
    log.info(f"Getting voice {voice}...")
    _available_voices = USER.get_voices_by_name(voice)
    if _available_voices:
        log.info(f"Voice {voice} already exists, found {_available_voices}.")
        return _available_voices[0]
    return None

@timeit
def get_make_voice(voice: Union[ElevenLabsVoice, str], audio_path: List[str] = None) -> ElevenLabsVoice:
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
    raise ValueError(f"Voice {voice} does not exist and cloning is not available.")


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract audio from YouTube videos using links from a CSV file.')
    parser.add_argument('data_dir', type=str, default='tube.output', help='Path to the data directory')
    args = parser.parse_args()
    
    for person in os.listdir(args.data_dir):
        person_dir = os.path.join(args.data_dir, person)
        for audio_file in os.listdir(person_dir):
            if audio_file.endswith(".wav"):
                audio_path = os.path.join(person_dir, audio_file)
                get_make_voice(person, audio_path)
            