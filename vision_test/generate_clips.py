import ffmpeg
import json
from datetime import datetime
from pathlib import Path
import os
from .decorators import record_performance

ANALYZE_DURATION = '10M'  # Increase analyzeduration (10 million microseconds = 10 seconds)
PROBE_SIZE = '50M'  # Increase probesize to 50 megabytes
PIXEL_FORMAT = 'yuv420p'  # Pixel format for the output video


def get_timestamp():
    return int(datetime.now().timestamp())


def generate_large_clip(data, input_video, output_dir_path):
    # Create input streams for each time period
    input_streams = []
    for d in data:
        start_time = d['from']
        duration = d['to'] - start_time
        input_streams.append(ffmpeg.input(input_video, ss=start_time, t=duration))

    # Concatenate the input streams
    concat_stream = ffmpeg.concat(*input_streams, v=1, a=1).node

    # Define the output stream
    output_stream = ffmpeg.output(concat_stream[0], concat_stream[1], output_dir_path / f"clip_merged.mp4")

    # Run the ffmpeg command
    ffmpeg.run(output_stream)


def generate_large_clip_2(data, input_video, output_dir_path):
    # Create temporary files for each time period
    temp_files = []
    for i, d in enumerate(data):
        start_time = d['from']
        duration = d['to'] - start_time
        temp_file = f"temp_{i}.mp4"
        ffmpeg.input(input_video, ss=start_time, t=duration, analyzeduration=ANALYZE_DURATION,
                     probesize=PROBE_SIZE).output(temp_file).run()
        temp_files.append(temp_file)

    # Create a temporary text file listing all the video segments
    concat_file_path = output_dir_path / "concat_list.txt"
    with open(concat_file_path, 'w') as f:
        for temp_file in temp_files:
            f.write(f"file '{os.path.abspath(temp_file)}'\n")

    # Use the concat demuxer to concatenate the segments
    (ffmpeg.input(
        concat_file_path,
        format='concat',
        safe=0)
     .output("clip_merged.mp4", c='copy').run())

    # Clean up the temporary files
    os.remove(concat_file_path)
    for temp_file in temp_files:
        os.remove(temp_file)


@record_performance
def generate_clips(movements_data_file="", input_video="", base_output_dir=""):
    """
    Generate clips from an input intensive-movements.json file.

    Args:
        movements_data_file (str): Path to the intensive-movements.json file relative to where the script is run.
        input_video (str): Path to the video used by intensive-movements.json.
        base_output_dir (str): The parent directory where the output clips will be saved under. A new directory (prefixed with a timestamp) will be created under this provided output directory path, and the videos will be put under this new directory.

    Returns:
        None: This function does not return any value.

    Example:
        generate_clips("output/intensive-movements.json", "output")
    """

    print(f"Generating clips from {movements_data_file} and {input_video}...")

    output_prefix = str(get_timestamp())
    output_dir_path = Path(base_output_dir) / f"{output_prefix}_clips"
    output_dir_path.mkdir(exist_ok=True)

    with open(movements_data_file, 'r') as f:
        data = json.load(f)

    count = 0
    err_count = 0
    clip_paths = []
    for i, movement in enumerate(data):
        start_time_sec = movement["from"]
        end_time_sec = movement["to"]
        activity_duration = end_time_sec - start_time_sec

        clip_id = str(i + 1)
        print(f"Generating clip {clip_id}...")
        output_file_path = output_dir_path / f"clip_{clip_id}_{str(start_time_sec)}-{str(end_time_sec)}.mp4"
        clip_paths.append(str(output_file_path))

        try:
            ffmpeg.input(input_video, ss=start_time_sec, t=activity_duration,
                         analyzeduration=ANALYZE_DURATION, probesize=PROBE_SIZE).output(
                str(output_file_path), pix_fmt=PIXEL_FORMAT).run()
            count += 1
        except ffmpeg.Error as e:
            print(f"Error generating clip {str(output_file_path)}: {e}")
            err_count += 1

    result_msg = f"{movements_data_file} + {input_video}: {count} clips generated with {err_count} errors."
    with open(str(output_dir_path / f"result.txt"), 'w') as f:
        f.write(result_msg)
    print(result_msg)

    print(f'Generated {count} clips. Now creating a merged video...')
    generate_large_clip_2(data, input_video, output_dir_path)
