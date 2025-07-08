import discord
from discord.ext import commands
from discord import app_commands
from utils.storage import load_queue

queues = load_queue()

class NowPlaying(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_song = {}  # guild_id : Song

    @commands.command(name="nowplaying", help="Hiển thị bài đang phát")
    async def nowplaying(self, ctx):
        guild_id = ctx.guild.id
        song = self.bot.get_cog("Music").current_song.get(guild_id)
        if not song:
            await ctx.send("Hiện không có bài nào đang phát.")
            return
        m, s = divmod(song.duration, 60)
        await ctx.send(f"🎵 **{song.title}** - `{m:02}:{s:02}`")

    @app_commands.command(name="nowplaying", description="Hiển thị bài đang phát")
    async def slash_nowplaying(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        song = self.bot.get_cog("Music").current_song.get(guild_id)
        if not song:
            await interaction.response.send_message("Hiện không có bài nào đang phát.", ephemeral=True)
            return
        m, s = divmod(song.duration, 60)
        await interaction.response.send_message(f"🎵 **{song.title}** - `{m:02}:{s:02}`")

async def setup(bot):
    await bot.add_cog(NowPlaying(bot))
