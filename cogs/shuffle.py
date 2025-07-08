import discord
from discord.ext import commands
from discord import app_commands
from utils.storage import load_queue, save_queue

queues = load_queue()

class Shuffle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shuffle", help="Xáo trộn hàng đợi")
    async def shuffle(self, ctx):
        guild_id = ctx.guild.id
        if guild_id not in queues or len(queues[guild_id]) <= 1:
            await ctx.send("Không có đủ bài trong hàng đợi để shuffle.")
            return

        import random
        random.shuffle(queues[guild_id])
        save_queue(queues)
        await ctx.send("🔀 Hàng đợi đã được shuffle!")

    @app_commands.command(name="shuffle", description="Xáo trộn hàng đợi hiện tại")
    async def slash_shuffle(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id not in queues or len(queues[guild_id]) <= 1:
            await interaction.response.send_message("Không có đủ bài trong hàng đợi để shuffle.", ephemeral=True)
            return

        import random
        random.shuffle(queues[guild_id])
        save_queue(queues)
        await interaction.response.send_message("🔀 Hàng đợi đã được shuffle!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Shuffle(bot))
