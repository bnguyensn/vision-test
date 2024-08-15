import cv2 as cv
import argparse
import ffmpeg
import json
from pathlib import Path

DEFAULT_MOG2_VAR_THRESHOLD = 1000
DEFAULT_MOG2_HISTORY = 500
DEFAULT_MOG2_SHADOWS = False

DEFAULT_WHITE_PIXEL_COUNT = 3000
DEFAULT_INPUT_FILE = Path('data/video_trimmed.mp4')
DEFAULT_OUTPUT_DIR = Path('output')
DEFAULT_MOVEMENT_TIME_ADDITION = 4
DEFAULT_POST_PROCESS_FRAME_TUNING_ADDITION = 3


def record_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"{func.__name__} took {duration:.2f} seconds to complete.")
        return result

    return wrapper


def merge_videos(input_videos, output_video):
    # Create input streams for each video
    input_streams = [ffmpeg.input(video) for video in input_videos]

    # Concatenate the input streams
    concat_stream = ffmpeg.concat(*input_streams, v=1, a=1).node

    # Define the output stream
    output_stream = ffmpeg.output(concat_stream[0], concat_stream[1], output_video)

    # Run the ffmpeg command
    ffmpeg.run(output_stream)


def extract_clip(input_video, output_clip, start_time, end_time):
    # Convert start_time and end_time from ms to s
    start_time_sec = start_time / 1000
    end_time_sec = end_time / 1000

    # Calculate clip duration
    duration = end_time_sec - start_time_sec

    # Extract the clip using ffmpeg-python
    ffmpeg.input(input_video, ss=start_time_sec, t=duration).output(
        output_clip).run()


def parse_args():
    parser = argparse.ArgumentParser(description='This program shows how to use background subtraction methods provided by \
         OpenCV. You can process both videos and images.')

    parser.add_argument('--input', type=Path,
                        help='Path to a video or a sequence of image.',
                        default=DEFAULT_INPUT_FILE)
    parser.add_argument('--algo', type=str,
                        help='Background subtraction method (KNN, MOG2).',
                        default='MOG2')
    parser.add_argument('--mvmt', type=int,
                        help='Movement threshold. Increase to reduce sensitivity, but might miss subtle movements.',
                        default=DEFAULT_MOG2_VAR_THRESHOLD)
    parser.add_argument('--history', type=int,
                        help='How many frames are used to update the background model. Increase to reduce false \
                             positives at the cost of missing fast movements.',
                        default=DEFAULT_MOG2_HISTORY)
    parser.add_argument('--shadows', type=bool,
                        help='If true, will try to detect shadows.',
                        default=DEFAULT_MOG2_SHADOWS)

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

    capture = cv.VideoCapture(cv.samples.findFileOrKeep(str(args.input)))
    if not capture.isOpened():
        print('Unable to open: ' + str(args.input))
        exit(0)

    # Video fps
    fps = capture.get(cv.CAP_PROP_FPS)
    total_frames = int(capture.get(cv.CAP_PROP_FRAME_COUNT))

    # Store the timestamps when intensive movements happen
    intensive_movements = []

    # Since we're adding some seconds to each start frame, we can't count
    # the same intensive movement twice.
    previous_intensive_movements_frame_end = 0

    print(f"Processing {total_frames:,} frames")

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
        cv.putText(frame, str(white_pixels), (15, 35),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

        # Store intensive movements
        if white_pixels > DEFAULT_WHITE_PIXEL_COUNT:
            current_frame = int(capture.get(cv.CAP_PROP_POS_FRAMES))
            current_time_ms = (current_frame * 1000)  # ms
            current_time_s = int(current_frame / fps)

            current_time = current_time_s
            if current_time > previous_intensive_movements_frame_end:
                to_time = current_time + DEFAULT_MOVEMENT_TIME_ADDITION
                intensive_movements.append(
                    {"from": current_time,
                     "to": to_time})
                previous_intensive_movements_frame_end = to_time

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

    print(f"Generating {len(intensive_movements)} clips...")

    with open('output/intensive-movements.json', 'w') as f:
        json.dump(intensive_movements, f, indent=4)

    for i, movement in enumerate(intensive_movements):
        print(f"Generating clip {i + 1}...")
        DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)
        output_path = DEFAULT_OUTPUT_DIR / f"clip_{i + 1}.mp4"
        extract_clip(str(DEFAULT_INPUT_FILE), str(output_path),
                     movement["from"] * 1000, movement["to"] * 1000)

    print("Done!")
