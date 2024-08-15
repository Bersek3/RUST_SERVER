import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('CAROBOT')

# Crear el cliente de Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Lista de usuarios que no pueden ser mencionados
usuarios_prohibidos = ['caro', 'carolinyaa', 'FreeBot music', 'FreeBot Music#2308']

@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} está listo para proteger el servidor de menciones prohibidas.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Verificar si se ha mencionado a los usuarios prohibidos
    if await contiene_mencion_prohibida(message):
        await message.delete()  # Eliminar mensaje
        return

    await bot.process_commands(message)

async def contiene_mencion_prohibida(message):
    """ Verifica si el mensaje contiene una mención a los usuarios prohibidos """
    for member in message.mentions:
        if member.name.lower() in usuarios_prohibidos:
            return True
    return False

# Ejecutar el bot
bot.run(TOKEN)