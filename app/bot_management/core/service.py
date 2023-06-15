import subprocess


def convert_to_wav(input_filepath, output_filepath):
    command = ["ffmpeg", "-i", input_filepath, output_filepath]
    subprocess.run(command, check=True)
