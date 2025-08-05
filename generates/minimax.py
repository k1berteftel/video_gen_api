import asyncio
from typing import Literal
import aiohttp

from errors.generate_error import AIGenerationError, InputGenerationError
from config_data.config import Config, load_config


config: Config = load_config()

headers = {
  'authorization': f'Bearer {config.minimax.api_key}',
  'Content-Type': 'application/json'
}


async def _fetch_video_result(file_id: str):
    url = f"https://api.minimaxi.com/v1/files/retrieve?file_id={file_id}"
    header = {
        'authorization': f'Bearer {config.minimax.api_key}',
    }
    async with aiohttp.ClientSession() as client:
        async with client.get(url, headers=header) as response:
            data = await response.json()
            return [data['file']['download_url']]


async def _get_generation(task_id: str):
    counter = 0
    url = f'https://api.minimaxi.com/v1/query/video_generation?task_id={task_id}'
    async with aiohttp.ClientSession() as client:
        while True:
            async with client.get(url, headers=headers) as response:
                if response.status != 200:
                    if counter == 7:
                        raise AIGenerationError('Превышен лимит проверок генерации')
                    counter += 1
                    continue
                data = await response.json()
                if data['status'] == 'Fail':
                    err = data['base_resp']
                    raise AIGenerationError(f'{err["status_code"]: {err["status_msg"]}}')
                if data['status'] == 'Success':
                    file_id = data['file_id']
                    break
                await asyncio.sleep(4)
        return await _fetch_video_result(file_id)


async def get_minimax_video(prompt: str, image: str | None = None) -> list[str]:
    url = 'https://api.minimaxi.com/v1/video_generation'
    data = {
        'model': 'MiniMax-Hailuo-02',
        'prompt': prompt,
        'duration': 6,
    }
    if image:
        data['first_frame_image'] = image
    async with aiohttp.ClientSession() as client:
        async with client.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                raise InputGenerationError()
            data = await response.json()
            if data['base_resp']['status_code'] != 0:
                raise InputGenerationError(data['base_resp']['status_msg'])
            task_id = data['task_id']
    result = await _get_generation(task_id)
    return result

