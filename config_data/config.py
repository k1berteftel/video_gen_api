from dataclasses import dataclass

from environs import Env


@dataclass
class Unifically:
    api_key: str


@dataclass
class Seedance:
    api_key: str

@dataclass
class Lingvanex:
    api_key: str


@dataclass
class Config:
    unifically: Unifically
    seedance: Seedance
    lingvanex: Lingvanex


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        unifically=Unifically(
            api_key=env('unifically_api_key')
        ),
        seedance=Seedance(
            api_key=env('seedance_api_key')
        ),
        lingvanex=Lingvanex(
            api_key=env('lingvanex_api_key')
        )
    )