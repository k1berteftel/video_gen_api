import asyncio
from typing import Literal
import aiohttp

from translator.translate import translate_text
from errors.generate_error import AIGenerationError, InputGenerationError
from config_data.config import Config, load_config


config: Config = load_config()


headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {config.unifically.api_key}'
}


async def _poll_generation(task_id: str):
    url = f'https://api.apimart.ai/v1/tasks/{task_id}'
    headers = {
        "Authorization": f"Bearer {config.apimart.api_key}",
    }
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers, ssl=False) as response:
                if response.status != 200:
                    try:
                        data = await response.json()
                        error = f"{data['error'].get('code')}: {data['error'].get('message')}"
                    except Exception:
                        error = await response.text()
                    raise AIGenerationError(error)
                data = await response.json()
                print(data)
                status = data['data'].get('status')
                if status and status == 'failed':
                    error = f"{data['error'].get('code')}: {data['error'].get('message')}"
                    raise AIGenerationError(error)
                if status and status == 'completed':
                    return data['data']['result']['videos'][0].get('url')[0]
                await asyncio.sleep(3)


async def get_kling_video(prompt: str, duration: Literal[5, 10], sizes: Literal["16:9", "9:16"], image: str | None = None) -> str:
    url = 'https://api.apimart.ai/v1/videos/generations'
    headers = {
        "Authorization": f"Bearer {config.apimart.api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "kling-v2-6",
        "prompt": prompt,
        "mode": "std",
        "duration": duration,
        "aspect_ratio": sizes
    }
    if image:
        data['image_urls'] = [image]

    async with aiohttp.ClientSession() as client:
        async with client.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                try:
                    data = await response.json()
                    error = f"{data['error'].get('code')}: {data['error'].get('message')}"
                except Exception:
                    error = await response.text()
                raise InputGenerationError(error)
            data = await response.json()
            task_id = data['data'][0].get('task_id')
    return await _poll_generation(task_id)

