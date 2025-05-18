import requests
from io import BytesIO

HF_TOKEN = "YOUR_HUGGINGFACE_TOKEN"  # <-- replace this
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def generate_image(prompt: str) -> BytesIO | None:
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        print(f"Image generation failed: {response.status_code}, {response.text}")
        return None
