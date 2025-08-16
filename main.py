import asyncio
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from worker.tasks import TaskWorker
from models.gen_models import GenerationResponse
from server import UvicornServer
from generates import (get_seedance_video, get_veo_video, get_kling_video, get_hailuo_video)


# Создаём приложение
app = FastAPI(title="Video generation API")


worker = TaskWorker()


@app.post("/generate")
async def generate(request: GenerationResponse):
    try:
        model = request.model_name
        prompt = request.prompt
        image = request.image_urls[0] if request.image_urls else None
        if model in ['veo3_quality', 'veo3_fast']:
            func = get_veo_video
            args = [prompt, model, image]
        elif model == 'kling-v2.1-master':
            func = get_kling_video
            args = [prompt, request.duration, request.aspect_ratio, image]
        elif model in ['hailuo-02-fast', 'hailuo-02']:
            func = get_hailuo_video
            args = [prompt, model, image]
        else:
            func = get_seedance_video
            args = [prompt, model, request.duration, request.aspect_ratio, image]

        task_id = str(uuid.uuid4())
        await worker.add_task(task_id, func, args)
        return {
            'task_id': task_id
        }
    except Exception as err:
        print(err)
        return HTTPException(500, detail='Ошибка при создании задачи на генерацию')


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    try:
        task = await worker.get_task(task_id)
    except KeyError as err:
        return HTTPException(404, detail=str(err))
    return JSONResponse(content=task, status_code=200)


@app.get("/")
async def root():
    return {"message": "Video generation API работает"}


if __name__ == '__main__':
    server = UvicornServer(app, host="127.0.0.1", port=8000)
    try:
        server.start()
    except KeyboardInterrupt as err:
        print(err)
        asyncio.run(server.stop())


