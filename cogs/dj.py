import discord
from discord.ext import commands
from discord import app_commands

# ID của người được phép skip dù không có role DJ
DEV_USER_ID = 478000224074203136 

async def is_dj_check(interaction_or_ctx):
    if isinstance(interaction_or_ctx, discord.Interaction):
        member = interaction_or_ctx.user
        guild = interaction_or_ctx.guild
    else:
        member = interaction_or_ctx.author
        guild = interaction_or_ctx.guild

    # ✅ Cho phép dev vượt quyền DJ
    if member.id == DEV_USER_ID:
        return True

    dj_role = discord.utils.get(guild.roles, name="DJ")
    if dj_role and dj_role in member.roles:
        return True

    # Thông báo nếu không có quyền
    if isinstance(interaction_or_ctx, discord.Interaction):
        await interaction_or_ctx.response.send_message(
            "Bạn cần role DJ để dùng lệnh này.", ephemeral=True
        )
    else:
        await interaction_or_ctx.send("Bạn cần role DJ để dùng lệnh này.")
    return False

class DJ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="forceskip", help="Skip ngay lập tức (DJ only hoặc Dev)")
    async def forceskip(self, ctx):
        if not await is_dj_check(ctx):
            return
        if not ctx.guild.voice_client:
            await ctx.send("Bot không có trong voice.")
            return
        ctx.guild.voice_client.stop()
        await ctx.send("⏭️ DJ đã skip bài này.")

    @app_commands.command(name="forceskip", description="Skip ngay lập tức (DJ only hoặc Dev)")
    async def slash_forceskip(self, interaction: discord.Interaction):
        if not await is_dj_check(interaction):
            return
        if not interaction.guild.voice_client:
            await interaction.response.send_message("Bot không có trong voice.", ephemeral=True)
            return
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏭️ DJ đã skip bài này.")

async def setup(bot):
    await bot.add_cog(DJ(bot))
