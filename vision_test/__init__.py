import cv2 as cv
import argparse
import ffmpeg
import json

DEFAULT_MOVEMENT_THRESHOLD = 1000
DEFAULT_WHITE_PIXEL_COUNT = 3000
DEFAULT_INPUT_FILE = 'data/video_trimmed.mp4'
DEFAULT_MOVEMENT_TIME_ADDITION = 4


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

    parser.add_argument('--input', type=str,
                        help='Path to a video or a sequence of image.',
                        default=DEFAULT_INPUT_FILE)
    parser.add_argument('--algo', type=str,
                        help='Background subtraction method (KNN, MOG2).',
                        default='MOG2')
    parser.add_argument('--mvmt', type=int,
                        help='Movement threshold.',
                        default=DEFAULT_MOVEMENT_THRESHOLD)

    return parser.parse_args()


def get_movements():
    args = parse_args()

    # Setup algorithm, either KNN or MOG2

    back_sub = cv.createBackgroundSubtractorMOG2(
        varThreshold=args.mvmt)
    # if args.algo == 'MOG2':
    #     backSub = cv.createBackgroundSubtractorMOG2(varThreshold=100)
    # else:
    #     backSub = cv.createBackgroundSubtractorKNN(varThreshold=100)

    # Create a video capture object

    capture = cv.VideoCapture(cv.samples.findFileOrKeep(args.input))
    if not capture.isOpened():
        print('Unable to open: ' + args.input)
        exit(0)

    # Video fps
    fps = capture.get(cv.CAP_PROP_FPS)

    # Store the timestamps when intensive movements happen
    intensive_movements = []

    # Since we're adding some seconds to each start frame, we can't count
    # the same intensive movement twice.
    previous_intensive_movements_frame_end = 0

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

        # Draw a rectangle on the frame, starting at (10, 2) and ending at
        # (100, 20)
        cv.rectangle(frame, (10, 2), (100, 20), (255, 0, 0), -1)

        # Add the current frame number in the top left corner
        cv.putText(frame, str(capture.get(cv.CAP_PROP_POS_FRAMES)), (15, 15),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

        # Show the frame and the fg mask
        cv.imshow('Frame', frame)
        cv.imshow('FG Mask', fg_mask)

        # Wait for 30 milliseconds, if the user presses 'q' or 'ESC', exit
        keyboard = cv.waitKey(30)
        if keyboard == 'q' or keyboard == 27:
            break

    print(f"Generating {len(intensive_movements)} clips...")

    with open('output/intensive-movements.json', 'w') as f:
        json.dump(intensive_movements, f, indent=4)

    for i, movement in enumerate(intensive_movements):
        print(f"Generating clip {i + 1}...")
        extract_clip(DEFAULT_INPUT_FILE, f"output/clip_{i + 1}.mp4",
                     movement["from"] * 1000, movement["to"] * 1000)

    print("Done!")
