import math
import multiprocessing

import ffmpeg


def split_wav(input_file, start_time, duration, output_file):
    """Splits the WAV file using ffmpeg for a given start time and duration."""
    try:
        (
            ffmpeg
            .input(input_file, ss=start_time, t=duration)
            .output(output_file)
            .run(overwrite_output=True)
        )
    except ffmpeg.Error as e:
        print(f"Error splitting {output_file}: {e}")


def get_wav_duration(input_file):
    """Get the total duration of the WAV file."""
    probe = ffmpeg.probe(input_file)
    duration = float(probe['format']['duration'])
    return duration


def split_wav_in_parallel(input_file, output_dir, segment_duration, num_cores):
    """Splits the WAV file into segments in parallel."""
    # Get the total duration of the WAV file
    total_duration = get_wav_duration(input_file)
    # Calculate the number of segments needed
    num_segments = math.ceil(total_duration / segment_duration)

    print(f"Splitting {input_file} (duration: {total_duration}s) into {num_segments} segments...")

    # Create arguments for each segment
    tasks = []
    for i in range(num_segments):
        start_time = i * segment_duration
        duration = min(segment_duration, total_duration - start_time)
        output_file = f'{output_dir}/segment_{i + 1}.wav'
        tasks.append((input_file, start_time, duration, output_file))

    # Use multiprocessing to split the WAV in parallel
    with multiprocessing.Pool(num_cores) as pool:
        pool.starmap(split_wav, tasks)

    print(f"Finished splitting {input_file} into {num_segments} segments.")
