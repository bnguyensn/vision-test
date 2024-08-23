import cv2 as cv


def analyze_movements(capture, back_sub, *, white_pixel_threshold, movement_time_addition,
                      post_process_frame_tuning_addition):
    """
    Return an array containing the start and end times of intensive movements in the video.
    """

    # Store the timestamps when intensive movements happen
    intensive_movements = []

    # Video fps
    fps = capture.get(cv.CAP_PROP_FPS)
    total_frames = int(capture.get(cv.CAP_PROP_FRAME_COUNT))
    print(f'Video FPS: {fps}')
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
        if white_pixels > white_pixel_threshold:
            current_frame = int(capture.get(cv.CAP_PROP_POS_FRAMES))
            current_time_ms = (current_frame * 1000)  # ms
            current_time_s = int(current_frame / fps)

            current_time = current_time_s

            if not intensive_movements or current_time > intensive_movements[-1]["to"] + movement_time_addition:
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

    # Post-processing
    for movement in intensive_movements:
        movement["to"] += post_process_frame_tuning_addition
    i = 0
    while i < len(intensive_movements) - 1:
        if intensive_movements[i]["to"] >= intensive_movements[i + 1]["from"]:
            intensive_movements[i]["to"] = max(intensive_movements[i]["to"], intensive_movements[i + 1]["to"])
            del intensive_movements[i + 1]
        else:
            i += 1

    # Sum up all the durations in intensive_movements
    total_duration = 0
    for movement in intensive_movements:
        total_duration += movement["to"] - movement["from"]

    print(f'Finished analyze_movements. Found {len(intensive_movements)}. Total duration: {total_duration}s.')
    return intensive_movements
