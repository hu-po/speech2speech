'''
Extract audio from a YouTube video

Usage:
    tube.py <url> <person> [-s <start_time>] [-d <duration>]
'''

import subprocess
from pathlib import Path
import datetime
import argparse
import os
from pytube import YouTube

# Define argparse arguments
parser = argparse.ArgumentParser(description='Extract audio from a YouTube video')
parser.add_argument('url', type=str, help='the YouTube video URL')
parser.add_argument('person', type=str, help='the name of the person speaking')
parser.add_argument('-s', '--start-time', type=float, default=0, help='the start time in minutes for the extracted audio (default: 0)')
parser.add_argument('-d', '--duration', type=int, help='the duration in seconds for the extracted audio (default: 60)')


# 200 seconds seems to be max duration for single clips
def extract_audio(url: str, label: str, start_minute: float = 0, duration: int = 200):
    
    # Download the YouTube video
    youtube_object = YouTube(url)
    stream = youtube_object.streams.first()
    video_path = Path(stream.download(skip_existing=True))
    
    # Convert start time to seconds
    start_time_seconds = int(start_minute * 60)

    # Format the start time in HH:MM:SS.mmm format
    start_time_formatted = str(datetime.timedelta(seconds=start_time_seconds))
    start_time_formatted = start_time_formatted[:11] + start_time_formatted[12:]

    # Set the output path using the audio file name
    output_path = video_path.parent / f"{label}.wav"

    # Run ffmpeg to extract the audio
    cmd = ['ffmpeg', '-y', '-i', str(video_path), '-ss', start_time_formatted]
    if duration is not None:
        # Format the duration in HH:MM:SS.mmm format
        duration_formatted = str(datetime.timedelta(seconds=duration))
        duration_formatted = duration_formatted[:11] + duration_formatted[12:]
        cmd += ['-t', duration_formatted]
    cmd += ['-q:a', '0', '-map', 'a', str(output_path)]
    subprocess.run(cmd)

    # remove the extra .3gpp file that is created:
    for file in os.listdir(video_path.parent):
        if file.endswith(".3gpp"):
            os.remove(os.path.join(video_path.parent, file))

    return output_path

if __name__ == '__main__':

    # Parse the arguments
    args = parser.parse_args()

    # Extract the audio
    extract_audio(args.url, args.person, args.start_time, args.duration)