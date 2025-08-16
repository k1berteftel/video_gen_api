from typing import Literal

from pydantic import BaseModel


class GenerationResponse(BaseModel):
    prompt: str
    image_urls: list[str] | None = None
    model_name: Literal[
        'veo3_quality', 'veo3_fast', 'kling-v2.1-master',
        'seedance-1-lite', 'seedance-1-pro', 'hailuo-02-fast', 'hailuo-02'
    ]
    duration: int = 5
    aspect_ratio: Literal['16:9', '9:16'] = '16:9'
