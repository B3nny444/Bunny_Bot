import cohere
import logging
from src.config import Config

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Cohere client
try:
    co = cohere.Client(Config.COHERE_API_KEY)
    logger.info("✅ Cohere initialized successfully.")
except Exception as e:
    logger.critical(f"❌ Failed to initialize Cohere: {e}")
    raise RuntimeError("AI service unavailable")

def get_ai_response(prompt: str) -> str:
    """
    Generate a concise AI response using Cohere.
    """
    try:
        if not prompt.strip():
            return "⚠️ Please enter a valid prompt."

        response = co.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )

        return response.generations[0].text.strip()

    except Exception as e:
        logger.error(f"Cohere error: {e}")
        return "⚠️ AI response failed. Please try again later."
