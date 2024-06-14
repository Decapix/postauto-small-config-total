import time
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from celery import Celery
import os
import secrets
import stat

app = FastAPI()

celery = Celery('tasks', broker='pyamqp://guest@rabbitmq//')
templates = Jinja2Templates(directory="templates")


@app.post("/submit_task", response_class=RedirectResponse)
async def submit_task(video: UploadFile = File(...), image: UploadFile = File(...)):
    video_uuid = secrets.token_hex(8)
    video_name = f"{video.filename.replace('.mp4', '')}_{video_uuid}.mp4"
    image_uuid = secrets.token_hex(8)
    image_name = f"{image.filename.replace('.png', '')}_{image_uuid}.png"

    video_filename = f"/data/uploads/videos/{video_name}"
    image_filename = f"/data/uploads/images/{image_name}"


    # Save video
    with open(video_filename, "wb") as video_file:
        video_file.write(await video.read())
    # Save image
    with open(image_filename, "wb") as image_file:
        image_file.write(await image.read())

    # Send task to Celery
    task = celery.send_task('worker.process_deepfake', args=[video_filename, image_filename, video_name])
    return RedirectResponse(url="/success", status_code=303)



@app.get("/success")
async def submission_success(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})


@app.get("/results")
async def list_results(request: Request):
    video_files = [f for f in os.listdir('/data/results') if f.endswith('.mp4')]
    # Simplification de la création de la liste des résultats
    results = [{'filename': v} for v in video_files]
    return templates.TemplateResponse("results.html", {"request": request, "results": results})



@app.post("/delete_video/{filename}")
async def delete_video(filename: str):
    os.remove(f"/data/results/{filename}")
    return RedirectResponse(url="/results", status_code=303)




@app.get("/video/{filename}", response_class=FileResponse)
async def get_video(filename: str):
    print("read_file_permissions 3")
    read_file_permissions(f"/data/results/{filename}") 
    return FileResponse(path=f"/data/results/{filename}", filename=filename, media_type='video/mp4')

@app.get("/")
async def submit_form(request: Request):
    return templates.TemplateResponse("submit_form.html", {"request": request})








def read_file_permissions(file_path):
    # Vérifie si le fichier existe
    if not os.path.exists(file_path):
        print("Le fichier spécifié n'existe pas.")
        return

    # Obtenir les permissions du fichier
    file_stat = os.stat(file_path)
    permissions = stat.filemode(file_stat.st_mode)
    print(f"Les permissions du fichier {file_path} sont : {permissions}")

# Exemple d'utilisation :
# read_file_permissions('/chemin/vers/le/fichier')