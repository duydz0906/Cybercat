import discord
from discord.ext import commands
from discord import app_commands
import random

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def random_color(self):
        return discord.Color(random.randint(0, 0xFFFFFF))

    def get_server_list(self):
        server_names = [f"• {guild.name} ({guild.member_count} thành viên)" for guild in self.bot.guilds]
        return "\n".join(server_names) if server_names else "Không có server nào."

    @commands.command(name="server", help="Hiển thị số server bot đang ở và ping hiện tại")
    async def server_info(self, ctx):
        guilds = len(self.bot.guilds)
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="📊 Thông tin Bot",
            description=f"Bot hiện đang ở **{guilds}** server\n⏱️ Ping hiện tại: **{latency}ms**",
            color=self.random_color()
        )
        embed.add_field(name="📌 Danh sách server:", value=self.get_server_list(), inline=False)
        await ctx.send(embed=embed)

    @app_commands.command(name="server", description="Hiển thị số server bot đang ở và ping hiện tại")
    async def slash_server(self, interaction: discord.Interaction):
        guilds = len(self.bot.guilds)
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="📊 Thông tin Bot",
            description=f"Bot hiện đang ở **{guilds}** server\n⏱️ Ping hiện tại: **{latency}ms**",
            color=self.random_color()
        )
        embed.add_field(name="📌 Danh sách server:", value=self.get_server_list(), inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
