import argparse
import json
import os
import sys
from pathlib import Path
from decorators.all_decorators import record_performance

import ffmpeg

ANALYZE_DURATION = '10M'
PROBE_SIZE = '50M'


def parse_data(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    speaker_data = {}

    for entry in data:
        speaker = entry['speaker']
        start = entry['start']
        stop = entry['stop']

        if speaker not in speaker_data:
            speaker_data[speaker] = []

        speaker_data[speaker].append({"from": start, "to": stop})

    return speaker_data


def generate_clips(input_video, speaker_data, output_dir):
    for speaker, clips in speaker_data.items():
        print(f"Generating clips for speaker {speaker} (total entries: {len(clips)})")

        temp_files = []
        for i, clip in enumerate(clips):
            start = clip['from']
            stop = clip['to']
            duration = stop - start
            temp_file = f"temp_{i}.mp4"
            ffmpeg.input(input_video, ss=start, t=duration, analyzeduration=ANALYZE_DURATION,
                         probesize=PROBE_SIZE).output(temp_file).run()
            temp_files.append(temp_file)

        concat_file_path = Path(output_dir) / "concat_list.txt"
        with open(concat_file_path, 'w') as f:
            for temp_file in temp_files:
                f.write(f"file '{os.path.abspath(temp_file)}'\n")
        print(f"Created temporary file: {str(concat_file_path)}")

        try:
            output_video_path = Path(output_dir) / f"{speaker}.mp4"
            (ffmpeg.input(
                str(concat_file_path),
                format='concat',
                safe=0)
             .output(str(output_video_path), c='copy').run())
        except Exception as e:
            print(f"An error occurred while generating the output video for speaker {speaker}: {str(e)}")

        finally:
            # Clean up the temporary files
            os.remove(concat_file_path)
            for temp_file in temp_files:
                os.remove(temp_file)
            print(f"Removed temporary file: {str(concat_file_path)}")

            if 'output_video_path' in locals():
                print(f"✨ Done! Created: {str(output_video_path)}")
            else:
                print(f"Process finished for speaker {speaker}")


def parse_args():
    parser = argparse.ArgumentParser(description='Generate speaker clips from JSON file.')
    parser.add_argument('--input_video', type=str, help='Path to the input video', required=True)
    parser.add_argument('--input_json', type=str, help='Path to the input JSON data file', required=True)
    parser.add_argument('--output_dir', type=str, help='Path to the output directory', required=True)
    return parser.parse_args()


@record_performance
def process_audio_clips():
    args = parse_args()
    input_video = args.input_video
    input_json = args.input_json
    output_dir = args.output_dir

    for input_path, input_name in [(input_video, 'input_video'), (input_json, 'input_json'),
                                   (output_dir, 'output_dir')]:
        if not Path(input_path).exists():
            print(f"Error: The {input_name} '{input_path}' does not exist.")
            sys.exit(1)

    parsed_input_json = parse_data(input_json)
    generate_clips(input_video, parsed_input_json, output_dir)


if __name__ == "__main__":
    process_audio_clips()
