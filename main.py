import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv
from collections import deque

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

spotify_credentials = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
spotify_client = spotipy.Spotify(
    client_credentials_manager=spotify_credentials)

intents = discord.Intents.default()
bot = commands.Bot(intents=intents)

queues = {}


def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = deque()
    return queues[guild_id]


YDL_OPTS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}


def search_spotify_and_get_youtube_url(query):
    results = spotify_client.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_name = track['name']
        track_artist = track['artists'][0]['name']
        search_query = f"{track_name} {track_artist}"

        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
            if 'entries' in info:
                video = info['entries'][0]
                return video['webpage_url']

    return None


async def spotify_track_to_query(spotify_track, ctx):
    if 'spotify.com' in spotify_track:
        track_id = spotify_track.split('/')[-1].split('?')[0]
        spotify_track = f'spotify:track:{track_id}'

    if spotify_track.startswith('spotify:track:'):
        track = spotify_client.track(spotify_track)
        track_name = track['name']
        track_artist = track['artists'][0]['name']
        await ctx.respond(f'Now playing: {track_name} {track_artist}')
        return f'{track_name} {track_artist}'

    return None


def get_audio_stream_url(video_url):
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(video_url, download=False)
        audio_url = None
        for format in info['formats']:
            if format['acodec'] != 'none':
                audio_url = format['url']
                break
        return audio_url


async def play_next(ctx):
    if not queues[ctx.guild.id]:
        return

    url = queues[ctx.guild.id].popleft()
    audio_url = get_audio_stream_url(url)
    if audio_url is None:
        await ctx.respond("No audio stream found for this video.")
        return

    def next_song(error=None):
        coro = play_next(ctx)
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            fut.result()
        except Exception as e:
            print(f'Error in play_next coroutine: {e}')

    ctx.voice_client.play(discord.FFmpegPCMAudio(
        audio_url, **FFMPEG_OPTIONS), after=next_song)

    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info['title']
        await ctx.respond(f'Now playing: {title}')
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=title))


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.unknown, name="Composing..."))


@bot.slash_command(name="play", description="Play a song from YouTube, SoundCloud, or search Spotify")
async def play(ctx, query):
    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)

    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = deque()

    if query.startswith('spotify:') or 'spotify.com' in query:
        search_query = await spotify_track_to_query(query, ctx)
        if search_query is None:
            await ctx.respond("Invalid Spotify track.")
            return
        url = search_spotify_and_get_youtube_url(search_query)
    else:
        url = query

    if url is None:
        await ctx.respond("No search results found.")
        return

    queues[ctx.guild.id].append(url)

    if not ctx.voice_client.is_playing():
        await play_next(ctx)


@bot.slash_command(name="skip", description="Skip the current song")
async def skip(ctx):
    queue = get_queue(ctx.guild.id)
    if ctx.voice_client.is_playing():
        if len(queue) > 0:
            ctx.voice_client.stop()
            await play_next(ctx)
            await ctx.respond(f'Skipping to the next song')
        else:
            await ctx.respond(f"There's nothing to skip. Try /stop if you want to stop the stream")
    else:
        await ctx.respond(f'Nothing to skip')


@bot.slash_command(name="stop", description="Stop playback and clear the queue")
async def stop(ctx):
    if ctx.voice_client is not None:
        queues[ctx.guild.id] = deque()
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.respond(f'Mozart is shutting down...')
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.unknown, name='Composing...'))


# Start the bot
bot.run(DISCORD_BOT_TOKEN)
