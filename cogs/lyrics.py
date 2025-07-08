import discord
from discord.ext import commands
from discord import app_commands
from utils.genius import get_lyrics

class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_and_send_lyrics(self, ctx_or_interaction):
        if isinstance(ctx_or_interaction, discord.Interaction):
            guild = ctx_or_interaction.guild
        else:
            guild = ctx_or_interaction.guild
        
        music_cog = self.bot.get_cog("Music")
        if not music_cog:
            message = "Music cog chưa được load."
            if isinstance(ctx_or_interaction, discord.Interaction):
                await ctx_or_interaction.response.send_message(message, ephemeral=True)
            else:
                await ctx_or_interaction.send(message)
            return
        
        song = music_cog.current_song.get(guild.id)
        if not song:
            message = "Không có bài nào đang phát."
            if isinstance(ctx_or_interaction, discord.Interaction):
                await ctx_or_interaction.response.send_message(message, ephemeral=True)
            else:
                await ctx_or_interaction.send(message)
            return
        
        lyrics = get_lyrics(song.title)
        if not lyrics:
            text = "Không tìm thấy lời bài hát."
            if isinstance(ctx_or_interaction, discord.Interaction):
                await ctx_or_interaction.response.send_message(text, ephemeral=True)
            else:
                await ctx_or_interaction.send(text)
            return

        chunks = [lyrics[i:i+2000] for i in range(0, len(lyrics), 2000)]
        for chunk in chunks:
            if isinstance(ctx_or_interaction, discord.Interaction):
                await ctx_or_interaction.followup.send(chunk)
            else:
                await ctx_or_interaction.send(chunk)

    @commands.command(name="lyrics", help="Xem lời bài hát hiện tại")
    async def lyrics(self, ctx):
        await self.fetch_and_send_lyrics(ctx)

    @app_commands.command(name="lyrics", description="Xem lời bài hát hiện tại")
    async def slash_lyrics(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.fetch_and_send_lyrics(interaction)

async def setup(bot):
    await bot.add_cog(Lyrics(bot))
