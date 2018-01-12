'''
    The bot itself

    discordpy documentation:
    http://discordpy.readthedocs.io/en/latest/api.html
'''
import configparser
from chatterbot import ChatBot
import discord
import asyncio
import random
# My libraries
import ImgurSpider
import EcchiSpider
import osu

# Make an object to read from auth.ini
config = configparser.ConfigParser()
config.read("auth.ini")

# Initialise the chatbot
chatbot = ChatBot("Ter$ka", trainer='chatterbot.trainers.ChatterBotCorpusTrainer')

# Uncomment these and run once if you're creating your chatbot for the first time
# These will train your chatbot 
'''
chatbot.train("chatterbot.corpus.english")
chatbot.train("chatterbot.corpus.english.greetings")
chatbot.train("chatterbot.corpus.english.conversations")
'''

# Initialise the discord client
clientKey = config.get('discord', 'key')
client = discord.Client()

# Initialise the osu API
osuClientKey = config.get('osu', 'key')
osuClient = osu.osu(osuClientKey)

# The bot admins and a function to check if a specific user is an admin or not
botAdmins = ["Helmerz#8030", "MoreUsersHere#0000"]
def isAdmin(user):
    for i in botAdmins:
        if i == user:
            return True
    return False

# When the bot has fully initialised itself, this function gets ran
@client.event
async def on_ready():
    print("Logged in!")    
    await client.send_message(client.get_channel('347349837903167489'), "I'm alive again! c:")

# This function gets called every time a new message has been sent to a channel that the bot can read
@client.event
async def on_message(message):
    # Kill the bot by "!quit" or "!die"
    if message.content == "!quit" or message.content == "!die":
        if isAdmin(str(message.author)):
            await client.send_message(message.channel, "Time for me to die :(")
            exit()

    # Roll a random number between 0 and 100 and send it to the chat channel where the command was sent
    elif message.content.startswith("!roll"):
        await client.send_message(message.channel, str(random.randint(0, 100)))

    # Send a text-to-speech text to the channel where the command was called
    # Text-to-speech plays to everyone who is using Discord and can read the channel
    # We also delete the messages to hide the evidence that someone used this command
    # Currently we check if the message sender is a bot admin, if so, run the troll
    elif message.content.startswith("!TTS"):
        if isAdmin(str(message.author)):
            text = message.content[5:]
            await client.send_message(message.channel, text, tts=True)
            await client.purge_from(message.channel, limit=2)
        else:
            await client.send_message(message.channel, "This command is for bot-admins only!")

    # This is to see if the bot gets tagged in a message, every text after that is a question for the chatbot to answer
    # Only works if you FIRST tag the bot and then write your question
    elif message.content.startswith("<@397454492108324864>"):
        # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
        await client.send_typing(message.channel)
        tagMe = discord.User().name = message.author
        chatbotAnswer = str(chatbot.get_response(message.content[22:]))
        output = tagMe.mention + " " + chatbotAnswer
        await client.send_message(message.channel, output)

    # Removes an X amount of messages than can be specified after "!RemoveMessages" (int only)
    elif message.content.startswith("!RemoveMessages"):
        try:
            if isAdmin(str(message.author)):
                howMany = int(message.content[16:]) + 1
                await client.purge_from(message.channel, limit=howMany)
                await client.send_message(message.channel, "Removed " + str(howMany - 1) + " messages!")
            else:
                await client.send_message(message.channel, "You can't tell me what to do >:(")
        except discord.errors.Forbidden:
            await client.send_message(message.channel, "I can't remove messages here!")

    # If a osu profile link gets posted, we get the user's country, country rank, PP and playcount and send the information
    # as an embed text so it's easy to read and looks nice and compact
    elif message.content.startswith("https://osu.ppy.sh/u/"):
        # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
        await client.send_typing(message.channel)

        # Get the data and start making our description and other stuff for our embed text
        user = osuClient.get_user(message.content)
        description = ""
        description += "Country: " + user['country'] + "\n"
        description += "Country rank: " + user['pp_country_rank'] + "\n"
        description += "PP: " + user['pp_raw'][:-3] + "\n"
        description += "Playcount: " + user['playcount'] + "\n"

        # Make the embed object and send the message
        embed = discord.Embed(title=user['username'], description=description, colour=0x1248FF)
        await client.send_message(message.channel, embed=embed)

    # If a osu map link gets sent, we get all kinds of data from the map and send it to the same channel as an embed link
    elif message.content.startswith("https://osu.ppy.sh/b/"):
        # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
        await client.send_typing(message.channel)

        # Get the data and start creating our description and other stuff for our embed text
        map = osuClient.get_beatmaps(message.content)
        description = ""
        mode = ""
        if map['mode'] == '0':
            mode = "Standard"
        elif map['mode'] == '1':
            mode = "Taiko"
        elif map['mode'] == '2':
            mode = "CTB"
        elif map['mode'] == '3':
            mode = "Mania"
        if map['approved'] == '1' or map['approved'] == '2':
            description += "Status: Ranked"
        elif map['approved'] == '3':
            description += "Approved: Qualified"
        elif map['approved'] == '4':
            description += "Approved: Loved"
        description += "\nDifficulty: " + map['difficultyrating'][:3] + "*"
        description += "\nCreator: " + map['creator']
        description += "\nMode: " + mode
        description += "\nBPM: " + map['bpm']

        # Make an embed object to send to the chat
        # (embed looks good :^))
        embed = discord.Embed(title=map['artist'] + " - " + map['title'] + " [" + map['version'] + "]", description=description, colour=0x53A0FF)
        await client.send_message(message.channel, embed=embed)

    # We download a random picture and send it to the chat channel where the command was sent
    elif message.content.startswith("!NSFWAnime"):
        # Log the command user, server, channel and time
        if message.server == None:
            print("[" + str(message.timestamp) + "] (" + message.content + ") by " + str(message.author) + " in " + str(message.channel))
        else:
            print("[" + str(message.timestamp) + "] (" + message.content + ") by " + str(message.author) + " in " + str(message.server) + "->#" + str(message.channel))
            
        # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
        await client.send_typing(message.channel)
        EcchiSpider.downloadRandomNSFWAnimePic()
        try:
            # Send the picture
            await client.send_file(message.channel, r'ecchi.jpg')
        except discord.errors.HTTPException: # This error occurs if the image is too "graphic", usually only happens in private messages
            # Download a new picture and send that
            EcchiSpider.downloadRandomNSFWAnimePic()
            await client.send_file(message.channel, r'ecchi.jpg')

    # Download a random picture from imgur's most recent pictures and send it to the chat channel where the command was sent
    elif message.content == "!picture random":
        # Log the command user, server, channel and time
        if message.server == None:
            print("[" + str(message.timestamp) + "] (" + message.content + ") by " + str(message.author) + " in " + str(message.channel))
        else:
            print("[" + str(message.timestamp) + "] (" + message.content + ") by " + str(message.author) + " in " + str(message.server) + "->#" + str(message.channel))

        # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
        await client.send_typing(message.channel)
        while ImgurSpider.Imgur.downloadRandomPic() == False:
            # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
            await client.send_typing(message.channel)
        # Send the picture
        await client.send_file(message.channel, r'random.jpg')

    # Download a picture from imgur's most recent pictures using the tags given after the "!picture" command 
    # and send it to the chat channel where the command was sent
    elif message.content.startswith("!picture"):
        # Log the command user, server, channel and time
        if message.server == None:
            print("[" + str(message.timestamp) + "] (" + message.content + ") by " + str(message.author) + " in " + str(message.channel))
        else:
            print("[" + str(message.timestamp) + "] (" + message.content + ") by " + str(message.author) + " in " + str(message.server) + "->#" + str(message.channel))

        # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
        await client.send_typing(message.channel)

        link = ImgurSpider.Imgur.createLink(message.content[9:])
        while ImgurSpider.Imgur.downloadRandomPicByTag(link) == False:
            # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
            await client.send_typing(message.channel)
        await client.send_file(message.channel, r'pic.jpg')

    # Flips a virtual coin (chooses either "Heads" or "Tails" randomly) and sends the result to the message 
    # channel where the command was called
    elif message.content.startswith("!coinflip"):
        await client.send_message(message.channel, str(random.sample(['Heads', 'Tails'], 1))[2:-2])

    # Sends a private message "Hello!" to the author of the command message
    elif message.content.startswith("!MessageMe"):
        await client.send_message(message.author, "Hello!")
        
    # Get all the text from help.txt and send it to the chat where the command was called
    elif message.content.startswith("!help"):
        with open("help.txt", 'r') as myfile:
            textHelp = myfile.read()
        await client.send_message(message.channel, textHelp)

    # This can be used to log every single message on every single channel that the bot can read (ignores the bot itself)
        '''
    elif message.content.startswith(""):
        if str(message.author) != "Ter$kaBot#6161":
            #sendThis = str(message.author)[:-5] + ": " + message.content
            embed = discord.Embed(description=message.content, colour=0x66a9aa) # title=str(message.author),
            embed.set_author(name=str(message.author))
            await client.send_message(client.get_channel('397580155339669515'), embed=embed)
        '''

# Run the bot with our API key
client.run(clientKey)
