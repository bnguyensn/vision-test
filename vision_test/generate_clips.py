import ffmpeg
import json
from pathlib import Path


def temp(prefix="aaa", input_file="", output_dir="output"):
    print("Generating clips from output/intensive-movements.json...")

    with open('output/intensive-movements.json', 'r') as f:
        data = json.load(f)

    for i, movement in enumerate(data):
        clip_id = str(i + 1)
        print(f"Generating clip {clip_id}...")
        Path(output_dir).mkdir(exist_ok=True)
        output_path = Path(output_dir) / f"{clip_id}_{prefix}.mp4"

        input_video = str(Path(str(input_file)))
        output_video = str(output_path)
        start_time_sec = movement["from"]
        end_time_sec = movement["to"]
        duration = end_time_sec - start_time_sec

        try:
            ffmpeg.input(input_video, ss=start_time_sec, t=duration).output(output_video).run()
        except ffmpeg.Error as e:
            print(f"Error generating clip {output_video}: {e}")

    print("Done!")
