import os


def contains_wav_files(directory_path):
    """
    Check if the given directory contains any .wav files.

    Args:
        directory_path (str): The path to the directory to check.

    Returns:
        bool: True if the directory contains at least one .wav file, False otherwise.

    Raises:
        ValueError: If the provided path is not a valid directory.
    """

    if not os.path.isdir(directory_path):
        raise ValueError(f"{directory_path} is not a valid directory.")

    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith('.wav'):
            return True

    return False
