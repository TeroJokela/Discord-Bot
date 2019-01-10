"""
    Suck my weewee and end my lifewee
"""
from discord.ext import commands
from cogs.helpers import checks
from cogs.clever import Clever
import configparser


client = commands.Bot(command_prefix="~")
client.remove_command("help")

# Read our config file (Hey, this 'global' parser works)
client.cfgParser = configparser.ConfigParser()
client.cfgParser.read("auth.ini")

# Store the data from it
clientKey = client.cfgParser.get("discord", "key")
cleverbotKey = client.cfgParser.get("cleverbot", "key")
cleverbotUser = client.cfgParser.get("cleverbot", "user")


client.allCogs = [
    "cogs.google",
    "cogs.ecchi",
    "cogs.clever",
    "cogs.troll",
    "cogs.mod",
    "cogs.help",
    "cogs.helmerz",
    "cogs.misc",
    "cogs.picture",
    "cogs.video"
]


@client.event
async def on_ready():
    print("==== Starting to initialize ====")

    print("Loading cogs...")    
    for cog in client.allCogs:
        try:
            client.load_extension(cog)
            print(f"Successfully loaded cog \"{cog}\"")
        except Exception as err:
            print(f"Failed to load cog \"{cog}\" [{type(err).__name__}: {err}]")

    print(f"-- Connected to {len(client.servers)} servers:")
    for server in client.servers:
        print(f":: {server.name}")

    print("==== Initialization success! ====")

# This is necessary for the tag-only function for the chatbot
@client.event
async def on_message(msg):
    if msg.content.startswith(f"<@{client.user.id}>") and msg.author != client.user:
        await client.send_typing(msg.channel)
        res = await client.getResponse(msg.content[22:])
        await client.send_message(msg.channel, f"{msg.author.mention} {res}")
        return

    # Continue to loop the commands
    await client.process_commands(msg)


# Run the bot with our API key
client.run(clientKey)