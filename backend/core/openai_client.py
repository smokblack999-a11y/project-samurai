from openai import OpenAI
from .config import get_settings

def get_client() -> OpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured on the backend")
    return OpenAI(api_key=settings.openai_api_key, timeout=45.0, max_retries=0)
