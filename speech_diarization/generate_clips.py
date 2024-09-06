import json
import os
from pathlib import Path

import ffmpeg

from decorators.all_decorators import record_performance

ANALYZE_DURATION = '10M'
PROBE_SIZE = '50M'


def convert_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return hours, minutes, remaining_seconds


def parse_data(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    speaker_data = {}

    for entry in data:
        speaker = entry['speaker']
        start = entry['start']
        stop = entry['stop']
        duration = stop - start

        if duration <= 0.3:
            continue
        if start > 600:
            break

        if speaker not in speaker_data:
            speaker_data[speaker] = []
        speaker_data[speaker].append({"from": start, "to": stop})

    return speaker_data


def generate_clips(input_video, speaker_data, output_dir):
    if os.path.isfile(input_video):
        print(f"Input is a file: {input_video}")
    elif input_video.is_dir():
        print(f"{input_video} is a directory of files")
    else:
        print(f"Input is neither a file nor a directory: {input_video}")

    for speaker, clips in speaker_data.items():
        total_entries = len(clips)
        total_duration_s = sum([clip['to'] - clip['from'] for clip in clips])
        hours, minutes, seconds = convert_seconds(total_duration_s)
        print(
            f"Generating clips for speaker {speaker} (total entries: {total_entries}, total duration: {hours}h {minutes}m {seconds}s)")

        temp_files = []
        for i, clip in enumerate(clips):
            start = clip['from']
            stop = clip['to']
            duration = stop - start
            temp_file_path = Path(output_dir) / f"temp_{i}.mp4"
            ffmpeg.input(input_video, ss=start, t=duration, analyzeduration=ANALYZE_DURATION,
                         probesize=PROBE_SIZE).output(str(temp_file_path)).run()
            temp_files.append(temp_file_path)
        print(f"Going to generate {len(temp_files)}x temp files")

        concat_file_path = Path(output_dir) / "concat_list.txt"
        with open(concat_file_path, 'w') as f:
            for temp_file_path in temp_files:
                f.write(f"file '{os.path.abspath(temp_file_path)}'\n")
            print(f"Created temporary file: {str(concat_file_path)}")

        try:
            output_video_path = Path(output_dir) / f"{speaker}.mp4"
            (ffmpeg.input(
                str(concat_file_path),
                format='concat',
                safe=0)
             .output(str(output_video_path), c='copy').run())
        except Exception as e:
            print(f"An error occurred while generating the output video for speaker {speaker}: {str(e)}")

        finally:
            # Clean up the temporary files
            os.remove(concat_file_path)
            for temp_file_path in temp_files:
                os.remove(temp_file_path)
            print(f"Removed temporary file: {str(concat_file_path)}")

            if 'output_video_path' in locals():
                print(f"✨ Done! Created: {str(output_video_path)}")
            else:
                print(f"Process finished for speaker {speaker}")


@record_performance
def process_audio_clips(input_video, input_json, output_dir):
    parsed_input_json = parse_data(input_json)
    generate_clips(input_video, parsed_input_json, output_dir)
