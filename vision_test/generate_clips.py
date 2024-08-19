import ffmpeg
import json
from datetime import datetime
from pathlib import Path
from .decorators import record_performance


def get_timestamp():
    return int(datetime.now().timestamp())


def merge_videos(input_videos, output_video):
    # Create input streams for each video
    input_streams = [ffmpeg.input(video) for video in input_videos]

    # Concatenate the input streams
    concat_stream = ffmpeg.concat(*input_streams, v=1, a=1).node

    # Define the output stream
    output_stream = ffmpeg.output(concat_stream[0], concat_stream[1], output_video)

    # Run the ffmpeg command
    ffmpeg.run(output_stream)


@record_performance
def generate_clips(movements_data_file="output/intensive-movements.json", input_video="data/sample-tennis-1.mp4",
                   base_output_dir="output"):
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
            ffmpeg.input(str(Path(input_video)), ss=start_time_sec, t=activity_duration).output(
                str(output_file_path)).run()
            count += 1
        except ffmpeg.Error as e:
            print(f"Error generating clip {str(output_file_path)}: {e}")
            err_count += 1

    print(f'Generated {count} clips. Now merging them...')
    merged_output_path = output_dir_path / f"clip_merged_from_{count}.mp4"
    merge_videos(clip_paths, str(merged_output_path))

    result_msg = f"{movements_data_file} + {input_video}: {count} clips generated with {err_count} errors."
    with open(str(output_dir_path / f"result.txt"), 'w') as f:
        f.write(result_msg)
    print(result_msg)
