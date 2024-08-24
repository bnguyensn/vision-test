import argparse
import json
from datetime import datetime
from pathlib import Path

import cv2 as cv
import ffmpeg

from .analyze_movements import analyze_movements
from .decorators import record_performance
from .generate_single_clip import generate_single_clip

DEFAULT_MOG2_VAR_THRESHOLD = 1000
DEFAULT_MOG2_HISTORY = 500
DEFAULT_MOG2_SHADOWS = False

DEFAULT_WHITE_PIXEL_COUNT = 3000
DEFAULT_OUTPUT_DIR = Path('output')
DEFAULT_MOVEMENT_TIME_ADDITION = 4
DEFAULT_POST_PROCESS_FRAME_TUNING_ADDITION = 3


def get_timestamp():
    return int(datetime.now().timestamp())


def extract_clip(input_video, output_clip, start_time, end_time):
    # Convert start_time and end_time from ms to s
    start_time_sec = start_time / 1000
    end_time_sec = end_time / 1000

    # Calculate clip duration
    duration = end_time_sec - start_time_sec

    # Extract the clip using ffmpeg-python
    try:
        ffmpeg.input(input_video, ss=start_time_sec, t=duration).output(output_clip).run()
    except ffmpeg.Error as e:
        print(f"Error generating clip {output_clip}: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description='This program shows how to use background subtraction methods provided by \
         OpenCV. You can process both videos and images.')

    parser.add_argument('--input',
                        type=str,
                        help='Path to a video.',
                        required=True)
    parser.add_argument('--clip_limit_s',
                        type=int,
                        help='Maximum length of each generated clip in seconds.',
                        default=None)
    parser.add_argument('--algo',
                        type=str,
                        help='Background subtraction method (KNN, MOG2).',
                        default='MOG2')
    parser.add_argument('--mvmt',
                        type=int,
                        help='Movement threshold. Increase to reduce sensitivity, but might miss subtle movements.',
                        default=DEFAULT_MOG2_VAR_THRESHOLD)
    parser.add_argument('--history',
                        type=int,
                        help='How many frames are used to update the background model. Increase to reduce false \
                             positives at the cost of missing fast movements.',
                        default=DEFAULT_MOG2_HISTORY)
    parser.add_argument('--shadows',
                        action='store_true',
                        help='If true, will try to detect shadows.',
                        default=DEFAULT_MOG2_SHADOWS)
    parser.add_argument('--generate-clips',
                        action='store_true',
                        help='If true, will automatically generate video clips.',
                        default=False)
    parser.add_argument('--movementsjson',
                        type=str,
                        help='Path to an intensive movements JSON file. If provided, will always generate clips.',
                        default="")

    return parser.parse_args()


@record_performance
def get_movements():
    args = parse_args()

    if args.movementsjson:
        print(f"Generating clips from {args.movementsjson} and {args.input}...")
        generate_single_clip(args.movementsjson, args.input, "output/merged_clips")
        return

    # Setup algorithm, either KNN or MOG2
    back_sub = cv.createBackgroundSubtractorMOG2(
        history=args.history,
        varThreshold=args.mvmt,
        detectShadows=args.shadows)
    # if args.algo == 'MOG2':
    #     backSub = cv.createBackgroundSubtractorMOG2(varThreshold=100)
    # else:
    #     backSub = cv.createBackgroundSubtractorKNN(varThreshold=100)

    # Create a video capture object
    capture = cv.VideoCapture(cv.samples.findFileOrKeep(args.input))
    if not capture.isOpened():
        print(f'Unable to open: {args.input}')
        exit(0)

    # Analyze movements
    intensive_movements = analyze_movements(capture, back_sub, white_pixel_threshold=DEFAULT_WHITE_PIXEL_COUNT,
                                            movement_time_addition=DEFAULT_MOVEMENT_TIME_ADDITION,
                                            post_process_frame_tuning_addition=DEFAULT_POST_PROCESS_FRAME_TUNING_ADDITION)

    # Store movements data
    timestamp = str(get_timestamp())
    intensive_movements_json = f'output/intensive-movements-{timestamp}-{str(args.mvmt)}mvmt-{str(args.history)}history.json'
    with open(intensive_movements_json, 'w') as f:
        json.dump(intensive_movements, f, indent=4)
    print(f'Created {intensive_movements_json}')

    # Create video clip (if requested)
    if args.generate_clips:
        # generate_clips(intensive_movements_json, args.input, "output")
        generate_single_clip(intensive_movements_json, args.input, "output/merged_clips")

    # for i, movement in enumerate(intensive_movements):
    #     print(f"Generating clip {i + 1}...")
    #     DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)
    #     output_path = DEFAULT_OUTPUT_DIR / f"clip_{i + 1}.mp4"
    #     extract_clip(str(args.input), str(output_path),
    #                  movement["from"] * 1000, movement["to"] * 1000)

    print("✨ Done!")
