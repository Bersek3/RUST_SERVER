import discord
import googleapiclient.discovery
import asyncio
import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('ANUNCIOS_BOT')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID_BOT_ANUNCIOS'))
YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID')  # Reemplaza esto con el ID de tu canal de YouTube
LAST_CHECKED_FILE = 'last_checked.txt'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def get_last_checked_time():
    try:
        with open(LAST_CHECKED_FILE, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return '1970-01-01T00:00:00Z'

def set_last_checked_time(time):
    with open(LAST_CHECKED_FILE, 'w') as file:
        file.write(time)

async def check_for_new_videos_and_streams_and_shorts():
    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    last_checked = get_last_checked_time()
    
    # Consulta para videos nuevos
    video_request = youtube.search().list(
        part='snippet',
        channelId=YOUTUBE_CHANNEL_ID,
        order='date',
        publishedAfter=last_checked,
        maxResults=5
    )
    try:
        video_response = video_request.execute()
    except googleapiclient.errors.HttpError as e:
        print(f'Error en la consulta de videos: {e}')
        return
    
    # Consulta para eventos en directo
    stream_request = youtube.search().list(
        part='snippet',
        channelId=YOUTUBE_CHANNEL_ID,
        eventType='live',
        type='video',
        publishedAfter=last_checked,
        maxResults=5
    )
    try:
        stream_response = stream_request.execute()
    except googleapiclient.errors.HttpError as e:
        print(f'Error en la consulta de directos: {e}')
        return

    # Consulta para shorts nuevos
    short_request = youtube.search().list(
        part='snippet',
        channelId=YOUTUBE_CHANNEL_ID,
        order='date',
        publishedAfter=last_checked,
        maxResults=5
    )
    try:
        short_response = short_request.execute()
    except googleapiclient.errors.HttpError as e:
        print(f'Error en la consulta de shorts: {e}')
        return
    
    new_videos = video_response.get('items', [])
    live_streams = stream_response.get('items', [])
    new_shorts = [item for item in short_response.get('items', []) if 'shorts' in item['snippet']['title'].lower()]

    if new_videos:
        last_checked_time = new_videos[0]['snippet']['publishedAt']
        set_last_checked_time(last_checked_time)
        
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        for video in new_videos:
            video_title = video['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
            await channel.send(f"Nuevo video: {video_title}\n{video_url}")
    
    if live_streams:
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        for stream in live_streams:
            stream_title = stream['snippet']['title']
            stream_url = f"https://www.youtube.com/watch?v={stream['id']['videoId']}"
            stream_start_time = stream['snippet']['publishedAt']
            stream_start_time_formatted = datetime.datetime.strptime(stream_start_time, '%Y-%m-%dT%H:%M:%SZ').strftime('%d de %B de %Y a las %H:%M')
            await channel.send(f"📅 **Nuevo directo programado**\n\nTítulo: {stream_title}\n📅 Fecha y Hora de Inicio: {stream_start_time_formatted}\n🔗 [Enlace al Directo]({stream_url})\n\n¡No te lo pierdas!")
    
    if new_shorts:
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        for short in new_shorts:
            short_title = short['snippet']['title']
            short_url = f"https://www.youtube.com/watch?v={short['id']['videoId']}"
            await channel.send(f"Nuevo short: {short_title}\n{short_url}")

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    while True:
        await check_for_new_videos_and_streams_and_shorts()
        await asyncio.sleep(300)  # Espera 5 minutos

client.run(TOKEN)
