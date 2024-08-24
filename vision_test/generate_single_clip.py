import json
import os
from pathlib import Path

import ffmpeg

ANALYZE_DURATION = '10M'  # Increase analyzeduration (10 million microseconds = 10 seconds)
PROBE_SIZE = '50M'  # Increase probesize to 50 megabytes


def generate_single_clip(movements_data_file, input_video, output_dir):
    with open(movements_data_file, 'r') as f:
        data = json.load(f)

    # Parse data and calculate total time
    total_time_s = sum(d['to'] - d['from'] for d in data)
    print(f"Total time of all segments: {total_time_s}s")

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
    concat_file_path = Path(output_dir) / "concat_list.txt"
    with open(concat_file_path, 'w') as f:
        for temp_file in temp_files:
            f.write(f"file '{os.path.abspath(temp_file)}'\n")
    print(f"Created temporary file: {str(concat_file_path)}")

    try:
        # Use the concat demuxer to concatenate the segments
        output_video_path = Path(output_dir) / "clip_merged.mp4"
        (ffmpeg.input(
            str(concat_file_path),
            format='concat',
            safe=0)
         .output(str(output_video_path), c='copy').run())
    finally:
        # Clean up the temporary files
        os.remove(concat_file_path)
        for temp_file in temp_files:
            os.remove(temp_file)
        print(f"Removed temporary file: {str(concat_file_path)}")

    print(f"Finished generate_single_clip. Created: {str(output_video_path)}")
