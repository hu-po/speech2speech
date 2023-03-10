'''
    Create a batch of audio files from a CSV file containing YouTube links and metadata.

    Usage:
        tube.batch.py <csv_path> [-o <output_dir>]

'''

import shutil
import argparse
import csv
import os
from tube import extract_audio

def extract_audio_from_csv(csv_path, output_dir):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Copy over the csv to the root output directory
    shutil.copy(csv_path, output_dir)
    # Parse CSV file line by line
    with open(csv_path, newline='') as csvfile:
        # Keep track of the number of audio files for each person
        people = dict()
        for row in csv.DictReader(csvfile):
            url = row['url']
            person = row['person']
            start_minute = row['start_minute']
            
            # Track the number of audio files for each person
            if people.get(person) is None:
                people[person] = 0
                person_dir = os.path.join(output_dir, person)
                # Create the person's directory if it doesn't exist
                if not os.path.exists(person_dir):
                    os.makedirs(person_dir)
            else:
                people[person] += 1

            # Extract a longer segment of audio
            label = f"audio.{people[person]}"
            output_path = extract_audio(url, label, start_minute)

            # Move the audio file to the person's directory
            os.rename(output_path, os.path.join(person_dir, output_path.name))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract audio from YouTube videos using links from a CSV file.')
    parser.add_argument('csv_path', type=str, help='path to CSV file containing YouTube links and metadata')
    parser.add_argument('-o', '--output_dir', type=str, default='tube.output', help='path to output directory')
    args = parser.parse_args()
    extract_audio_from_csv(args.csv_path, args.output_dir)
