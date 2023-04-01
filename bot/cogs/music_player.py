import discord
import asyncio
from discord.ext import commands
from guild_queue import GuildQueueManager
from utils import get_youtube_info


class MusicPlayer(commands.Cog, guild_ids=[1032673718914273310]):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}

    async def connect_to_voice(self, ctx):
            if ctx.author.voice is None:
                await ctx.send("You are not connected to a voice channel.")
                return None

            voice_channel = ctx.author.voice.channel

            if ctx.guild.voice_client is None:
                voice_client = await voice_channel.connect()
            else:
                voice_client = ctx.guild.voice_client
                if voice_client.channel != voice_channel:
                    await voice_client.move_to(voice_channel)

            return voice_client

    async def play_next_in_queue(self, ctx, voice_client):
        guild_id = ctx.guild.id
        guild_queue = GuildQueueManager.get_guild_queue(guild_id)

        if guild_queue.is_empty():
            await voice_client.disconnect()
            return

        next_song = guild_queue.pop_front()

        url = next_song['audio_url']
        audio_source = discord.FFmpegPCMAudio(url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")

        def after_playing(err):
            if err:
                print(f"Error occurred while playing audio: {err}")
            asyncio.run_coroutine_threadsafe(self.play_next_in_queue(ctx, voice_client), self.bot.loop)

        voice_client.play(audio_source, after=after_playing)

    @discord.slash_command()
    async def play(self, ctx, url):
        """
        Command to start playing a song.
        """
        guild_id = ctx.guild.id
        guild_queue = GuildQueueManager.get_guild_queue(guild_id)
        info = await get_youtube_info(url)


        if info == None:
            await ctx.send_response(content=f"Unable to find youtube data for `{url}`", delete_after=10, ephemeral=True)
            return
        
        voice_client = await self.connect_to_voice(ctx)

        if not guild_queue.is_empty():
            guild_queue.push_front(info)
        else:
            guild_queue.push_back(info)

        await self.play_next_in_queue(ctx, voice_client)

        embed = discord.Embed(
            title=info['title'],
            url=info['url'],
        )
        embed.set_author(name="play")
        await ctx.send_response(embed=embed, delete_after=10, ephemeral=True)

    @discord.slash_command()
    async def pause(self, ctx):
        """
        Command to pause the currently playing song.
        """

        await ctx.respond('Audio paused.', delete_after=10, ephemeral=True)

    @discord.slash_command()
    async def stop(self, ctx):
        """
        Command to stop playing and clear the playlist.
        """
        guild_id = ctx.guild.id
        guild_queue = GuildQueueManager.get_guild_queue(guild_id)
        guild_queue.clear()
        await ctx.respond("The playlist has been cleared.", delete_after=10, ephemeral=True)

    @discord.slash_command()
    async def skip(self, ctx):
        """
        Command to skip to the next song in the queue.
        """
        guild_id = ctx.guild.id
        guild_queue = GuildQueueManager.get_guild_queue(guild_id)

        if not guild_queue.is_empty():
            next_song = guild_queue.pop_front()
            embed = discord.Embed(
                title=next_song['title'],
                url=next_song['url'],
            )
            embed.set_author(name="skip")
            await ctx.send_response(embed=embed, delete_after=10, ephemeral=True)
        else:
            await ctx.respond("There are no more songs in the queue to skip.", delete_after=10, ephemeral=True)

    @discord.slash_command()
    async def add(self, ctx, url):
        """
        Command to add a song to the end of the queue.
        """
        guild_id = ctx.guild.id
        guild_queue = GuildQueueManager.get_guild_queue(guild_id)

        if guild_queue.is_empty():
            await self.play(ctx, url)
            return
        info = await get_youtube_info(url)

        if info == None:
            await ctx.send_response(content=f"Unable to find youtube data for `{url}`", delete_after=10, ephemeral=True)
            return

        guild_queue.push_back(info)

        embed = discord.Embed(
            title=info['title'],
            url=info['url'],
        )
        embed.set_author(name="add")
        await ctx.send_response(embed=embed, delete_after=10, ephemeral=True)


def setup(bot):
    bot.add_cog(MusicPlayer(bot))
