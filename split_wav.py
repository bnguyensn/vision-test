import argparse
import os

import psutil

from wav_splitter.split_wav import split_wav_in_parallel


def main():
    parser = argparse.ArgumentParser(description="Split a WAV file into 10-minute segments.")
    parser.add_argument('input_file', type=str, help='Path to the input WAV file.')
    parser.add_argument('output_dir', type=str, help='Path to the output directory.')
    parser.add_argument('--num-cores', type=int, default=psutil.cpu_count() // 2,
                        help='Number of CPU cores to use for splitting. Defaults to half of the machine\'s cores.')

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    segment_duration = 10 * 60  # 10 minutes in seconds
    split_wav_in_parallel(args.input_file, args.output_dir, segment_duration, args.num_cores)


if __name__ == "__main__":
    main()
