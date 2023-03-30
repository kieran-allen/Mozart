# Mozart

This is a simple Discord music bot that can play music from YouTube and attempt to find a youtube video based on a spotify link. It uses the pycord library, yt-dlp, and Spotipy.
Features

* Play music from YouTube
* Play next song automatically when the current song ends
* Skip songs
* Stop playback and clear the queue

## Setup

### Bot setup in discord dev dashboard

scopes
* bot
* applications:commands

permissions
* Read Messages/View channels
* Send Messages
* Read Message History
* Connect
* Speak
* Use Voice Activity

Enable Message Content Intent



### Install ffmpeg
```bash
sudo apt update
sudo apt install ffmpeg
```

### Install required packages:
```bash
pip install py-cord spotipy yt-dlp
```

### Create a .env file in the project directory and add the following:

```plaintext
DISCORD_BOT_TOKEN=<your_discord_bot_token>
SPOTIFY_CLIENT_ID=<your_spotify_client_id>
SPOTIFY_CLIENT_SECRET=<your_spotify_client_secret>
```

Replace `<your_discord_bot_token>`, `<your_spotify_client_id>`, and `<your_spotify_client_secret>` with your actual tokens and credentials.

### Run the bot:

```bash
python main.py
```

### Usage
Invite the bot to your server and use the following slash commands:


`/play <query>: Play a song from YouTube or search Spotify. Example: /play https://www.youtube.com/watch?v=dQw4w9WgXcQ`

`/skip: Skip the current song`

`/stop: Stop playback and clear the queue`
