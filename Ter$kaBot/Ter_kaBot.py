'''
    The bot itself

    discordpy documentation:
    http://discordpy.readthedocs.io/en/latest/api.html
'''
from chatterbot import ChatBot
from urllib import request
#import cleverbot_io
import configparser
import requests
import discord
import asyncio
import random
import datetime
import clever
import time
import os
# My libraries
import GoogleImageAPI
import ImgurSpider
import EcchiSpider
import osu

# Prefix
prefix = "~"

# Make an object to read from auth.ini
config = configparser.ConfigParser()
config.read("auth.ini")

# Initialise Google image API
googleAPIKey = config.get('google', 'APIKey')
googleCX = config.get('google', 'CX')
google = GoogleImageAPI.gAPI(googleAPIKey, googleCX)

# Initialise the chatbots
chatbot = ChatBot("Ter$ka", trainer='chatterbot.trainers.ChatterBotCorpusTrainer')
cleverbotUser = config.get('cleverbot', 'user')
cleverbotKey = config.get('cleverbot', 'key')
cleverbot = clever.CleverBot(user=cleverbotUser, key=cleverbotKey, nick="Ter$kaBot")

# Uncomment these and run once if you're creating your chatbot for the first time
# These will train your chatbot 
'''
chatbot.train("chatterbot.corpus.english")
chatbot.train("chatterbot.corpus.english.greetings")
chatbot.train("chatterbot.corpus.english.conversations")
'''

# Initialise the discord client and voice client
clientKey = config.get('discord', 'key')
client = discord.Client()

# Initialise the osu API
osuClientKey = config.get('osu', 'key')
osuClient = osu.osu(osuClientKey)

# If this is active, the bot will react to every single message that it can react to
reactToMessages = False

# Log the command user, server, channel and time
def logCommand(message):
    if message.server == None:
        print("[" + str(message.timestamp) + "] (" + message.content + ") by " + str(message.author) + " in " + str(message.channel))
    else:
        print("[" + str(message.timestamp) + "] (" + message.content + ") by " + str(message.author) + " in " + str(message.server) + "->#" + str(message.channel))

# The bot admins and a function to check if a specific user is an admin or not
botAdmins = ["Helmerz#8030", "More Users Here"]
def isAdmin(user):
    for i in botAdmins:
        if i == user:
            return True
    return False
	
# Blacklisting servers that don't want to use the gyazo embed thing
gyazoList = ["Server1", "More servers here"]
def isGyazo(server):
    for i in gyazoList:
        if i == server:
            return True
    return False

# Blacklisting servers that don't want to get reacted with a lot of messages
reactBlacklist = ["Server1", "More servers here"]
def isReactBlacklisted(server):
    for i in reactBlacklist:
        if i == server:
            return True
    return False

# When the bot has fully initialised itself, this function gets ran
@client.event
async def on_ready():
    howManyServers = 0
    servers = []
    for server in client.servers:
        servers.append(server)
        howManyServers += 1

    print("============= Ready! =============")
    print("== We're connected to " + str(howManyServers) + " servers ==")
    print("(", end="")
    temp = 0
    for i in servers:
        temp += 1
        if temp == len(servers):
            print(str(i) + ")")
        else:
            print(str(i) + ",", end=" ")

def leaveVoice(_voice):
    coro = _voice.disconnect()
    fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
    try:
        fut.result()
    except:
        pass

# This function gets called every time a new message has been sent to a channel that the bot can read
@client.event
async def on_message(message):
    startTime = time.time()

    # Kill the bot by prefix + "quit" or prefix + "die"
    if message.content == prefix + "quit" or message.content == prefix + "die" or message.content == prefix + "kill" or message.content == prefix + "suicide":
        if isAdmin(str(message.author)):
            await client.send_message(message.channel, "Time for me to die :(")
            exit()
        else:
            await client.send_message(message.channel, "You can't tell me what to do >:(")

    # This adds a reaction to every single message that the bot can react to
    global reactToMessages
    if reactToMessages == True and not isReactBlacklisted(str(message.server)):
        await client.add_reaction(message, message.server.emojis[random.randint(0, len(message.server.emojis) - 1)])
        await client.add_reaction(message, u"\U0001F1F0")
        await client.add_reaction(message, u"\U0001F1FE")
        await client.add_reaction(message, u"\U0001F1F8")
        await client.add_reaction(message, '😂')
        await client.add_reaction(message, '👌')

    # Here you can toggle if you want the bot to react to message (see above)
    if message.content.startswith(prefix + "ReactToMessages"):
        # Log the command user, server, channel and time
        logCommand(message)

        if isAdmin(str(message.author)):
            reactToMessages = not reactToMessages
            await client.send_message(message.channel, "Reacting to messages: " + str(reactToMessages))
        else:
            await client.send_message(message.channel, "You can't tell me what to do >:(")
        
    elif message.content.startswith(prefix + "CreateEmoji"):
        # Log the command user, server, channel and time
        logCommand(message)

        if isAdmin(str(message.author)):
            tagMe = discord.User().name = message.author
            link = message.content[len(prefix + "CreateEmoji"):]
            try:
                #request.urlretrieve(link, 'emoji.png')
                f = open('emoji.png', 'wb')
                f.write(requests.get(link).content)
                f.close()
            except:
                await client.send_message(message.channel, "I wasn't able to get the picture from that URL, please try another one")
                return
            await client.send_message(message.channel, "What do you want to call this emoji " + tagMe.mention + "?")
            name = await client.wait_for_message(author=message.author)
            f = open(r'emoji.png', 'rb')
            try:
                emoji = await client.create_custom_emoji(message.server, name=str(name.content), image=f.read())
                await client.send_message(message.channel, tagMe.mention + " " + str(emoji))
            except discord.errors.Forbidden:
                await client.send_message(message.channel, "I'm not allowed to create custom emojis on this server")
        else:
            await client.send_message(message.channel, "You can't tell me what to do >:(")

    elif message.content.startswith(prefix + "DeleteEmoji"):
        # Log the command user, server, channel and time
        logCommand(message)

        if isAdmin(str(message.author)):
            tagMe = discord.User().name = message.author
            reactToThis = await client.send_message(message.channel, "React to this message with the emoji that you want to remove " + tagMe.mention + "!")
            reaction = await client.wait_for_reaction(user=message.author, message=reactToThis, timeout=60)
            reactionEmoji, reactionUser = reaction
            if reactionEmoji.custom_emoji == True:
                await client.delete_custom_emoji(reactionEmoji.emoji)
                await client.send_message(message.channel, "Emoji succesfully deleted!")
            else:
                await client.send_message(message.channel, "You can't delete this emoji!")
        else:
            await client.send_message(message.channel, "You can't tell me what to do >:(")

    elif message.content.startswith(prefix + "ping"):
        # Log the command user, server, channel and time
        logCommand(message)

        msg = await client.send_message(message.channel, "Pong!")
        howLongItTook = time.time() - startTime
        await client.edit_message(msg, new_content="Pong! [ " + str(round(howLongItTook, 2)) + "s ]")

    elif message.content.startswith(prefix + "earrape"):
        if isAdmin(str(message.author)):
            channel = message.content[len(prefix + "earrape") + 1:]
            voice = await client.join_voice_channel(client.get_channel(channel))
            player = voice.create_ffmpeg_player('earrape.mp3', after=lambda: leaveVoice(voice))
            player.start()

    # Roll a random number between 0 and 100 and send it to the chat channel where the command was sent
    # And tag the one who rolled the number
    elif message.content.startswith(prefix + "roll"):
        # Log the command user, server, channel and time
        logCommand(message)

        if len(message.content) > len(prefix + "roll"):
            try:
                maxNumber = int(message.content[len(prefix + "roll"):])
                tagMe = discord.User().name = message.author
                await client.send_message(message.channel, tagMe.mention + " -> " + str(random.randint(0, maxNumber)))
            except ValueError:
                await client.send_message(message.channel, tagMe.mention + ", numbers only!")
        else:
            tagMe = discord.User().name = message.author
            await client.send_message(message.channel, tagMe.mention + " -> " + str(random.randint(0, 100)))

    # Send a text-to-speech text to the channel where the command was called
    # Text-to-speech plays to everyone who is using Discord and can read the channel
    # We also delete the messages to hide the evidence that someone used this command
    # Currently we check if the message sender is a bot admin, if so, run the troll
    elif message.content.startswith(prefix + "TTS"):
        # Log the command user, server, channel and time
        logCommand(message)

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
        #chatbotAnswer = str(chatbot.get_response(message.content[22:])) #Chatterbot
        chatbotAnswer = cleverbot.query(message.content[22:]) # Cleverbot
        output = tagMe.mention + " " + chatbotAnswer
        await client.send_message(message.channel, output)

    # Removes an X amount of messages than can be specified after prefix + "RemoveMessages" (int only)
    elif message.content.startswith(prefix + "RemoveMessages"):
        # Log the command user, server, channel and time
        logCommand(message)

        try:
	    # See if the message author is a bot-admin
            if isAdmin(str(message.author)):
                howMany = int(message.content[16:]) + 1
		# Remove messages
                await client.purge_from(message.channel, limit=howMany)
                await client.send_message(message.channel, "Removed " + str(howMany - 1) + " messages!")
            else: # Message author it not a bot-admin
                await client.send_message(message.channel, "You can't tell me what to do >:(")
        except discord.errors.Forbidden: # No permissions to remove messages
            await client.send_message(message.channel, "I can't remove messages here!")

    # We download a random picture and send it to the chat channel where the command was sent
    elif message.content.startswith(prefix + "NSFWAnime"):
        # Log the command user, server, channel and time
        logCommand(message)
                    
        # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
        await client.send_typing(message.channel)
        
        # Get a random ecchi picture
        ecchiPic = EcchiSpider.downloadRandomNSFWAnimePic()

        # Make a tag of the requester and add it to the embed description
        tagMe = discord.User().name = message.author
        description = "Requested by: " + tagMe.mention

        # Make a new embed message
        embed = discord.Embed(title="NSFWAnime", description=description, colour=0x312952)
        embed.set_image(url=ecchiPic)
        await client.send_message(message.channel, embed=embed)

    # Download a random picture from imgur's most recent pictures and send it to the chat channel where the command was sent
    elif message.content == prefix + "picture random":
        # Log the command user, server, channel and time
        logCommand(message)

        # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
        await client.send_typing(message.channel)

        # Get a random picture
        randomPic = ImgurSpider.Imgur.getRandomPic()

        # Make a tag of the requester and add it to the embed description
        tagMe = discord.User().name = message.author
        description = "Requested by: " + tagMe.mention

        # Make a new embed message
        embed = discord.Embed(title="Random picture", description=description, colour=0x00FFFF)
        embed.set_image(url=randomPic)
        await client.send_message(message.channel, embed=embed)

    # Download a picture from imgur's most recent pictures using the tags given after the prefix + "picture" command 
    # and send it to the chat channel where the command was sent
    elif message.content.startswith(prefix + "picture"):
        # Log the command user, server, channel and time
        logCommand(message)

        # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
        await client.send_typing(message.channel)
        
        # Get a random picture from Google
        try:
            imageURL = google.downloadRandomPicture(message.content[len(prefix + "picture") + 1:])
        except:
            await client.send_message(message.channel, "Either I didn't find a picture with that tag or I've reached my Google CSE API request limit, I need money to post more :< (PM Helmerz#8030 for more information)")
            return

        # Make a tag of the requester and add it to the embed description
        tagMe = discord.User().name = message.author
        description = "Requested by: " + tagMe.mention

        # Make a new embed message, set the image and send it
        embed = discord.Embed(title='`' + message.content[len(prefix + "picture") + 1:] + '`', description=description, colour=0xFF00FF)
        embed.set_image(url=imageURL)
        await client.send_message(message.channel, embed=embed)

    # Send a random emoji from the server's custom emojis
    elif message.content.startswith(prefix + "RandEmoji"):
        await client.send_message(message.channel, message.server.emojis[random.randint(0, len(message.server.emojis) - 1)])

    # This is changes the "playing" status on Discord to the text after the prefix + "playing" command
    elif message.content.startswith(prefix + "playing"):
        # Log the command user, server, channel and time
        logCommand(message)

        # In order to change your "playing" status, you need to make a discord game object and change the name
        if isAdmin(str(message.author)):
            Game = discord.Game(name=message.content[9:], url="http://www.helmerz.xyz")
            await client.change_presence(game=Game)
        else:
            await client.send_message(message.channel, "You can't tell me what to do >:(")

    # Flips a virtual coin (chooses either "Heads" or "Tails" randomly) and sends the result to the message 
    # channel where the command was called
    elif message.content.startswith(prefix + "coinflip"):
        # Log the command user, server, channel and time
        logCommand(message)

        await client.send_message(message.channel, str(random.sample(['Heads', 'Tails'], 1))[2:-2])

    # Sends a private message "Hello!" to the author of the command message
    elif message.content.startswith(prefix + "MessageMe"):
        # Log the command user, server, channel and time
        logCommand(message)

        await client.send_message(message.author, "Hello!")
        
    # Get all the text from help.txt and send it to the chat where the command was called
    elif message.content.startswith(prefix + "help"):
        # Log the command user, server, channel and time
        logCommand(message)

        with open("help.txt", 'r') as myfile:
            textHelp = myfile.read()
        await client.send_message(message.channel, textHelp)

    # Send a custom message to a specific channel (The bot must be in the same server and you must send the channel ID)
    elif message.content.startswith(prefix + "messageTo"):
        if isAdmin(str(message.author)):
            channel = message.content[11:29]
            await client.send_message(client.get_channel(channel), message.content[30:])
			
    # If a osu profile link gets posted, we get the user's country, country rank, PP and playcount and send the information
    # as an embed text so it's easy to read and looks nice and compact
    elif message.content.startswith("https://osu.ppy.sh/u/"):
        # Log the command user, server, channel and time
        logCommand(message)

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
        # Log the command user, server, channel and time
        logCommand(message)
        
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
        
    # Remove the normal gyazo message and send the direct link to the image
    elif message.content.startswith("https://gyazo.com/") and isGyazo(str(message.server)):
        link = message.content[:50]
        tagMe = discord.User().name = message.author
        await client.send_message(message.channel, tagMe.mention + " https://i.gyazo.com/" + link[18:] + ".png" + message.content[50:])
        await client.delete_message(message)

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
