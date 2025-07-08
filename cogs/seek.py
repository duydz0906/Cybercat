import discord
from discord.ext import commands
from discord import app_commands
from yt_dlp import YoutubeDL

class Seek(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="seek", help="Tua bài hát (giây)")
    async def seek(self, ctx, seconds: int):
        guild_id = ctx.guild.id
        vc = ctx.guild.voice_client
        song = self.bot.get_cog("Music").current_song.get(guild_id)
        if not vc or not song:
            await ctx.send("Không có bài nào đang phát.")
            return

        if seconds < 0 or seconds > song.duration:
            await ctx.send("Thời gian không hợp lệ.")
            return

        with YoutubeDL({"format": "bestaudio"}) as ydl:
            info = ydl.extract_info(song.url, download=False)
            audio_url = info["url"]

        vol = self.bot.get_cog("Music").volume.get(guild_id, 1.0)
        source = discord.FFmpegPCMAudio(
            audio_url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options=f"-vn -ss {seconds} -filter:a volume={vol}"
        )

        vc.stop()
        vc.play(source, after=lambda e: self.bot.loop.create_task(
            self.bot.get_cog("Music").play_next(ctx)
        ))
        await ctx.send(f"⏩ Đã tua tới {seconds} giây.")

    @app_commands.command(name="seek", description="Tua bài hát hiện tại theo giây")
    @app_commands.describe(seconds="Vị trí cần tua đến (tính theo giây)")
    async def slash_seek(self, interaction: discord.Interaction, seconds: int):
        await interaction.response.defer(ephemeral=True)
        guild_id = interaction.guild.id
        vc = interaction.guild.voice_client
        song = self.bot.get_cog("Music").current_song.get(guild_id)
        if not vc or not song:
            await interaction.followup.send("Không có bài nào đang phát.")
            return

        if seconds < 0 or seconds > song.duration:
            await interaction.followup.send("Thời gian không hợp lệ.")
            return

        with YoutubeDL({"format": "bestaudio"}) as ydl:
            info = ydl.extract_info(song.url, download=False)
            audio_url = info["url"]

        vol = self.bot.get_cog("Music").volume.get(guild_id, 1.0)
        source = discord.FFmpegPCMAudio(
            audio_url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options=f"-vn -ss {seconds} -filter:a volume={vol}"
        )

        vc.stop()
        vc.play(source, after=lambda e: self.bot.loop.create_task(
            self.bot.get_cog("Music").play_next(interaction)
        ))
        await interaction.followup.send(f"⏩ Đã tua tới {seconds} giây.")

async def setup(bot):
    await bot.add_cog(Seek(bot))
