import yt_dlp
import json
import discord
import re


def is_valid_youtube_url(url):
    # Define a regular expression to match the standard YouTube URL format
    pattern = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]+)"
    # Use the re.match function to check if the URL matches the pattern
    match = re.match(pattern, url)
    # Return True if the URL matches the pattern, False otherwise
    return match is not None


async def get_youtube_info(url):
    """
    Extract information from a YouTube video or playlist URL.
    Returns a dictionary of video information, or None if the URL is invalid or an error occurs.
    """
    if not is_valid_youtube_url(url):
        return None

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            sanitized = ydl.sanitize_info(info)
            title = info['title']
            url = info['webpage_url']
            audio_url = info['url']
            return {"title": title, "url": url, "audio_url": audio_url}
    except (yt_dlp.utils.DownloadError, yt_dlp.utils.ExtractorError):
        return None


async def stream_audio(voice_client, url):
    source = discord.FFmpegPCMAudio(url)
    voice_client.play(source)
