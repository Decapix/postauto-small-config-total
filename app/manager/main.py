from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from celery import Celery
import os
import uuid

app = FastAPI()

celery = Celery('tasks', broker='pyamqp://guest@rabbitmq//')
templates = Jinja2Templates(directory="manager/templates")

@app.post("/submit_task", response_class=RedirectResponse)
async def submit_task(video: UploadFile = File(...), image: UploadFile = File(...)):
    video_filename = f"/data/{video.filename.replace('.mp4', '')}_{uuid.uuid4()}.mp4"
    image_filename = f"/data/{image.filename.replace('.png', '')}_{uuid.uuid4()}.png"
    with open(video_filename, "wb") as video_file:
        video_file.write(await video.read())
    with open(image_filename, "wb") as image_file:
        image_file.write(await image.read())
    task = celery.send_task('ai_1.worker.process_deepfake', args=[video_filename, image_filename])
    return RedirectResponse(url="/success", status_code=303)

@app.get("/success")
async def submission_success(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})


@app.get("/results")
async def list_results(request: Request):
    video_files = [f for f in os.listdir('/data') if f.endswith('_processed.mp4')]
    results = [{'id': v.split('_')[1], 'filename': v} for v in video_files]
    return templates.TemplateResponse("results.html", {"request": request, "results": results})


@app.post("/delete_video/{filename}")
async def delete_video(filename: str):
    os.remove(f"/data/{filename}")
    return RedirectResponse(url="/results", status_code=303)




@app.get("/video/{filename}", response_class=FileResponse)
async def get_video(filename: str):
    return FileResponse(path=f"/data/{filename}", filename=filename, media_type='video/mp4')

@app.get("/submit_form")
async def submit_form(request: Request):
    return templates.TemplateResponse("submit_form.html", {"request": request})