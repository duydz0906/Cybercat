import discord
from discord.ext import commands
from discord import app_commands
import json
import os

playlist_file = "data/playlists.json"

# Tạo thư mục data nếu chưa có
os.makedirs("data", exist_ok=True)

if not os.path.exists(playlist_file):
    with open(playlist_file, "w", encoding="utf8") as f:
        json.dump({}, f)

def load_playlists():
    with open(playlist_file, "r", encoding="utf8") as f:
        return json.load(f)

def save_playlists(data):
    with open(playlist_file, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlists = load_playlists()

    @commands.command(name="savepl", help="Lưu hàng đợi thành playlist riêng")
    async def saveplaylist(self, ctx, name: str):
        guild_id = ctx.guild.id
        queues = self.bot.get_cog("Music").queues
        q = queues.get(guild_id, [])
        if not q:
            await ctx.send("Hàng đợi trống.")
            return
        self.playlists.setdefault(str(ctx.author.id), {})[name] = [
            {"url": s.url, "title": s.title, "duration": s.duration} for s in q
        ]
        save_playlists(self.playlists)
        await ctx.send(f"✅ Đã lưu playlist `{name}`.")

    @commands.command(name="loadpl", help="Tải playlist đã lưu")
    async def loadplaylist(self, ctx, name: str):
        user_pl = self.playlists.get(str(ctx.author.id), {})
        if name not in user_pl:
            await ctx.send("Không tìm thấy playlist.")
            return
        queues = self.bot.get_cog("Music").queues
        guild_id = ctx.guild.id
        queues[guild_id] = [
            self.bot.get_cog("Music").Song(i["url"], i["title"], i["duration"])
            for i in user_pl[name]
        ]
        await ctx.send(f"✅ Đã nạp playlist `{name}` vào hàng đợi.")

    @commands.command(name="mypl", help="Xem các playlist đã lưu")
    async def myplaylists(self, ctx):
        user_pl = self.playlists.get(str(ctx.author.id), {})
        if not user_pl:
            await ctx.send("Bạn chưa có playlist nào.")
            return
        await ctx.send("🎵 Playlist của bạn:\n" + "\n".join(f"- {name}" for name in user_pl))

async def setup(bot):
    await bot.add_cog(Playlist(bot))