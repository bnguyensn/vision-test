import ffmpeg
import json
from datetime import datetime
from pathlib import Path


def get_timestamp():
    return int(datetime.now().timestamp())


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
    for i, movement in enumerate(data):
        clip_id = str(i + 1)
        print(f"Generating clip {clip_id}...")
        output_file_path = output_dir_path / f"clip_{clip_id}.mp4"

        start_time_sec = movement["from"]
        end_time_sec = movement["to"]
        activity_duration = end_time_sec - start_time_sec

        try:
            ffmpeg.input(str(Path(input_video)), ss=start_time_sec, t=activity_duration).output(
                str(output_file_path)).run()
            count += 1
        except ffmpeg.Error as e:
            print(f"Error generating clip {str(output_file_path)}: {e}")
            err_count += 1

    print(f"generate_clips() completed. {count} clips generated with {err_count} errors.")
