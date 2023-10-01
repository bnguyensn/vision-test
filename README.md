# vision-test

Codebase notes:
- We have Poetry. Install packages with [`poetry add`](https://python-poetry.org/docs/cli/#add).
- `venv` was created using venv. Used as a local python interpreter.
- OpenCV link: https://pypi.org/project/opencv-python/#installation-and-usage
  - https://medium.com/analytics-vidhya/object-detection-with-opencv-step-by-step-6c49a9cc1ff0
  - https://towardsdatascience.com/yolo-you-only-look-once-17f9280a47b0
  - [Motion detection with background subtraction](https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html)

## Features

### Background subtraction

This is used to detect motion. It consists of 2 main steps:
- Background initialization: an initial model of the background is computed.
- Background update: the model is updated to adapt to possible changes in the scene.

## How to use

Run the project using `poetry run run-vision-test`. This script is defined in `pyproject.toml`.
