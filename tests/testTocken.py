import asyncio
from telegram import Bot

async def test_token():
    token = "7957135457:AAHmzUw9cfQ_bRfqwNCDSNio4ZqkI-QCTpA"  # Replace with your token
    bot = Bot(token)
    
    try:
        me = await bot.get_me()
        print(f"✅ Token is valid! Bot info:")
        print(f"ID: {me.id}")
        print(f"Username: @{me.username}")
        print(f"Name: {me.first_name}")
    except Exception as e:
        print(f"❌ Invalid token: {e}")

asyncio.run(test_token())