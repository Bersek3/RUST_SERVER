import discord
import googleapiclient.discovery
import asyncio
import datetime
import os
import sqlite3
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('ANUNCIOS_BOT')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID_BOT_ANUNCIOS'))
YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID')  # Reemplaza esto con el ID de tu canal de YouTube
DB_PATH = 'bots/db/data.db'  # Ruta actualizada a la base de datos

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def get_last_checked_time():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp FROM last_checked ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else '1970-01-01T00:00:00Z'

def set_last_checked_time(timestamp):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO last_checked (timestamp) VALUES (?)', (timestamp,))
    conn.commit()
    conn.close()

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

    channel = client.get_channel(DISCORD_CHANNEL_ID)
    
    for video in new_videos:
        try:
            video_title = video['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
            await channel.send(f"Nuevo video: {video_title}\n{video_url}")
        except KeyError:
            print(f"Error: No se encontró 'videoId' en el resultado del video: {video}")
    
    for stream in live_streams:
        try:
            stream_title = stream['snippet']['title']
            stream_url = f"https://www.youtube.com/watch?v={stream['id']['videoId']}"
            await channel.send(f"Nuevo directo: {stream_title}\n{stream_url}")
        except KeyError:
            print(f"Error: No se encontró 'videoId' en el resultado del directo: {stream}")
    
    for short in new_shorts:
        try:
            short_title = short['snippet']['title']
            short_url = f"https://www.youtube.com/watch?v={short['id']['videoId']}"
            await channel.send(f"Nuevo short: {short_title}\n{short_url}")
        except KeyError:
            print(f"Error: No se encontró 'videoId' en el resultado del short: {short}")

    # Actualizar el tiempo de la última comprobación
    new_last_checked = datetime.datetime.utcnow().isoformat() + 'Z'
    set_last_checked_time(new_last_checked)

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    await asyncio.sleep(120)  # Esperar 2 minutos (120 segundos)
    await check_for_new_videos_and_streams_and_shorts()  # Realizar la primera comprobación
    while True:
        await asyncio.sleep(300)  # Espera 5 minutos entre comprobaciones
        await check_for_new_videos_and_streams_and_shorts()

client.run(TOKEN)
