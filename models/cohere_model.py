import cohere
from src.config import Config
import asyncio

co = cohere.Client(Config.COHERE_API_KEY)

async def generate_response(prompt: str) -> str:
    try:
        response = await asyncio.to_thread(
            co.generate,
            model="command-r-plus",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception as e:
        print(f"❌ Cohere Error: {e}")
        return f"⚠️ Cohere Error: {e}"
