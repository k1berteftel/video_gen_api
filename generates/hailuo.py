import asyncio
from typing import Literal
import aiohttp

from config_data.config import Config, load_config
from errors.generate_error import AIGenerationError, InputGenerationError


config: Config = load_config()


models = {
    'hailuo-02-fast': 'MiniMax-Hailuo-02',
    'hailuo-02': 'MiniMax-Hailuo-2.3'
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
                await asyncio.sleep(5)


async def get_hailuo_video(prompt: str, model: Literal['hailuo-02-fast', 'hailuo-02'], duration: int, image: str | None = None):
    url = 'https://api.apimart.ai/v1/videos/generations'
    headers = {
        "Authorization": f"Bearer {config.apimart.api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": models.get(model),
        "prompt": prompt,
        "duration": duration,
        "resolution": "768p"
    }
    if image:
        data['first_frame_image'] = image

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


#prompt = 'Create a realistic vertical video (9:16), as if recorded with an iPhone at an outdoor seasons as summer. The setting has warm lighting from streetlights or soft party lights. A little girl around 2 to 3 years old, with light skin tone, long curly dark hair, and big brown expressive eyes, runs joyfully toward a young couple sitting close together. The couple must look exactly like the people in the attached photo — no changes to their facial features, skin tone, hairstyle, or clothing. They both have medium skin, man have dark hair, women have dark hair and are man wearing summer outfits. The child should clearly look like their daughter, with features that naturally combine both parents. She hugs them lovingly, wrapping her arms around them, smiling and laughing. The couple smiles and embraces her warmly. The video should feel authentic, as if casually filmed by a friend or family member on a phone — slightly shaky, casually composed, and emotionally genuine.'
#print(asyncio.run(get_hailuo_video(prompt, 'hailuo-02', 'https://i.ibb.co/JFzb41y9/7f3a359df8e1.jpg')))