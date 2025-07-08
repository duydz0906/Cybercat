import discord
from discord.ext import commands
from utils.storage import load_queue, save_queue

queues = load_queue()

class Move(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="move", help="Di chuyển bài trong hàng đợi")
    async def move(self, ctx, from_pos: int, to_pos: int):
        guild_id = ctx.guild.id
        q = queues.get(guild_id, [])
        if not q:
            await ctx.send("Hàng đợi trống.")
            return

        if from_pos < 1 or from_pos > len(q) or to_pos < 1 or to_pos > len(q):
            await ctx.send("Vị trí không hợp lệ.")
            return

        song = q.pop(from_pos - 1)
        q.insert(to_pos - 1, song)
        save_queue(queues)
        await ctx.send(f"✅ Đã di chuyển [{song.title}]({song.url}) từ vị trí {from_pos} đến {to_pos}.")

async def setup(bot):
    await bot.add_cog(Move(bot))
