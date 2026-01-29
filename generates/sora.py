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
    url = f'https://api.unifically.com/v1/tasks/{task_id}'
    async with aiohttp.ClientSession() as client:
        while True:
            async with client.get(url, headers=headers) as response:
                if response.status != 200:
                    raise AIGenerationError()
                data = await response.json()
                if data['data']['status'] == 'failed':
                    raise AIGenerationError(f"{data['data']['error']['code']}: {data['data']['error']['message']}")
                if data['data']['status'] == 'completed':
                    return data['data']['output']['video_url']
                print(data)
                await asyncio.sleep(4)


async def get_sora_video(prompt: str, duration: Literal[4, 8, 12], sizes: Literal["16:9", "9:16"], image: str | None = None):
    url = f'https://api.unifically.com/v1/tasks'
    data = {
        "model": "openai/sora-2",
        "input": {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": sizes
        }
    }
    if image:
        data['image_url'] = image

    async with aiohttp.ClientSession() as client:
        async with client.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                raise InputGenerationError(await response.content.read())
            data = await response.json()
            if data['code'] != 200:
                error = f"{data['code']}: {data['data']['error']['message']}"
                raise InputGenerationError(error)
            task_id = data['data']['task_id']
    return await _poll_generation(task_id)


#print(asyncio.run(get_sora_video('Сделай бегущего мультяшного человечка', 'sora-2-pro', 12, "16:9")))