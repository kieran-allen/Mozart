import discord
from os import getenv
from dotenv import load_dotenv

load_dotenv()
bot = discord.Bot()

DISCORD_BOT_TOKEN = getenv('DISCORD_BOT_TOKEN')


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

cogs_list = [
    'music_player',
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')


bot.run(DISCORD_BOT_TOKEN)
