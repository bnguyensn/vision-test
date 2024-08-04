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

### Fine-tuning

Parameters to fine-tune:
- Foreground mask threshold
- History
- Variance threshold
- Minimum and maximum "heavy movement" segment length
- Frame rate

## How to use

### IDE

If using PyCharm, make sure you set up your Python interpreter so that the IDE correctly detects your packages. See [here](https://www.jetbrains.com/help/pycharm/package-installation-issues.html#terminal).

### Python

Please install Python first to your system. You can download it from [here](https://www.python.org/downloads/).

Poetry specifies the Python version of the project. See `pyproject.toml`, section `tool.poetry.dependencies`. If you run into version problems e.g. "current Python version is not allowed by the project", you can change Python version with `poetry env use /path/to/python` or `poetry env use python3.12` or `poetry env use 3.12` if Python 3.12 is available in your `PATH`. See more [here](https://python-poetry.org/docs/managing-environments/). What this does, is it lets Poetry re-create the virtualenv folder.

Poetry can be configured using an (uncommitted) `poetry.toml` file. This controls things like: virtual environment location, etc. See more [here](https://python-poetry.org/docs/configuration).

### Python virtual environment

By default, Poetry creates a virtual environment in `{cache-dir}/virtualenvs`. [`{cache-dir}`](https://python-poetry.org/docs/configuration/#cache-dir) has a default location e.g. on Windows, it's `C:\Users\{user}\AppData\Local\pypoetry\Cache`. It's possible to create virtualenv inside this project's root directory using [`virtualenvs.in-project`](https://python-poetry.org/docs/configuration/#virtualenvsin-project).

To find out where this project's virtual environment is located, run `poetry env info --path`.

Initialise the project using `poetry install`. This will let Poetry install dependencies and update the `poetry.lock` file.

Run the project using `poetry run run-vision-test`. This script is defined in `pyproject.toml`.

You can provide arguments to the program. All arguments are optional.

```bash
# Run the program on 'path/to/input.mp4' video, with a movement threshold of 1000.
$ poetry run run-vision-test --input "data/video.mp4" --mvmt 1000 --history 500 --shadows False
```

## Deployment

This service is meant to be triggered whenever there is a new long-form video uploaded to storage. The trigger is handled via main.py using GCP's `functions_framework`, as this is deployed as a Google Cloud Function.

## Miscellaneous

### CV playground

Try this command:

```bash
$ poetry run cv-playground
```
