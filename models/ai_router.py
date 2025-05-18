# models/ai_router.py

from models.cohere_model import generate_response as cohere_generate

async def generate_with_fallback(prompt: str) -> str:
    try:
        return await cohere_generate(prompt)
    except Exception as e:
        print(f"[Cohere Error] {e}")
        return "⚠️ Cohere AI service failed. Please try again later."
