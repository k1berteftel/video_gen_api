import asyncio
import aiohttp

from config_data.config import Config, load_config
from errors.generate_error import TranslateError

config: Config = load_config()


headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Bearer {config.lingvanex.api_key}"
}


async def translate_text(text: str) -> str:
    url = "https://api-b2b.backenster.com/b1/api/v3/translate"
    data = {
        "platform": "api",
        "from": "ru_RU",
        "to": "en_GB",
        "data": text
    }
    async with aiohttp.ClientSession() as client:
        async with client.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                raise TranslateError(f'Ошибка при переводе текста: {await response.content.read()}')
            data = await response.json()
            if data['err']:
                raise TranslateError(f'Ошибка при переводе текста: {data["err"]}')
            return data['result']
