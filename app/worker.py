from celery import Celery
import time

app = Celery('worker', broker='pyamqp://guest@rabbitmq//', backend='rpc://')

@app.task
def process_deepfake(video_path, image_path):
    # Simulate a long processing task
    import shutil
    output_video_path = video_path.replace(".mp4", "_processed.mp4")
    shutil.copy(video_path, output_video_path)  # Simulation de la création d'un deepfake
    time.sleep(10)
    return output_video_path.split('/')[-1]
