import cv2 as cv
import argparse

DEFAULT_MOVEMENT_THRESHOLD = 1000


def get_movements():
    # Set up parser

    parser = argparse.ArgumentParser(description='This program shows how to use background subtraction methods provided by \
     OpenCV. You can process both videos and images.')
    parser.add_argument('--input', type=str,
                        help='Path to a video or a sequence of image.',
                        default='data/video.mp4')
    parser.add_argument('--algo', type=str,
                        help='Background subtraction method (KNN, MOG2).',
                        default='MOG2')
    args = parser.parse_args()

    # Setup alogrithm, either KNN or MOG2

    backSub = cv.createBackgroundSubtractorMOG2(
        varThreshold=DEFAULT_MOVEMENT_THRESHOLD)
    # if args.algo == 'MOG2':
    #     backSub = cv.createBackgroundSubtractorMOG2(varThreshold=100)
    # else:
    #     backSub = cv.createBackgroundSubtractorKNN(varThreshold=100)

    # Create a video capture object

    capture = cv.VideoCapture(cv.samples.findFileOrKeep(args.input))
    if not capture.isOpened():
        print('Unable to open: ' + args.input)
        exit(0)

    # Store the timestamps when intensive movements happen
    intensive_movements = []

    while True:
        # capture.read() grabs, decodes, and returns the next video frame
        ret, frame = capture.read()
        if frame is None:
            break

        # Apply the background subtraction algorithm to the frame
        fgMask = backSub.apply(frame)

        # Count white pixels
        white_pixels = cv.countNonZero(fgMask)

        # Show the white pixels count
        cv.putText(frame, str(white_pixels), (15, 35),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

        if white_pixels > 2000:
            current_frame = int(capture.get(cv.CAP_PROP_POS_FRAMES))
            current_time = (current_frame * 1000)
            intensive_movements.append(
                {"from": current_time, "to": current_time + 1000})

        # Draw a rectangle on the frame, starting at (10, 2) and ending at
        # (100, 20)
        cv.rectangle(frame, (10, 2), (100, 20), (255, 0, 0), -1)

        # Add the current frame number in the top left corner
        cv.putText(frame, str(capture.get(cv.CAP_PROP_POS_FRAMES)), (15, 15),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

        # Show the frame and the fg mask
        cv.imshow('Frame', frame)
        cv.imshow('FG Mask', fgMask)

        # Wait for 30 milliseconds, if the user presses 'q' or 'ESC', exit
        keyboard = cv.waitKey(30)
        if keyboard == 'q' or keyboard == 27:
            break

    print(intensive_movements)
