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
usuarios_prohibidos_ids = [
    330852263566376961, 982920110727634974, 1229658877365190726
]

# Lista de roles exentos
roles_exentos_ids = [
    805654387208224818, 1131060481088561254, 838553391218425959, 1273863280858759190
]

@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} está listo para proteger el servidor de menciones prohibidas.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Verificar si el mensaje contiene una mención prohibida y si el autor no tiene un rol exento
    if await contiene_mencion_prohibida(message):
        await message.delete()  # Eliminar mensaje
        return

    await bot.process_commands(message)

async def contiene_mencion_prohibida(message):
    """ Verifica si el mensaje contiene una mención directa a los usuarios prohibidos 
        y si el autor no tiene un rol exento """

    # Verificar si el autor tiene un rol exento
    if any(role.id in roles_exentos_ids for role in message.author.roles):
        return False

    # Verificar si el mensaje es una respuesta
    if message.reference:
        # Si el mensaje referenciado es de un usuario prohibido, permitir la respuesta
        referenced_message = await message.channel.fetch_message(message.reference.message_id)
        if referenced_message.author.id in usuarios_prohibidos_ids:
            return False  # No eliminar la respuesta

    # Verificar si el mensaje contiene menciones directas a usuarios prohibidos
    if any(member.id in usuarios_prohibidos_ids for member in message.mentions):
        return True  # Eliminar mensaje si contiene menciones directas

    return False

# Ejecutar el bot
bot.run(TOKEN)
