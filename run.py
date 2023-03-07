import logging
import os
import time
from datetime import datetime

import gradio as gr
import openai
import sounddevice as sd
from elevenlabslib import ElevenLabsUser

from scipy.io.wavfile import write

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def text_to_speech(text: str, voice_name: str = "Hugo"):

    user = ElevenLabsUser(os.environ["ELEVENLABS_API_KEY"])
    voice = user.get_voices_by_name(voice_name)[0]
    voice.generate_and_play_audio(text, playInBackground=False)


def run(servo_1, servo_2):
    return f"Servo 1: {servo_1}\nServo 2: {servo_2}"


def speech_to_text(
    # Sampling frequency
    fs=4999,
    channels=1,
    # Higher quality audio
    # fs=44100,
    # channels=2,
    # Max recording duration
    max_record_sec=12,
    # Recording file buffer
    record_buffer_path="/tmp/calgpt_vocal_buffer.wav",
):
    # Record audio
    log.info(f"\n Recording Starting")
    time_start_recording = time.time()
    myrecording = sd.rec(int(max_record_sec * fs),
                         samplerate=fs, channels=channels)
    while time.time() - time_start_recording < max_record_sec:
        log.info(
            f"Recording: {time.time() - time_start_recording:.2f} seconds\r")
        # if input("\t\t Stop recording? (y/n) ") == "y":
        #     sd.stop()
        #     break
    log.debug(
        f"\n Recording Stopped, duration: {time.time() - time_start_recording:.2f} seconds")

    # Save as WAV file
    # TODO: Can this be avoided?
    time_start_filewrite = time.time()
    write(record_buffer_path, fs, myrecording)
    myrecording = open(record_buffer_path, "rb")
    log.debug(
        f"\n File write duration: {time.time() - time_start_filewrite:.2f} seconds")

    # Transcribe audio with OpenAI Whisper
    time_start_transcribe = time.time()
    transcript = openai.Audio.transcribe("whisper-1", myrecording)
    text = transcript["text"]
    log.debug(
        f"\n Transcription duration: {time.time() - time_start_transcribe:.2f} seconds")
    log.info(f"\n Transcript: \n\t{text}")

    return text


def text_to_calendar(
        # Text to convert to calendar
        text,
        # Path to .ics file
        calendar_ics_filepath="test.ics",
        # Which GPT model to use
        model="gpt-3.5-turbo"
):

    # API Request for In-Context Learning
    EXAMPLES = [
        (
            "I want to go to the dentist on March 8th, 2023 from 9am to 10:30am",
            "Dentist,datetime(2023,3,8,9,0,0),datetime(2023,3,8,10,30,0)"
        ),
        (
            "Today is January 1st, 2022. I will meditate for 15 minutes the next two days in the morning.",
            "Meditate.datetime(2022,1,2,8,0,0).datetime(2022,1,2,8,15,0)|Meditate.datetime(2022,1,3,8,0,0).datetime(2022,1,3,8,15,0)"
        ),
        (
            "Today is March 6th, 2023. I want to workout on Tuesday from 2pm to 4pm. I also want to workout on Thursday from noon to 2pm.",
            "Workout.datetime(2023,3,7,14,0,0).datetime(2023,3,7,16,0,0)|Workout.datetime(2023,3,9,12,0,0).datetime(2023,3,9,14,0,0)"
        ),

    ]
    context = []
    for prompt, answer in EXAMPLES:
        context += [{"role": "user", "content": prompt},
                    {"role": "assistant", "content": answer}]

    # API Request for In-Context Learning
    openai.api_key = os.getenv("OPENAI_API_KEY")
    time_start_gptapi = time.time()
    log.info(f"\n GPT API Request Starting")
    _response = openai.ChatCompletion.create(
        model=model,
        messages=context + [
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0,
        n=1,
        max_tokens=200,
    )
    response: str = _response['choices'][0]['message']['content']
    log.debug(
        f"\n GPT API Request duration: {time.time() - time_start_gptapi:.2f} seconds")
    log.info(f"\n Response: \n\t{response}")


# Create interface
interface = gr.Interface(
    run,
    [
        gr.Slider(minimum=0.0, maximum=1.0, value=0.5, label="Servo 1"),
        gr.Slider(minimum=0.0, maximum=1.0, value=0.5, label="Servo 2"),
    ],
    [
        gr.Textbox(lines=2, label="Output")
    ],
    title="Plai",
    description="Control the servos",
)

if __name__ == "__main__":
    interface.launch()
