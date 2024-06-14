from celery import Celery
from pathlib import Path
import subprocess
import os
import stat



app = Celery('worker', broker='pyamqp://guest@rabbitmq//', backend='rpc://')


BASE_DIR_CONTROLLER = Path(__file__).resolve().parent / "facefusion"



@app.task
def process_deepfake(video_path, image_path, video_name):
    video_filename_processed = f"processed_{video_name}"
    output_path =  f"/data/results/{video_filename_processed}"

    os.chmod(video_path, 0o777) 
    os.chmod(image_path, 0o777) 

    process_video(image_path, video_path, output_path)


    os.chmod(output_path, 0o777) 
    print("read_file_permissions 2")
    read_file_permissions(output_path) 

    cleanup_files(image_path, video_path)
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





def read_file_permissions(file_path):
    # Vérifie si le fichier existe
    if not os.path.exists(file_path):
        print("Le fichier spécifié n'existe pas.")
        return

    # Obtenir les permissions du fichier
    file_stat = os.stat(file_path)
    permissions = stat.filemode(file_stat.st_mode)
    print(f"Les permissions du fichier {file_path} sont : {permissions}")

