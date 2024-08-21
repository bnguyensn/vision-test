import ffmpeg
import os


def generate_concat_file(video_files, concat_file_path):
    with open(concat_file_path, 'w') as f:
        for video in video_files:
            f.write(f"file '{os.path.abspath(video)}'\n")


def merge_videos_demuxer(input_videos, output_video):
    # Create a temporary text file that lists all the video clips
    concat_file_path = "concat_list.txt"
    generate_concat_file(input_videos, concat_file_path)

    # Run ffmpeg using the concat demuxer
    ffmpeg.input(concat_file_path, format='concat', safe=0).output(output_video, c='copy').run()

    # Clean up the temporary file
    os.remove(concat_file_path)

    print(f"Merged video saved as {output_video}")
