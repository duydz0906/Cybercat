import discord
from discord.ext import commands
from keep_alive import keep_alive
import os
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
APP_ID = int(os.getenv("APPLICATION_ID"))  # ID bot của bạn

# Thiết lập intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Tạo bot instance và truyền application_id rõ ràng
bot = commands.Bot(
    command_prefix="d!",
    intents=intents,
    application_id=APP_ID
)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_disconnect():
    print("⚠️ Bot disconnected")

@bot.event
async def on_resumed():
    print("🔄 Bot reconnected")

# Hàm chính load các Cog và sync slash commands
async def main():
    extensions = [
        "cogs.music",
        "cogs.seek",
        "cogs.lyrics",
        "cogs.voteskip",
        "cogs.move",
        "cogs.shuffle",
        "cogs.nowplaying",
        "cogs.dj",
        "cogs.playlist",
        "cogs.help",
        "cogs.server_info",
    ]

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Loaded {ext}")
        except Exception as e:
            print(f"❌ Failed to load {ext}: {e}")

    # 👉 Sync slash commands sau khi đã load đầy đủ các Cog
    try:
        synced = await bot.tree.sync()
        print(f"🌐 Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Sync error: {e}")

    await bot.start(TOKEN)

# Khởi động Flask server nếu có (UptimeRobot)
keep_alive()

# Khởi chạy chương trình
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
