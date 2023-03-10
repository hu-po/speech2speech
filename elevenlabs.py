import logging
import os
import time

from elevenlabslib import ElevenLabsUser
import argparse

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def get_make_voice(voice: str, audio_path: str = None):
    log.info(f"Getting voice {voice}...")
    user = ElevenLabsUser(os.environ["ELEVENLABS_API_KEY"])
    _available_voices = user.get_voices_by_name(voice)
    if _available_voices:
        log.info(f"Voice {voice} already exists, found {_available_voices}.")
        return _available_voices[0]
    if user.get_voice_clone_available():
        # Create the new voice by uploading the sample as bytes
        assert audio_path is not None, "audio_path must be provided"
        log.info(f"Cloning voice {voice}...")
        newVoice = user.clone_voice_bytes(
            voice, {audio_path: open(audio_path, "rb").read()})
        return newVoice
    log.warning(f"Voice {voice} does not exist and cloning is not available.")


def text_to_speech(text: str, voice: str = "Hugo"):
    log.info(f"Generating audio using voice {voice}...")
    time_start = time.time()
    _voice = get_make_voice(voice)
    _voice.generate_and_play_audio(text, playInBackground=False)
    log.info(f"Audio duration: {time.time() - time_start:.2f} seconds")

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
            