from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from celery import Celery

app = FastAPI()

# Configure Celery
celery = Celery('tasks', broker='pyamqp://guest@rabbitmq//')

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.post("/submit_task", response_class=HTMLResponse)
async def submit_task(request: Request, n: int = Form(...)):
    try:
        task = celery.send_task('worker.fibonacci', args=[n])
        return templates.TemplateResponse("submit_task.html", {"request": request, "message": "Task submitted", "task_id": task.id})
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "message": str(e)})

@app.get("/get_result/{task_id}", response_class=HTMLResponse)
async def get_result(request: Request, task_id: str):
    try:
        with open(f"/data/{task_id}.txt", 'r') as file:
            result = file.read()
        return templates.TemplateResponse("get_result.html", {"request": request, "result": result, "task_id": task_id})
    except FileNotFoundError:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Result not found"})
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "message": str(e)})

@app.get("/submit_form")
async def submit_form(request: Request):
    return templates.TemplateResponse("submit_form.html", {"request": request})
