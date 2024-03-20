import asyncio

import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL


# ------------------------ COGS ------------------------ #

class MusicYouTube(commands.Cog, name="musicyoutube"):
    def __init__(self, bot):
        self.bot = bot

        # ------------------------ COGS ------------------------ #

        # Variables liées à la musique
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []  # Liste contenant [chanson, channel]
        self.YDL_OPTIONS = {'format': 'bestaudio/best'}
        self.FFMPEG_OPTIONS = {'options': '-vn'}
        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)

    # Recherche sur YouTube
    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return {'source': item, 'title': title}
        search = VideosSearch(item, limit=1)
        return {'source': search.result()["result"][0]["link"], 'title': search.result()["result"][0]["title"]}

    # Lecture de la prochaine chanson dans la file d'attente
    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS),
                         after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    # Lecture de la musique
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
                if self.vc is None:
                    await ctx.send("```Impossible de se connecter au canal vocal```")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
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
        """
        Commande pour jouer une chanson depuis YouTube.

        Args:
            args (str): Mots-clés pour rechercher la chanson sur YouTube.

        Exemple:
            !play <mots-clés>
        """
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
                await ctx.send(
                    "```Impossible de télécharger la chanson. Format incorrect. Essayez un autre mot-clé.```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue) + 2} - '{song['title']}'** ajouté à la file d'attente")
                else:
                    await ctx.send(f"**'{song['title']}'** ajouté à la file d'attente")
                self.music_queue.append([song, voice_channel])
                if not self.is_playing:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Met en pause la chanson actuellement en cours de lecture")
    async def pause(self, ctx, *args):
        """
        Commande pour mettre en pause la chanson actuellement en cours de lecture.
        """
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="resume", aliases=["r"], help="Reprend la lecture avec le bot Discord")
    async def resume(self, ctx, *args):
        """
        Commande pour reprendre la lecture avec le bot Discord.
        """
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Passe à la chanson suivante")
    async def skip(self, ctx):
        """
        Commande pour passer à la chanson suivante dans la file d'attente.
        """
        if self.vc != None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)

    @commands.command(name="queue", aliases=["q"], help="Affiche les chansons actuellement dans la file d'attente")
    async def queue(self, ctx):
        """
        Commande pour afficher les chansons actuellement dans la file d'attente.
        """
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f"#{i + 1} -" + self.music_queue[i][0]['title'] + "\n"
        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No music in queue```")

    @commands.command(name="clearqueue", aliases=["c", "bin"], help="Arrête la musique et efface la file d'attente")
    async def clear(self, ctx):
        """
        Commande pour arrêter la musique et effacer la file d'attente.
        """
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("```Music queue cleared```")

    @commands.command(name="stop", aliases=["disconnect", "l", "d"], help="Expulse le bot du VC")
    async def dc(self, ctx):
        """
        Commande pour expulser le bot du canal vocal.
        """
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    @commands.command(name="remove", help="Supprime la dernière chanson ajoutée à la file d'attente")
    async def remove(self, ctx):
        """
        Commande pour supprimer la dernière chanson ajoutée à la file d'attente.
        """
        self.music_queue.pop()
        await ctx.send("```La dernière chanson a été supprimée de la file d'attente```")


async def setup(bot) -> None:
    await bot.add_cog(MusicYouTube(bot))
