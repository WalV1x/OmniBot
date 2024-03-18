import discord
from discord.ext import commands
from ast import alias
import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import asyncio

class MusicYouTube(commands.Cog, name="musicyoutube"):
    def __init__(self, bot):
        self.bot = bot

        #all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best'}
        self.FFMPEG_OPTIONS = {'options': '-vn'}

        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)

    #searching the item on youtube
    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return {'source': item, 'title': title}
        search = VideosSearch(item, limit=1)
        return {'source': search.result()["result"][0]["link"], 'title': search.result()["result"][0]["title"]}


    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # Obtenir le premier URL
            m_url = self.music_queue[0][0]['source']

            # Retirer le premier élément car vous le jouez actuellement
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS),
                         after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            # Essayez de vous connecter au canal vocal si vous n'êtes pas déjà connecté
            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                # En cas d'échec de la connexion
                if self.vc is None:
                    await ctx.send("```Impossible de se connecter au canal vocal```")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            # Retirer le premier élément car vous le jouez actuellement
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS),
                         after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))

        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p", "playing"], help="Joue une chanson sélectionnée depuis YouTube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send("```Vous devez d'abord vous connecter à un canal vocal!```")
            return
        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if isinstance(song, bool):
                await ctx.send("```Impossible de télécharger la chanson. Format incorrect. Essayez un autre mot-clé.```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue) + 2} - '{song['title']}'** ajouté à la file d'attente")
                else:
                    await ctx.send(f"**'{song['title']}'** ajouté à la file d'attente")
                self.music_queue.append([song, voice_channel])
                if not self.is_playing:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name = "resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music(ctx)


    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f"#{i+1} -" + self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No music in queue```")

    @commands.command(name="clearqueue", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("```Music queue cleared```")

    @commands.command(name="stop", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    @commands.command(name="remove", help="Removes last song added to queue")
    async def re(self, ctx):
        self.music_queue.pop()
        await ctx.send("```last song removed```")

async def setup(bot) -> None:
    await bot.add_cog(MusicYouTube(bot))