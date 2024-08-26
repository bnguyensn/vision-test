import argparse
import sys
from datetime import datetime
from pathlib import Path

from speech_diarization.analyze_audio import analyze_audio
from speech_diarization.generate_clips import process_audio_clips


def get_timestamp():
    return int(datetime.now().timestamp())


def parse_args():
    parser = argparse.ArgumentParser(description='Analyze audio using speech diarization.')
    parser.add_argument('--input_audio', type=str, help='Path to the input audio file')
    parser.add_argument('--input_video', type=str, help='Path to the input video')
    parser.add_argument('--input_json', type=str, help='Path to the input JSON data file')
    parser.add_argument('--output_dir', type=str, help='Path to the output directory', required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    input_audio = args.input_audio
    input_video = args.input_video
    input_json = args.input_json
    output_dir = args.output_dir

    if input_audio:
        if not Path(input_audio).exists():
            print(f"Error: The input file '{input_audio}' does not exist.")
            sys.exit(1)

        if not input_audio.lower().endswith('.wav'):
            print("Error: The input file must be a WAV file.")
            sys.exit(1)

        try:
            analyze_audio(input_audio, f"{output_dir}/{get_timestamp()}")
        except Exception as e:
            print(f"An error occurred while analyzing the audio: {str(e)}")
            sys.exit(1)
    elif input_video and input_json:
        try:
            process_audio_clips(input_video, input_json, output_dir)
        except Exception as e:
            print(f"An error occurred while generating audio clips: {str(e)}")
            sys.exit(1)
    else:
        print("Error: You must provide either input_audio OR input_video and input_json")
        sys.exit(1)


if __name__ == "__main__":
    main()
