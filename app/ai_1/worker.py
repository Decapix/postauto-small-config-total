from celery import Celery
import time
import os
from pathlib import Path
import subprocess


app = Celery('worker', broker='pyamqp://guest@rabbitmq//', backend='rpc://')


BASE_DIR_CONTROLLER = Path(__file__).resolve().parent / "facefusion"



@app.task
def process_deepfake(video_path, image_path, output_path):
    process_video(image_path, video_path, output_path)
    print("video precessed successfully")
    # effacer les video de bases
    # cleanup_files(image_path, video_path)
    return output_path




# func

def cleanup_files(*paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)

def process_video(image_path, video_path, output_path):
    os.chdir(BASE_DIR_CONTROLLER)  # Change le répertoire de travail
    command = [
        "python", "run.py", "--headless",
        "--source",  image_path,
        "--target",  video_path,
        "--output", output_path
    ]

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("Command output:", result.stdout)
        print("Video processed successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to process video:", e)
        print("Error output:", e.stderr)

    