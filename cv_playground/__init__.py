import cv2 as cv
import sys
from pathlib import Path

"""
Sandbox function 1. Load an image and display it, then re-saves it in a different format when the 's' key is pressed.
"""


def resave_img():
    print('resave_img()')

    """
    Load the image. The second parameter of imread is optional. It specifies the format in which the image is read.
    By default, the image is read in color format (IMREAD_COLOR). Other options include: IMREAD_UNCHANGED and
    IMREAD_GRAYSCALE. Image data is stored in a cv.Mat object.
    """
    img_path = Path(__file__).parent / './starry_night.jpg'
    img = cv.imread(str(img_path))
    if img is None:
        sys.exit('Could not read the image.')

    """
    Show the image with cv.imshow(). The first parameter is the window name, and the second parameter is the image data.
    cv.waitKey() waits for a key event for a specific amount of time (0 means indefinite). The return value is the
    Unicode point of the pressed key.
    """
    cv.imshow('Display window', img)
    k = cv.waitKey(0)

    """
    If the pressed key is 's', save the image with cv.imwrite(). The first parameter is the file name, and the second
    parameter is the image data. This essentially re-saves the same image as a new format (PNG).
    """
    if k == ord('s'):
        output_path = Path(__file__).parent / './starry_night.png'
        cv.imwrite(str(output_path), img)


def main():
    resave_img()
