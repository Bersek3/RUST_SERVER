import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener el token y el canal ID del archivo .env
TOKEN = os.getenv('BOT_PRINCIPAL')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID_BOT_PRINCIPAL'))
MESSAGE_ID_PLATAFORMA = int(os.getenv('MESSAGE_ID_PLATAFORMA'))
MESSAGE_ID_REGION = int(os.getenv('MESSAGE_ID_REGION'))

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Diccionario de colores y roles
color_roles = {
    'ROJO': 'ID_DEL_ROL_ROJO',
    'AZUL': 'ID_DEL_ROL_AZUL',
    'AMARILLO': 'ID_DEL_ROL_AMARILLO',
    'NARANJA': 'ID_DEL_ROL_NARANJA',
    'VERDE': 'ID_DEL_ROL_VERDE',
    'MORADO': 'ID_DEL_ROL_MORADO',
    'ROSA': 'ID_DEL_ROL_ROSA',
    'MARRON': 'ID_DEL_ROL_MARRON',
    'GRIS': 'ID_DEL_ROL_GRIS',
    'BLANCO': 'ID_DEL_ROL_BLANCO'
}


roles = {
    '<:PC:1263359013861458044>': '1263360911779827726',         # Emoji: <:PC:1263359013861458044>, Role: PC
    '<:PLAYSTATION:1263359018769059871>': '1263360763721027595',  # Emoji: <:PlayStation:1263359018769059871>, Role: PlayStation
    '<:XBOX:1263359017296592969>': '1263360685073498193',         # Emoji: <:Xbox:1263359017296592969>, Role: Xbox
    '<:SWITCH:1263359020207439942>': '1263360831073026158'        # Emoji: <:Switch:1263359020207439942>, Role: Nintendo
}

region_roles = {
    '🍔': '1263376862931980409',  # Norteamérica
    '🫔': '1263376953885589597',  # América Central
    '🍕': '1263377048307634249',  # Sudamérica
    '🍜': '1263377116666269788',  # Europa
    '🦁': '1263377241203675157',  # África
    '🐫': '1263377288309768274',  # Medio Oriente
    '🍣': '1263377342613422110',  # Asia
    '🐨': '1263377372334395476'   # Oceanía
}

class ColorButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Evitar que los botones expiren

        # Crear un botón para cada color en el diccionario
        for color in color_roles.keys():
            self.add_item(Button(label=color, style=discord.ButtonStyle.primary, custom_id=color))

    @discord.ui.button(label="ROJO", style=discord.ButtonStyle.primary)
    async def assign_role(self, interaction: discord.Interaction, button: Button):
        # Obtener el rol a partir del botón presionado
        role_id = color_roles[button.label]
        role = interaction.guild.get_role(int(role_id))
        member = interaction.user

        # Quitar otros roles de color si ya tienen uno
        for color in color_roles.values():
            role_to_remove = interaction.guild.get_role(int(color))
            if role_to_remove in member.roles:
                await member.remove_roles(role_to_remove)

        # Asignar el nuevo rol
        await member.add_roles(role)
        await interaction.response.send_message(f"Se te ha asignado el color {button.label}!", ephemeral=True

# Command !redes

@bot.command(name='redes')
async def redes(ctx):
    embed = discord.Embed(
        title="REDES SOCIALES DE CAOZ",
        color=0x6A0DAD  # Purple color
    )
    embed.add_field(name="", value="<:TWITCH:1266623059662733363> [Twitch](https://www.twitch.tv/caozssj)", inline=False)
    embed.add_field(name="", value="<:FACEBOOK:1266623057645015082> [Facebook](https://www.facebook.com/caozyt)", inline=False)
    embed.add_field(name="", value="<:X:1266686402003730523> [Twitter](https://x.com/CAOZYUTU)", inline=False)
    embed.add_field(name="", value="<:INSTAGRAM:1266623062929969247> [Instagram](https://www.instagram.com/caozyt/)", inline=False)
    embed.add_field(name="", value="<:YOUTUBE:1266623064347775027> [YouTube](https://www.youtube.com/@CAOZ)", inline=False)
    embed.add_field(name="", value="<:kick:1266624736226578532> [Kick](https://kick.com/caoz)", inline=False)
    embed.add_field(name="", value="<:TIKTOK:1266693677791707177> [Tiktok](https://www.tiktok.com/@caozyt)", inline=False)
    embed.set_footer(text="¡No olvides darle follow!")

    # Set the image URL with the desired image
    embed.set_image(url="https://i.imgur.com/hLaagec.jpeg")

    await ctx.send(embed=embed)

# Command !plataforma
@bot.command(name='plataforma')
async def plataforma(ctx):
    embed = discord.Embed(description=
        "Reacciona con el emote correspondiente para obtener el rol:\n\n"
        "<:PC:1263359013861458044> - PC\n"
        "<:PLAYSTATION:1263359018769059871> - PlayStation\n"
        "<:XBOX:1263359017296592969> - Xbox\n"
        "<:SWITCH:1263359020207439942> - Nintendo",
        color=0x6A0DAD  # Purple color
    )
    message = await ctx.send(embed=embed)

    for emoji in roles.keys():
        await message.add_reaction(emoji)

    # Save the message ID to a global variable for use in on_raw_reaction_add and on_raw_reaction_remove
    MESSAGE_ID_PLATAFORMA = message.id
    print(f'Sent !plataforma message with ID: {MESSAGE_ID_PLATAFORMA}')

# Comando para mostrar los botones de colores
@bot.command(name='colores')
async def colores(ctx):
    embed = discord.Embed(
        title="COLORES NORMALES",
        description="ELIGE UN COLOR PARA TU NOMBRE\n\n"
                    "[ROJO] 🔥\n"
                    "[AZUL] 🌊\n"
                    "[AMARILLO] 🌻\n"
                    "[NARANJA] 🦊\n"
                    "[VERDE] 🍀\n"
                    "[MORADO] 🍇\n"
                    "[ROSA] 🌸\n"
                    "[MARRON] 🍂\n"
                    "[GRIS] ☁️\n"
                    "[BLANCO] ❄️",
        color=0x6A0DAD  # Purple color
    )

    # Enviar el mensaje con el embed y la vista de botones
    await ctx.send(embed=embed, view=ColorButtonView())

# Command !region
@bot.command(name='region')
async def region(ctx):
    embed = discord.Embed(description=
        "Reacciona a la región para obtener el rol:\n\n"
        "🍔 - Norteamérica\n"
        "🫔 - América Central\n"
        "🍕 - Sudamérica\n"
        "🍜 - Europa\n"
        "🦁 - África\n"
        "🐫 - Medio Oriente\n"
        "🍣 - Asia\n"
        "🐨 - Oceanía",
        color=0x6A0DAD  # Purple color
    )
    message = await ctx.send(embed=embed)

    for emoji in region_roles.keys():
        await message.add_reaction(emoji)

    # Save the message ID to a global variable for use in on_raw_reaction_add and on_raw_reaction_remove

    MESSAGE_ID_REGION = message.id
    print(f'Sent !region message with ID: {MESSAGE_ID_REGION}')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Successfully connected to Discord!')
    print('Loaded commands:')
    for command in bot.commands:
        print(f' - {command.name}')

@bot.event
async def on_raw_reaction_add(payload):
    print(f'Reaction added: {payload.emoji} by {payload.user_id}')
    
    if payload.message_id == MESSAGE_ID_PLATAFORMA:
        guild = bot.get_guild(payload.guild_id)
        print(f'Guild: {guild.name} (ID: {guild.id})')
        role_id = roles.get(str(payload.emoji))
        print(f'Role ID for emoji {payload.emoji}: {role_id}')
        if role_id:
            role = guild.get_role(int(role_id))
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.add_roles(role)
                print(f'Assigned {role.name} to {member.name}')
            else:
                print(f'Error: Role or member not found. Role ID: {role_id}, Member ID: {payload.user_id}')
        else:
            print(f'Error: No role found for emoji {payload.emoji}')

    elif payload.message_id == MESSAGE_ID_REGION:
        guild = bot.get_guild(payload.guild_id)
        print(f'Guild: {guild.name} (ID: {guild.id})')
        role_id = region_roles.get(str(payload.emoji))
        print(f'Role ID for emoji {payload.emoji}: {role_id}')
        if role_id:
            role = guild.get_role(int(role_id))
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.add_roles(role)
                print(f'Assigned {role.name} to {member.name}')
            else:
                print(f'Error: Role or member not found. Role ID: {role_id}, Member ID: {payload.user_id}')
        else:
            print(f'Error: No role found for emoji {payload.emoji}')

@bot.event
async def on_raw_reaction_remove(payload):
    print(f'Reaction removed: {payload.emoji} by {payload.user_id}')
    
    if payload.message_id == MESSAGE_ID_PLATAFORMA:
        guild = bot.get_guild(payload.guild_id)
        print(f'Guild: {guild.name} (ID: {guild.id})')
        role_id = roles.get(str(payload.emoji))
        print(f'Role ID for emoji {payload.emoji}: {role_id}')
        if role_id:
            role = guild.get_role(int(role_id))
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.remove_roles(role)
                print(f'Removed {role.name} from {member.name}')
            else:
                print(f'Error: Role or member not found. Role ID: {role_id}, Member ID: {payload.user_id}')
        else:
            print(f'Error: No role found for emoji {payload.emoji}')

    elif payload.message_id == MESSAGE_ID_REGION:
        guild = bot.get_guild(payload.guild_id)
        print(f'Guild: {guild.name} (ID: {guild.id})')
        role_id = region_roles.get(str(payload.emoji))
        print(f'Role ID for emoji {payload.emoji}: {role_id}')
        if role_id:
            role = guild.get_role(int(role_id))
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.remove_roles(role)
                print(f'Removed {role.name} from {member.name}')
            else:
                print(f'Error: Role or member not found. Role ID: {role_id}, Member ID: {payload.user_id}')
        else:
            print(f'Error: No role found for emoji {payload.emoji}')

# Start the bot
bot.run(TOKEN)
