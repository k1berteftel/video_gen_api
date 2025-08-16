import asyncio
import aiohttp
from typing import Literal

from translator.translate import translate_text
from config_data.config import Config, load_config
from errors.generate_error import InputGenerationError, AIGenerationError


config: Config = load_config()


headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {config.unifically.api_key}'
}


async def _poll_generation(task_id: str):
    url = f'https://api.unifically.com/veo-3/status/{task_id}'
    async with aiohttp.ClientSession() as client:
        while True:
            async with client.get(url, headers=headers) as response:
                if response.status != 200:
                    raise AIGenerationError()
                data = await response.json()
                if data['success'] != True:
                    error = f'{data["code"]}: {data["message"]}'
                    raise AIGenerationError(error)
                if data['data']['status'] == 'completed':
                    return data['data']['video_url']
                await asyncio.sleep(4)


async def get_veo_video(prompt: str, model: Literal['veo3_quality', 'veo3_fast'], image: str | None = None) -> str:
    prompt = await translate_text(prompt)
    url = 'https://api.unifically.com/veo-3/generate'
    data = {
        "model": model,
        "prompt": prompt
    }
    if image:
        data['image_url'] = image
    async with aiohttp.ClientSession() as client:
        async with client.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                raise InputGenerationError(await response.content.read())
            data = await response.json()
            if data['success'] != True:
                error = f'{data["code"]}: {data["message"]}'
                raise InputGenerationError(error)
            task_id = data['id']
    return await _poll_generation(task_id)
