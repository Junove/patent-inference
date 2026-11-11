from functools import lru_cache

from app.config import get_settings
from app.generator.client import HttpNearAIClient, NearAIClient


@lru_cache
def get_near_ai_client() -> NearAIClient:
    return HttpNearAIClient(get_settings())
