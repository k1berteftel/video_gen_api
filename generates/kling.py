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
    url = f'https://api.unifically.com/kling/v1/videos/generations/{task_id}'
    async with aiohttp.ClientSession() as client:
        while True:
            async with client.get(url, headers=headers) as response:
                if response.status != 200:
                    raise AIGenerationError()
                data = await response.json()
                if data['data']['status'] == 'failed':
                    raise AIGenerationError(f'{data['data']['error']['code']}: {data['data']['error']['message']}')
                if data['data']['status'] == 'completed':
                    return data['data']['output']['video_url']
                await asyncio.sleep(4)


async def get_kling_video(prompt: str, duration: Literal[5, 10], sizes: Literal["16:9", "9:16"], image: str | None = None) -> str:
    prompt = await translate_text(prompt)
    url = 'https://api.unifically.com/kling/v1/videos/generations'
    data = {
        "model": "2.1-master",
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": sizes
    }
    if image:
        data['image_url'] = image

    async with aiohttp.ClientSession() as client:
        async with client.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                raise InputGenerationError(await response.content.read())
            data = await response.json()
            if data['code'] != 200:
                error = f'{data["code"]}: {data['data']['error']["message"]}'
                raise InputGenerationError(error)
            task_id = data['data']['task_id']
    return await _poll_generation(task_id)

