import discord
from discord.ext import commands
import re
from dotenv import load_dotenv
import os
from datetime import timedelta

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('SPAMER_BOT')
canal_registro_id = int(os.getenv('CANAL_REGISTRO_ID_SPAMER_BOT'))
canal_id_kick = int(os.getenv('CANAL_CLIPS_KICK_ID')) 
roles_a_excluir = list(map(int, os.getenv('ROLES_A_EXCLUIR').split(',')))

# Crear el cliente de Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Diccionario para rastrear suspensiones
suspensiones = {}

@bot.event
async def on_ready():
    print(f'{bot.user.name} está listo para proteger el servidor de spam.')

def es_clip_kick(message_content):
    return bool(re.search(r'https:\/\/kick\.com\/\w+\?clip=\w+', message_content, flags=re.IGNORECASE))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == canal_id_kick:
        if not es_clip_kick(message.content):
            await message.delete()  # Eliminar mensaje que no es un enlace de clip de Kick
            return

    if await es_spam(message):
        await manejar_spam(message.author)
        await message.delete()  # Eliminar mensaje de spam

    if await es_invitacion_discord(message):
        await manejar_invitacion_discord(message.author)
        await message.delete()  # Eliminar mensaje de invitación

    await bot.process_commands(message)

import re

async def es_spam(message):
    # Si el mensaje es muy largo
    if len(message.content) > 250:
        return True

    # Lista de acortadores de enlaces comunes (regex mejorada)
    shorteners = [
        r'(https?:\/\/)?(www\.)?(bit\.ly|goo\.gl|t\.co|tinyurl\.com|cutt\.ly|is\.gd|cli\.ck|shorte\.st|ultraurl\.com|ow\.ly)'
    ]
    if any(re.search(shortener, message.content) for shortener in shorteners):
        return True

    # Palabras o frases típicas de spam
    spam_keywords = ['gana dinero', 'oferta', 'descuento', 'gratis', 'click aquí', 'regístrate ahora']
    if any(keyword in message.content.lower() for keyword in spam_keywords):
        return True

    # Contar cuántos enlaces hay en el mensaje
    links = re.findall(r'(https?://[^\s]+)', message.content)
    if len(links) > 2:  # Si hay más de 2 enlaces en el mensaje
        return True

    # No permitir enlaces que contengan la palabra "gift"
    if any('gift' in link for link in links):
        return True

    return False


async def es_invitacion_discord(message):
    if re.search(r'discord\.gg\/\w+', message.content, flags=re.IGNORECASE):
        return True
    return False

async def manejar_spam(user):
    roles_usuario = [role.id for role in user.roles]
    if any(role_id in roles_a_excluir for role_id in roles_usuario):
        return

    user_id = user.id

    # Incrementar el conteo de suspensiones
    if user_id in suspensiones:
        suspensiones[user_id] += 1
    else:
        suspensiones[user_id] = 1

    # Verificar el conteo de suspensiones
    if suspensiones[user_id] >= 4:
        await user.ban(reason='Baneado después de 3 suspensiones por spam.')
        await user.send('Has sido baneado del servidor después de recibir 3 suspensiones por spam.')
        suspensiones.pop(user_id)  # Limpiar el conteo

        # Informar en el canal de registro
        canal_registro = bot.get_channel(canal_registro_id)
        if canal_registro:
            await canal_registro.send(f'Usuario {user.name}#{user.discriminator} ({user.id}) ha sido baneado por hacer spam repetido.')
    else:
        timeout_duration = timedelta(hours=1)
        await aplicar_timeout(user, timeout_duration)

async def manejar_invitacion_discord(user):
    roles_usuario = [role.id for role in user.roles]
    if any(role_id in roles_a_excluir for role_id in roles_usuario):
        return

    user_id = user.id

    # Incrementar el conteo de suspensiones
    if user_id in suspensiones:
        suspensiones[user_id] += 1
    else:
        suspensiones[user_id] = 1

    # Verificar el conteo de suspensiones
    if suspensiones[user_id] >= 4:
        await user.ban(reason='Baneado después de 3 suspensiones por invitaciones.')
        await user.send('Has sido baneado del servidor después de recibir 3 suspensiones por invitaciones a otros servidores.')
        suspensiones.pop(user_id)  # Limpiar el conteo

        # Informar en el canal de registro
        canal_registro = bot.get_channel(canal_registro_id)
        if canal_registro:
            await canal_registro.send(f'Usuario {user.name}#{user.discriminator} ({user.id}) ha sido baneado por enviar invitaciones repetidas.')
    else:
        timeout_duration = timedelta(minutes=30)
        await aplicar_timeout(user, timeout_duration)

async def aplicar_timeout(user, timeout_duration):
    canal_registro = bot.get_channel(canal_registro_id)

    if timeout_duration:
        # Aplicar timeout
        await user.edit(timed_out_until=discord.utils.utcnow() + timeout_duration)
        await user.send(f'Se te ha aplicado un timeout por {timeout_duration.total_seconds() // 60} minutos por enviar invitaciones a otros servidores de Discord o hacer spam en el servidor.')
        await limpiar_mensajes(user)

        if canal_registro:
            await canal_registro.send(f'Usuario {user.name}#{user.discriminator} ({user.id}) ha sido suspendido por {timeout_duration.total_seconds() // 60} minutos.')

    else:
        # Aplicar baneo
        await user.ban(reason='Spam repetido en el servidor.')
        await user.send('Has sido baneado del servidor por hacer spam repetido.')
        await limpiar_mensajes(user)

        if canal_registro:
            await canal_registro.send(f'Usuario {user.name}#{user.discriminator} ({user.id}) ha sido baneado por hacer spam repetido.')

async def limpiar_mensajes(user):
    for channel in user.guild.text_channels:
        async for message in channel.history(limit=100):
            if message.author == user:
                await message.delete()

# Ejecutar el bot
bot.run(TOKEN)
