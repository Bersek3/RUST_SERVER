import discord
from discord.ext import commands
import asyncio
from datetime import timedelta
import re
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('SPAMER_BOT')
canal_registro_id = int(os.getenv('CANAL_REGISTRO_ID_SPAMER_BOT'))
roles_a_excluir = list(map(int, os.getenv('ROLES_A_EXCLUIR').split(',')))

# Crear el cliente de Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Evento para cuando el bot está listo
@bot.event
async def on_ready():
    print(f'{bot.user.name} está listo para proteger el servidor de spam.')

# Función para verificar si el usuario ha sido suspendido anteriormente por spam
async def es_spammer_anterior(user):
    banned_users = [ban_entry async for ban_entry in user.guild.bans()]
    return any(ban.user.id == user.id for ban in banned_users)

# Función para limpiar mensajes del usuario (opcional, según políticas del servidor)
async def limpiar_mensajes(user):
    for channel in user.guild.text_channels:
        async for message in channel.history(limit=100):
            if message.author == user:
                await message.delete()

# Evento para manejar mensajes y detectar spam e invitaciones
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if await es_spam(message):
        await manejar_spam(message.author)
    
    if await es_invitacion_discord(message):
        await manejar_invitacion_discord(message.author)

    await bot.process_commands(message)

# Función para detectar spam
async def es_spam(message):
    if len(message.content) > 250:
        return True
    
    shorteners = [
        r'bit\.ly', r'goo\.gl', r't\.co', r'tinyurl\.com', r'cutt\.ly', 
        r'is\.gd', r'cli\.ck', r'shorte\.st', r'ultraurl\.com', r'ow\.ly'
    ]
    if any(re.search(shortener, message.content) for shortener in shorteners):
        return True
    
    return False

# Función para detectar invitaciones a otros servidores de Discord
async def es_invitacion_discord(message):
    if re.search(r'discord\.gg\/\w+', message.content, flags=re.IGNORECASE):
        return True
    return False

# Función para manejar acciones contra usuarios que hacen spam
async def manejar_spam(user):
    roles_usuario = [role.id for role in user.roles]
    if any(role_id in roles_a_excluir for role_id in roles_usuario):
        return
     
    if not await es_spammer_anterior(user):
        timeout_duration = timedelta(hours=1)
    else:
        timeout_duration = None
     
    await aplicar_timeout(user, timeout_duration)

# Función para manejar acciones contra usuarios que hacen invitaciones a otros servidores de Discord
async def manejar_invitacion_discord(user):
    roles_usuario = [role.id for role in user.roles]
    if any(role_id in roles_a_excluir for role_id in roles_usuario):
        return
     
    timeout_duration = timedelta(minutes=30)
    await aplicar_timeout(user, timeout_duration)

# Función genérica para aplicar timeout temporal a un usuario
async def aplicar_timeout(user, timeout_duration):
    if timeout_duration:
        await user.edit(timed_out_until=discord.utils.utcnow() + timeout_duration)
        await user.send(f'Se te ha aplicado un timeout por {timeout_duration.total_seconds() // 60} minutos por enviar invitaciones a otros servidores de Discord o hacer spam en el servidor.')
        await limpiar_mensajes(user)
        
        canal_registro = bot.get_channel(canal_registro_id)
        if canal_registro:
            await canal_registro.send(f'Usuario {user.name}#{user.discriminator} ({user.id}) ha sido suspendido por {timeout_duration.total_seconds() // 60} minutos.')

    else:
        await user.ban(reason='Spam repetido en el servidor.')
        await user.send(f'Has sido baneado del servidor por hacer spam repetido.')
        await limpiar_mensajes(user)
        
        canal_registro = bot.get_channel(canal_registro_id)
        if canal_registro:
            await canal_registro.send(f'Usuario {user.name}#{user.discriminator} ({user.id}) ha sido baneado por hacer spam repetido.')

# Ejecutar el bot
bot.run(TOKEN)
