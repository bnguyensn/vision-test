import ffmpeg
import os

ANALYZE_DURATION = '10M'  # Increase analyzeduration (10 million microseconds = 10 seconds)
PROBE_SIZE = '50M'  # Increase probesize to 50 megabytes


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
