import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import logging
from utils.youtube import is_youtube_url, search_youtube
from utils.storage import load_queue, save_queue

logger = logging.getLogger(__name__)

queues_raw = load_queue()
queues = {}
playlist_cache = {}  # guild_id: (full_playlist_url, next_offset)

class Song:
    def __init__(self, url, title, duration):
        self.url = url
        self.title = title
        self.duration = duration

for gid, q in queues_raw.items():
    queues[int(gid)] = [Song(i["url"], i["title"], i["duration"]) for i in q]

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_song = {}
        self.volume = {}
        self.repeat = {}
        self.autoplay = {}
        self.playlist = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ]

    async def extract_playlist(self, url, limit=None, offset=0):
        ydl_opts = {
            "extract_flat": True,
            "playliststart": offset + 1,
            "playlistend": (offset + limit) if limit else None,
            "quiet": True,
            "skip_download": True,
            "format": "bestaudio"
        }
        songs = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if "_type" in info and info["_type"] == "playlist":
                entries = info.get("entries", [])
                for entry in entries:
                    songs.append(Song(f"https://www.youtube.com/watch?v={entry['id']}", entry["title"], entry.get("duration", 0)))
        return songs

    @commands.command(name="invite", help="Lấy link mời bot vào server khác")
    async def invite_cmd(self, ctx):
        invite_url = f"https://discord.com/oauth2/authorize?client_id=1392160510681813052"
        await ctx.send(f"🔗 [Nhấn vào đây để mời bot](<{invite_url}>)")

    @app_commands.command(name="invite", description="Lấy link mời bot vào server khác")
    async def invite(self, interaction: discord.Interaction):
        invite_url = f"https://discord.com/oauth2/authorize?client_id=881928974102577202&scope=bot+applications.commands&permissions=8"
        await interaction.response.send_message(
            f"🔗 [Nhấn vào đây để mời bot](<{invite_url}>)",
            ephemeral=True
        )

    async def play_song(self, interaction, song: Song):
        guild_id = interaction.guild.id
        vc = interaction.guild.voice_client
        if not vc:
            member = interaction.guild.get_member(interaction.user.id)
            if not member or not member.voice:
                await interaction.followup.send("🚫 Bạn chưa vào voice channel.")
                return
            channel = member.voice.channel
            vc = await channel.connect()

        vol = self.volume.get(guild_id, 1.0)
        with yt_dlp.YoutubeDL({"format": "bestaudio"}) as ydl:
            info = ydl.extract_info(song.url, download=False)
            audio_url = info["url"]

        source = discord.FFmpegPCMAudio(
            audio_url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options=f"-vn -filter:a volume={vol}"
        )
        def after_play(error):
            if error:
                logger.error(f"Playback error: {error}")
            fut = self.bot.loop.create_task(self.play_next(interaction))
            try:
                fut.result()
            except Exception as e:
                logger.error(f"Error in play_next: {e}")

        vc.play(source, after=after_play)
        self.current_song[guild_id] = song
        await interaction.followup.send(f"🎵 Now playing: **{song.title}**")

    async def play_next(self, interaction):
        guild_id = interaction.guild.id
        queue = queues.get(guild_id, [])
        if not queue:
            if guild_id in playlist_cache:
                url, offset = playlist_cache[guild_id]
                songs = await self.extract_playlist(url, limit=100, offset=offset)
                if songs:
                    queues[guild_id].extend(songs)
                    playlist_cache[guild_id] = (url, offset + 100)
                    save_queue(queues)
                    return await self.play_next(interaction)
            self.current_song[guild_id] = None
            vc = interaction.guild.voice_client
            if vc:
                await vc.disconnect()
            return
        next_song = queue.pop(0)
        save_queue(queues)
        await self.play_song(interaction, next_song)

    @commands.command(name="play", help="Phát nhạc từ YouTube")
    async def play_cmd(self, ctx, *, query: str):
        class FakeInteraction:
            def __init__(self, ctx):
                self.guild = ctx.guild
                self.user = ctx.author
                self.channel = ctx.channel
                self.guild_id = ctx.guild.id
                self.response = type("R", (), {"defer": lambda *_: None, "send_message": ctx.send})()
                self.followup = ctx
        await self.play(FakeInteraction(ctx), query)

    @app_commands.command(name="play", description="Phát nhạc từ YouTube")
    @app_commands.describe(query="YouTube link hoặc từ khoá")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        guild_id = interaction.guild.id
        try:
            if is_youtube_url(query):
                if "list=" in query:
                    songs = await self.extract_playlist(query, limit=100)
                    if not songs:
                        await interaction.followup.send("🚫 Không thể tải playlist.")
                        return
                    queues.setdefault(guild_id, []).extend(songs)
                    playlist_cache[guild_id] = (query, 100)
                    save_queue(queues)
                    if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
                        await self.play_next(interaction)
                    await interaction.followup.send(f"✅ Đã thêm {len(songs)} bài đầu từ playlist vào hàng đợi.")
                    return
                with yt_dlp.YoutubeDL({"format": "bestaudio"}) as ydl:
                    info = ydl.extract_info(query, download=False)
                    song = Song(query, info["title"], info.get("duration", 0))
                queues.setdefault(guild_id, []).append(song)
                save_queue(queues)
                if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
                    await self.play_next(interaction)
                else:
                    await interaction.followup.send(f"✅ Đã thêm vào hàng đợi: {song.title}")
                return
            results = search_youtube(query, max_results=5)
            if not results:
                await interaction.followup.send("🚫 Không tìm thấy kết quả.")
                return
            options = [
                discord.SelectOption(label=r["title"][:100], description=r["url"], value=r["url"])
                for r in results
            ]
            class SongSelect(discord.ui.Select):
                def __init__(self):
                    super().__init__(placeholder="Chọn bài để phát", options=options)
                async def callback(self2, interaction2: discord.Interaction):
                    await interaction2.response.defer(ephemeral=True)
                    try:
                        guild_id2 = interaction2.guild.id
                        with yt_dlp.YoutubeDL({"format": "bestaudio"}) as ydl:
                            info = ydl.extract_info(self2.values[0], download=False)
                            song = Song(self2.values[0], info["title"], info.get("duration", 0))
                        queues.setdefault(guild_id2, []).append(song)
                        save_queue(queues)
                        await interaction2.followup.send(f"✅ Đã thêm vào hàng đợi: {song.title}", ephemeral=True)
                        if not interaction2.guild.voice_client or not interaction2.guild.voice_client.is_playing():
                            await self.play_next(interaction2)
                    except Exception as e:
                        logger.error(f"Lỗi trong callback select: {e}")
                        await interaction2.followup.send("Đã xảy ra lỗi!", ephemeral=True)
            class SongSelectView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=30)
                    self.add_item(SongSelect())
                async def on_timeout(self):
                    for child in self.children:
                        child.disabled = True
            view = SongSelectView()
            await interaction.followup.send("🎵 Hãy chọn bài:", view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"Lỗi trong command /play: {e}")
            try:
                await interaction.followup.send("Đã xảy ra lỗi khi xử lý lệnh!", ephemeral=True)
            except Exception:
                pass

    @commands.command(name="saveplaylist", help="Lưu toàn bộ playlist vào hàng đợi")
    async def saveplaylist_cmd(self, ctx, *, url: str):
        class FakeInteraction:
            def __init__(self, ctx):
                self.guild = ctx.guild
                self.user = ctx.author
                self.channel = ctx.channel
                self.guild_id = ctx.guild.id
                self.response = type("R", (), {"defer": lambda *_: None, "send_message": ctx.send})()
                self.followup = ctx
        await self.saveplaylist(FakeInteraction(ctx), url)

    @app_commands.command(name="saveplaylist", description="Lưu toàn bộ playlist vào hàng đợi")
    @app_commands.describe(url="Link playlist YouTube")
    async def saveplaylist(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()
        guild_id = interaction.guild.id
        try:
            if "list=" not in url:
                await interaction.followup.send("🚫 URL không phải playlist YouTube.")
                return
            songs = await self.extract_playlist(url)
            if not songs:
                await interaction.followup.send("🚫 Playlist rỗng hoặc lỗi khi tải.")
                return
            queues.setdefault(guild_id, []).extend(songs)
            save_queue(queues)
            await interaction.followup.send(f"✅ Đã lưu playlist với {len(songs)} bài vào hàng đợi.")
        except Exception as e:
            logger.error(f"Lỗi trong /saveplaylist: {e}")
            await interaction.followup.send("Đã xảy ra lỗi khi lưu playlist.")

async def setup(bot):
    await bot.add_cog(Music(bot))
