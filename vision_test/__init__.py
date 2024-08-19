from datetime import datetime
import cv2 as cv
import argparse
import ffmpeg
import json
from pathlib import Path
from .generate_clips import generate_clips
from .decorators import record_performance

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
                        help='Path to a video or a sequence of image.',
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

    return parser.parse_args()


@record_performance
def get_movements():
    args = parse_args()

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

    # Video fps
    fps = capture.get(cv.CAP_PROP_FPS)
    total_frames = int(capture.get(cv.CAP_PROP_FRAME_COUNT))

    # Store the timestamps when intensive movements happen
    intensive_movements = []

    # Since we're adding some seconds to each start frame, we can't count
    # the same intensive movement twice.
    previous_intensive_movements_frame_end = 0

    print(f'Processing {total_frames:,} frames')

    frame_count = 0
    while True:
        # capture.read() grabs, decodes, and returns the next video frame
        ret, frame = capture.read()
        if frame is None:
            break

        # Apply the background subtraction algorithm to the frame
        fg_mask = back_sub.apply(frame)

        # Count white pixels
        white_pixels = cv.countNonZero(fg_mask)

        # Show the white pixels count
        # cv.putText(frame, str(white_pixels), (15, 35),
        #            cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

        # Store intensive movements
        if white_pixels > DEFAULT_WHITE_PIXEL_COUNT:
            current_frame = int(capture.get(cv.CAP_PROP_POS_FRAMES))
            current_time_ms = (current_frame * 1000)  # ms
            current_time_s = int(current_frame / fps)

            current_time = current_time_s

            if not intensive_movements or current_time > intensive_movements[-1]["to"] + DEFAULT_MOVEMENT_TIME_ADDITION:
                intensive_movements.append({"from": current_time, "to": current_time})
            else:
                intensive_movements[-1]["to"] = current_time

            # if current_time > previous_intensive_movements_frame_end:
            #     to_time = current_time + DEFAULT_MOVEMENT_TIME_ADDITION
            #     intensive_movements.append(
            #         {"from": current_time,
            #          "to": to_time})
            #     previous_intensive_movements_frame_end = to_time

        # Log progress
        frame_count += 1
        if frame_count % (total_frames // 10) == 0:
            print(f"Processing: {frame_count / total_frames * 100:.2f}% complete")

        # Uncomment the below to show the video.

        # Draw a rectangle on the frame, starting at (10, 2) and ending at
        # (100, 20)
        # cv.rectangle(frame, (10, 2), (100, 20), (255, 0, 0), -1)

        # Add the current frame number in the top left corner
        # cv.putText(frame, str(capture.get(cv.CAP_PROP_POS_FRAMES)), (15, 15),
        #            cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

        # Show the frame and the fg mask
        # cv.imshow('Frame', frame)
        # cv.imshow('FG Mask', fg_mask)

        # Wait for 30 milliseconds, if the user presses 'q' or 'ESC', exit
        # keyboard = cv.waitKey(30)
        # if keyboard == 'q' or keyboard == 27:
        #     break

    # Post-processing
    for movement in intensive_movements:
        movement["to"] += DEFAULT_POST_PROCESS_FRAME_TUNING_ADDITION
    i = 0
    while i < len(intensive_movements) - 1:
        if intensive_movements[i]["to"] >= intensive_movements[i + 1]["from"]:
            intensive_movements[i]["to"] = max(intensive_movements[i]["to"], intensive_movements[i + 1]["to"])
            del intensive_movements[i + 1]
        else:
            i += 1

    timestamp = str(get_timestamp())
    intensive_movements_json_path = f'output/intensive-movements-{str(args.mvmt)}mvmt-{str(args.history)}history-{timestamp}.json'
    print(
        f'Finished processing. Total of {len(intensive_movements)} found. Writing intensive-movements.json to {intensive_movements_json_path}')

    with open(intensive_movements_json_path, 'w') as f:
        json.dump(intensive_movements, f, indent=4)

    print(f'Created {intensive_movements_json_path}')

    if args.generate_clips:
        generate_clips(intensive_movements_json_path, args.input, "output")

    # for i, movement in enumerate(intensive_movements):
    #     print(f"Generating clip {i + 1}...")
    #     DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)
    #     output_path = DEFAULT_OUTPUT_DIR / f"clip_{i + 1}.mp4"
    #     extract_clip(str(args.input), str(output_path),
    #                  movement["from"] * 1000, movement["to"] * 1000)

    print("Done!")
