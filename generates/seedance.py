import asyncio
from typing import Literal

import replicate

from config_data.config import Config, load_config
from errors.generate_error import AIGenerationError, InputGenerationError


config: Config = load_config()


client = replicate.Client(api_token=config.seedance.api_key)


async def get_seedance_video(prompt: str, model: Literal['seedance-1-pro', 'seedance-1-lite'], duration: Literal[5, 10], sizes: Literal["16:9", "9:16"], image: str | None = None) -> str:
    data = {
        'prompt': prompt,
        'duration': duration,
        'aspect_ratio': sizes,
    }
    if image:
        data['image'] = image
    try:
        output = await client.predictions.async_create(
            model=f"bytedance/{model}",
            input=data
        )
    except Exception as err:
        raise InputGenerationError(f'Ошибка при создании запроса на генерацию: {err}')
    prediction_id = output.id
    prediction = await client.predictions.async_get(prediction_id)
    while True:
        if prediction.status == 'failed':
            raise AIGenerationError(output.error)
        if prediction.status == 'succeeded':
            return prediction.output
        await asyncio.sleep(4)
        prediction = await client.predictions.async_get(prediction_id)