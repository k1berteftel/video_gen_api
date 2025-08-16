import asyncio
from typing import Literal

import replicate

from config_data.config import Config, load_config
from errors.generate_error import AIGenerationError, InputGenerationError


config: Config = load_config()


client = replicate.Client(api_token=config.seedance.api_key)


async def get_hailuo_video(prompt: str, model: Literal['hailuo-02-fast', 'hailuo-02'], image: str):
    data = {
        'prompt': prompt,
    }
    if image:
        data['first_frame_image'] = image
    if model == 'hailuo-02':
        data['resolution'] = '768p'
    try:
        output = await client.predictions.async_create(
            model=f"minimax/{model}",
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


#prompt = 'Create a realistic vertical video (9:16), as if recorded with an iPhone at an outdoor seasons as summer. The setting has warm lighting from streetlights or soft party lights. A little girl around 2 to 3 years old, with light skin tone, long curly dark hair, and big brown expressive eyes, runs joyfully toward a young couple sitting close together. The couple must look exactly like the people in the attached photo — no changes to their facial features, skin tone, hairstyle, or clothing. They both have medium skin, man have dark hair, women have dark hair and are man wearing summer outfits. The child should clearly look like their daughter, with features that naturally combine both parents. She hugs them lovingly, wrapping her arms around them, smiling and laughing. The couple smiles and embraces her warmly. The video should feel authentic, as if casually filmed by a friend or family member on a phone — slightly shaky, casually composed, and emotionally genuine.'
#print(asyncio.run(get_hailuo_video(prompt, 'hailuo-02', 'https://i.ibb.co/JFzb41y9/7f3a359df8e1.jpg')))