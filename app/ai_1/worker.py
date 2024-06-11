from celery import Celery
import time
import os
from pathlib import Path
import subprocess
import shutil

app = Celery('worker', broker='pyamqp://guest@rabbitmq//', backend='rpc://')


BASE_DIR_CONTROLLER = Path(__file__).resolve().parent / "facefusion"



@app.task
def process_deepfake(video_path, image_path, video_name):
    temp_dir = Path(__file__).resolve().parent / "temp_video"
    video_filename_processed = f"processed_{video_name}"
    temp_output_path = temp_dir / video_filename_processed
    output_path =  f"/data/results/{video_filename_processed}"

    process_video(image_path, video_path, temp_output_path)

    shutil.move(str(temp_output_path), str(output_path))

    cleanup_files(image_path, video_path, temp_output_path)
    return output_path




# func

def cleanup_files(*paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)

def process_video(image_path, video_path, temp_output_path):
    os.chdir(BASE_DIR_CONTROLLER)  # Change le répertoire de travail
    command = [
        "python", "run.py", "--headless",
        "--source",  image_path,
        "--target",  video_path,
        "--output", temp_output_path
    ]

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("Command output:", result.stdout)
        print("Video processed successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to process video:", e)
        print("Error output:", e.stderr)

    