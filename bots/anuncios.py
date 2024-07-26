import discord
from discord.ext import commands, tasks
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('ANUNCIOS_BOT')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID_BOT_ANUNCIOS'))

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)
notified_streams = set()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('Successfully connected to Discord!')
    check_scheduled_streams.start()

@tasks.loop(minutes=1)
async def check_scheduled_streams():
    try:
        print("Checking for scheduled streams...")
        upcoming_streams, live_streams = get_scheduled_streams()
        print(f"Upcoming streams: {upcoming_streams}")
        print(f"Live streams: {live_streams}")
        
        for stream_id, stream_title, stream_start_time, stream_url in upcoming_streams:
            if stream_id not in notified_streams:
                await announce_upcoming_stream(stream_title, stream_start_time, stream_url)
                notified_streams.add(stream_id)
        
        for stream_id, stream_title, stream_url in live_streams:
            if stream_id not in notified_streams:
                await announce_live_stream(stream_title, stream_url)
                notified_streams.add(stream_id)
    
    except Exception as e:
        print(f'Error checking scheduled streams: {type(e).__name__}: {e}')

def get_scheduled_streams():
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    # Obtener próximos directos
    request_upcoming = youtube.search().list(
        part='snippet',
        channelId='UCUskWGVf9SCdcp0HGpTKUxw',
        eventType='upcoming',
        type='video',
        maxResults=5
    )
    response_upcoming = request_upcoming.execute()
    upcoming_streams = parse_search_response(response_upcoming)
    
    # Obtener directos en vivo
    request_live = youtube.search().list(
        part='snippet',
        channelId='UCUskWGVf9SCdcp0HGpTKUxw',
        eventType='live',
        type='video',
        maxResults=5
    )
    response_live = request_live.execute()
    live_streams = parse_search_response(response_live)
    
    return upcoming_streams, live_streams

def parse_search_response(response):
    streams = []
    for item in response.get('items', []):
        stream_id = item['id']['videoId']
        stream_title = item['snippet']['title']
        stream_start_time = datetime.fromisoformat(item['snippet']['publishTime'].replace('Z', '+00:00')).replace(tzinfo=None)
        stream_url = f"https://www.youtube.com/watch?v={stream_id}"
        streams.append((stream_id, stream_title, stream_start_time, stream_url))
    return streams

async def announce_upcoming_stream(stream_title, stream_start_time, stream_url):
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        print(f'Error: Discord channel with ID {DISCORD_CHANNEL_ID} not found.')
        return
    
    chile_tz = pytz.timezone('America/Santiago')
    chile_time = stream_start_time.astimezone(chile_tz)
    
    embed = discord.Embed(
        title=f"Nuevo directo programado en YouTube: {stream_title}",
        description=f"El directo comenzará a las {chile_time.strftime('%H:%M')} hora de Chile (UTC-3)",
        color=discord.Color.red()
    )
    embed.add_field(name="Ver en YouTube", value=stream_url)
    
    try:
        await channel.send(embed=embed)
        print(f'Stream announcement sent for: {stream_title}')
    except discord.HTTPException as e:
        print(f'Error sending announcement for {stream_title}: {e}')

async def announce_live_stream(stream_title, stream_url):
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        print(f'Error: Discord channel with ID {DISCORD_CHANNEL_ID} not found.')
        return
    
    embed = discord.Embed(
        title=f"¡El directo ha comenzado en YouTube!: {stream_title}",
        description=f"No te lo pierdas en YouTube: {stream_url}",
        color=discord.Color.green()
    )
    
    try:
        await channel.send(embed=embed)
        print(f'Live stream announcement sent for: {stream_title}')
    except discord.HTTPException as e:
        print(f'Error sending live announcement for {stream_title}: {e}')

# Start the bot
bot.run(TOKEN)
