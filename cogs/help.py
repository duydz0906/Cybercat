import discord
from discord.ext import commands
from discord import app_commands
import random

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def random_color(self):
        return discord.Color(random.randint(0, 0xFFFFFF))

    @commands.command(name="helpme", help="Hiển thị danh sách các lệnh")
    async def helpme(self, ctx):
        embed = discord.Embed(title="📖 Danh sách lệnh bot", color=self.random_color())

        embed.add_field(
            name="Phát nhạc 🎵",
            value=(
                "`d!play <link/từ khóa>` - Phát nhạc\n"
                "`d!savepl <tên>` - Lưu hàng đợi\n"
                "`d!loadpl <tên>` - Tải playlist\n"
                "`d!mypl` - Danh sách playlist\n"
                "`d!shuffle` - Xáo trộn hàng đợi"
            ),
            inline=False
        )

        embed.add_field(
            name="Điều khiển ⏯️",
            value=(
                "`d!seek <giây>` - Tua bài\n"
                "`d!forceskip` - Bỏ qua ngay (DJ/dev)\n"
                "`d!voteskip` - Bỏ phiếu skip\n"
                "`d!nowplaying` - Bài đang phát\n"
                "`d!lyrics` - Lời bài hát"
            ),
            inline=False
        )

        embed.add_field(
            name="Thông tin ℹ️",
            value="`d!invite` - Mời bot vào server khác\n`d!helpme` - Xem hướng dẫn\n`d!server` - Thống kê server & ping",
            inline=False
        )

        await ctx.send(embed=embed)

    @app_commands.command(name="help", description="Hiển thị danh sách các lệnh")
    async def slash_help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📖 Danh sách lệnh bot", color=self.random_color())

        embed.add_field(
            name="Phát nhạc 🎵",
            value=(
                "`/play` - Phát nhạc\n"
                "`/saveplaylist` - Lưu playlist\n"
                "`/loadplaylist` - Tải playlist\n"
                "`/myplaylists` - Danh sách playlist\n"
                "`/shuffle` - Xáo trộn hàng đợi"
            ),
            inline=False
        )

        embed.add_field(
            name="Điều khiển ⏯️",
            value=(
                "`/seek` - Tua bài\n"
                "`/forceskip` - Bỏ qua ngay\n"
                "`/voteskip` - Bỏ phiếu skip\n"
                "`/nowplaying` - Bài đang phát\n"
                "`/lyrics` - Lời bài hát"
            ),
            inline=False
        )

        embed.add_field(
            name="Thông tin ℹ️",
            value="`/invite` - Mời bot vào server khác\n`/help` - Xem hướng dẫn\n`/server` - Thống kê server & ping",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot))