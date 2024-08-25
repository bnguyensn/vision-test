import argparse
import sys
from datetime import datetime
from pathlib import Path

from speech_diatrization.analyze_audio import analyze_audio


def get_timestamp():
    return int(datetime.now().timestamp())


def parse_args():
    parser = argparse.ArgumentParser(description='Analyze audio using speech diarization.')
    parser.add_argument('--input', type=str, help='Path to the input file', required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    input_file = args.input

    if not Path(input_file).exists():
        print(f"Error: The input file '{input_file}' does not exist.")
        sys.exit(1)

    if not input_file.lower().endswith('.wav'):
        print("Error: The input file must be a WAV file.")
        sys.exit(1)

    try:
        analyze_audio(input_file, f"output/analyze_audio/{get_timestamp()}")
    except Exception as e:
        print(f"An error occurred while analyzing the audio: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
