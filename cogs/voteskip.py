import discord
from discord.ext import commands
from discord import app_commands

class VoteSkip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.skip_votes = {}  # guild_id: set(user_ids)

    @commands.command(name="voteskip", help="Bỏ phiếu skip bài hiện tại")
    async def voteskip(self, ctx):
        guild_id = ctx.guild.id
        vc = ctx.guild.voice_client
        if not vc:
            await ctx.send("Bot chưa kết nối voice.")
            return

        listeners = len(vc.channel.members) - 1  # trừ bot
        if listeners <= 0:
            await ctx.send("Không có người nghe để vote skip.")
            return

        self.skip_votes.setdefault(guild_id, set()).add(ctx.author.id)
        vote_count = len(self.skip_votes[guild_id])
        required = listeners // 2 + 1
        if vote_count >= required:
            vc.stop()
            await ctx.send("✅ Bài đã skip qua bỏ phiếu.")
            self.skip_votes[guild_id].clear()
        else:
            await ctx.send(f"🗳️ {vote_count}/{required} phiếu skip.")

    @app_commands.command(name="voteskip", description="Bỏ phiếu skip bài đang phát")
    async def slash_voteskip(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("Bot chưa kết nối voice.", ephemeral=True)
            return

        listeners = len(vc.channel.members) - 1
        if listeners <= 0:
            await interaction.response.send_message("Không có người nghe để vote skip.", ephemeral=True)
            return

        self.skip_votes.setdefault(guild_id, set()).add(interaction.user.id)
        vote_count = len(self.skip_votes[guild_id])
        required = listeners // 2 + 1

        if vote_count >= required:
            vc.stop()
            self.skip_votes[guild_id].clear()
            await interaction.response.send_message("✅ Bài đã skip qua bỏ phiếu.")
        else:
            await interaction.response.send_message(f"🗳️ {vote_count}/{required} phiếu skip.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VoteSkip(bot))