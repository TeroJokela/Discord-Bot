'''
    The bot itself

    discordpy documentation:
    http://discordpy.readthedocs.io/en/latest/api.html
'''
from discord.ext import commands
from chatterbot import ChatBot
from urllib import request
import configparser
import pyspeedtest
import datetime
import requests
import discord
import asyncio
import random
import clever
import time
import sys
import os

# My libraries
import GoogleImageAPI
import ImgurSpider
import EcchiSpider
import osu

# Make an object to read from auth.ini
config = configparser.ConfigParser()
config.read("auth.ini")

# Initialise Google image API
googleAPIKey = config.get('google', 'APIKey')
googleCX = config.get('google', 'CX')
google = GoogleImageAPI.gAPI(googleAPIKey, googleCX)

# Initialise the chatbots
#chatbot = ChatBot("Ter$ka", trainer='chatterbot.trainers.ChatterBotCorpusTrainer')
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

# Initialise the osu API
osuClientKey = config.get('osu', 'key')
osuClient = osu.osu(osuClientKey)

# Initialise the discord client and voice client
clientKey = config.get('discord', 'key')
client = commands.Bot(command_prefix="~", command_not_found="")
client.remove_command("help")

# If this is active, the bot will react to every single message that it can react to
bReactToMessages = False

# Log the command user, server, channel and time
async def logCommand(ctx):
    if ctx.message.server == None:
        await client.send_message(client.get_channel([YOUR BOT_LOG CHANNEL HERE]), "[" + str(ctx.message.timestamp) + "] (" + ctx.message.content + ") by " + str(ctx.message.author) + " in " + str(ctx.message.channel))
    else:
        await client.send_message(client.get_channel([YOUR BOT_LOG CHANNEL HERE]), "[" + str(ctx.message.timestamp) + "] (" + ctx.message.content + ") by " + str(ctx.message.author) + " in " + str(ctx.message.server) + "->#" + str(ctx.message.channel))

# The bot admins and a function to check if a specific user is an admin or not
botAdmins = ["Helmerz#8030", "MoreUsersHere#000", "MoreUsersHere#000"]
def isAdmin(user):
    for i in botAdmins:
        if i == user:
            return True
    return False

# Blacklisting servers that don't want to use the gyazo embed thing
gyazoList = ["server1", "server2"]
def isGyazo(server):
    for i in gyazoList:
        if i == server:
            return True
    return False

# Blacklisting servers that don't want to get reacted with a lot of messages
reactBlacklist = ["server1", "server2"]
def isReactBlacklisted(server):
    for i in reactBlacklist:
        if i == server:
            return True
    return False

def isPostBanned(user):
    with open("banlist.txt", 'r') as f:
        bannedUsers = f.read().split('\n')
    for i in bannedUsers:
        if i == user:
            return True
    return False

def isPictureBanned(user):
    with open("picturebanlist.txt", 'r') as f:
        bannedUsers = f.read().split('\n')
    for i in bannedUsers:
        if i == user:
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

    global startTime 
    startTime = time.time()
    await client.send_message(client.get_channel([YOUR BOT_LOG CHANNEL HERE]), "I'm alive again! c:")

def leaveVoice(_voice):
    coro = _voice.disconnect()
    fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
    try:
        fut.result()
    except:
        pass


# Block non-admins from using a command
async def adminBlock(ctx):
    await client.send_message(ctx.message.channel, "You can't tell me what to do " + ctx.message.author.mention + " >:(")


@client.command(pass_context=True)
async def die(ctx):
    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    await client.say("Time for me to die :(")
    exit()


@client.command(pass_context=True)
async def reactToMessages(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    global bReactToMessages
    bReactToMessages = not bReactToMessages
    await client.say("Reacting to messages: " + str(bReactToMessages))


@client.command(pass_context=True)
async def uptime(ctx):
    global startTime
    uptime = time.time() - startTime
    await client.say("Uptime: " + str(round(uptime, 2)) + " seconds")


@client.command(pass_context=True)
async def createEmoji(ctx, emojiLink : str):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    try:
        f = open('emoji.png', 'wb')
        f.write(requests.get(emojiLink).content)
        f.close()
    except:
        await client.say("I wasn't able to get the picture from that URL, please try another one")
        return
    await client.say("What do you want to call this emoji " + ctx.message.author.mention + "?")
    name = await client.wait_for_message(author=ctx.message.author)
    f = open(r'emoji.png', 'rb')
    try:
        emoji = await client.create_custom_emoji(ctx.message.server, name=str(name.content), image=f.read())
        await client.say(ctx.message.author.mention + " " + str(emoji))
    except discord.errors.Forbidden:
        await client.say("I'm not allowed to create custom emojis on this server")
    except discord.errors.HTTPException:
        await client.say("All the custom emoji slots are already in use! Please delete one before trying to add more.")
    f.close()


@client.command(pass_context=True)
async def deleteEmoji(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    reactToThis = await client.say("React to this message with the emoji that you want to remove " + ctx.message.author.mention + "!")
    reaction = await client.wait_for_reaction(user=ctx.message.author, message=reactToThis, timeout=60)
    reactionEmoji = reaction
    if reactionEmoji.custom_emoji == True:
        await client.delete_custom_emoji(reactionEmoji.emoji)
        await client.send_message(ctx.message.channel, "Emoji succesfully deleted!")
    else:
        await client.send_message(ctx.message.channel, "You can't delete this emoji!")


@client.command(pass_context=True)
async def postBan(ctx, *, toBeBanned : str):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    with open("banlist.txt", 'a') as f:
        f.write(toBeBanned + '\n')
        f.close()

    await client.say("The user `" + toBeBanned + "` has been banned from making posts!")


@client.command(pass_context=True)
async def postUnban(ctx, *, toBeUnbanned : str):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    with open("banlist.txt", 'r+') as f:
        bannedUsers = f.readlines()
        open("banlist.txt", 'w').close() # Clear the text inside
        for i in bannedUsers:
            if not i.startswith(toBeUnbanned):
                f.write(i)
        f.close()

    await client.say("The user `" + toBeUnbanned + "` has been unbanned from making posts!")


@client.command(pass_context=True)
async def postBanlist(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    msg = ""

    with open("banlist.txt", 'r') as f:
        bannedUsers = f.read().split('\n')
        for i in bannedUsers:
            msg += i + '\n'
        f.close()

    await client.say("The banned users are: ```" + msg + "```")


# This is a custom command to send a message to our server, and it will be shown on our website.
# If you want this to work, make a form handler to your server that saves the form data to a file or database
# and show all of the posts somewhere "if you want"
'''
@client.command(pass_context=True)
async def post(ctx, *, msg : str):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if isPostBanned(str(ctx.message.author)):
        await client.say("You are banned from using this command " + ctx.message.author.mention + "!")
        return

    postData = {
        'Nickname': str(ctx.message.author),
        'Message': msg,
        'Password': I'm not telling you this
        }

    res = requests.post("http://lerspi.wtf/posts/post.php", data=postData)
    if res.status_code == requests.codes.ok:
        await client.say("Success!\n" + ctx.message.author.mention + ", your message can be found here: http://lerspi.wtf/posts")
    else:
        helmerz = await client.get_user_info("191608800619266048")
        await client.say("There was an error sending your message " + ctx.message.author.mention + ". I've sent a message about it to my master")
        await client.send_message(helmerz, str(ctx.message.author) + "\n`" + ctx.message.content + "`\nError code: " + str(res.status_code) + "Handler URL: http://lerspi.wtf/posts/post.php")


@client.command(pass_context=True)
async def posts(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    await client.say("Dear " + ctx.message.author.mention + ", you can view the posts here: http://lerspi.wtf/posts")
'''

@client.command(pass_context=True)
async def ping(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    startTime = time.time()
    msg = await client.say("Pong!")
    howLongItTook = time.time() - startTime
    await client.edit_message(msg, new_content="Pong! [ " + str(round(howLongItTook, 2)) + "s ]")


@client.command(pass_context=True)
async def earrape(ctx, chnl : str):
    if not isAdmin(str(ctx.message.author)):
        return

    channel = client.get_channel(chnl)

    if client.is_voice_connected(channel.server):
        voice = channel.server.voice_client
        await voice.move_to(channel)
    else:
        voice = await client.join_voice_channel(channel)
    
    player = voice.create_ffmpeg_player('earrape.mp3')
    player.start()

@client.command(pass_context=True)
async def speedtest(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)
    
    await client.add_reaction(ctx.message, '\U0000231b')

    speedtestResult = pyspeedtest.shell()

    # Make a tag of the requester and add it to the embed description
    description = "Requested by: " + ctx.message.author.mention

    # Make a new embed message
    embed = discord.Embed(title="Speedtest", description=description, colour=0x00ff00)
    embed.set_image(url=speedtestResult)
    await client.send_message(ctx.message.channel, embed=embed)


# No, this isn't a real command for obvious reasons
@client.command(pass_context=True)
async def ddos(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    users = ctx.message.mentions
    if len(users) == 0:
        await client.say("Dear " + ctx.message.author.mention + ", you need to tag the victim(s)!")

    msg = "Sending a DDoS attack to "

    if len(users) > 2:
        temp = 0
        for i in users:
            temp += 1
            if temp == len(users) - 1:
                msg += users[temp - 1].mention + " and " + users[temp].mention
                break
            else:
                msg += i.mention + ", "
    elif len(users) == 2:
        msg += users[0].mention + " and " + users[1].mention
    else:
        msg += users[0].mention

    await client.say(msg)


# Roll a random number between 0 and 100 and send it to the chat channel where the command was sent
# And tag the one who rolled the number
@client.command(pass_context=True)
async def roll(ctx, maxNumber=100):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    await client.say(ctx.message.author.mention + " -> " + str(random.randint(0, int(maxNumber))))

@roll.error
async def roll_handler(error, ctx):
    await client.send_message(ctx.message.channel, ctx.message.author.mention + ", whole numbers only!")

	
# Send a text-to-speech text to the channel where the command was called
# Text-to-speech plays to everyone who is using Discord and can read the channel
# We also delete the messages to hide the evidence that someone used this command
# Currently we check if the message sender is a bot-admin, if so, run the troll
@client.command(pass_context=True)
async def TTS(ctx, *, msg : str):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    await client.say(msg, tts=True)
    await client.purge_from(ctx.message.channel, limit=2)


@client.command(pass_context=True)
async def removeMessages(ctx, amount : int):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    try:
        await client.purge_from(ctx.message.channel, limit=amount + 1)
        await client.say("Removed " + str(amount - 1) + " messages!")
    except discord.errors.Forbidden:
        await client.say("I can't remove messages here!")


@client.command(pass_context=True)
async def pictureBan(ctx, *, toBeBanned : str):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    with open("picturebanlist.txt", 'a') as f:
        f.write(toBeBanned + '\n')
        f.close()

    await client.say("The user `" + toBeBanned + "` has been banned from requesting pictures from me!")


@client.command(pass_context=True)
async def pictureUnban(ctx, *, toBeUnbanned : str):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    with open("picturebanlist.txt", 'r+') as f:
        bannedUsers = f.readlines()
        open("picturebanlist.txt", 'w').close() # Clear the text inside
        for i in bannedUsers:
            if not i.startswith(toBeUnbanned):
                f.write(i)
        f.close()

    await client.say("The user `" + toBeUnbanned + "` has been unbanned from requesting pictures from me!")


@client.command(pass_context=True)
async def pictureBanlist(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    msg = ""

    with open("picturebanlist.txt", 'r') as f:
        bannedUsers = f.read().split('\n')
        for i in bannedUsers:
            msg += i + '\n'
        f.close()

    await client.say("The banned users are: ```" + msg + "```")


@client.command(pass_context=True)
async def picture(ctx, *, tag : str):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
    await client.send_typing(ctx.message.channel)

    if isPictureBanned(str(ctx.message.author)):
        await client.say("Dear " + ctx.message.author.mention + ", you are banned from using this command")
        return
    
    if tag == "random":
        # Get a random picture
        randomPic = ImgurSpider.Imgur.getRandomPic()

        # Make a tag of the requester and add it to the embed description
        description = "Requested by: " + ctx.message.author.mention

        # Make a new embed message
        embed = discord.Embed(title="Random picture", description=description, colour=0x00FFFF)
        embed.set_image(url=randomPic)
        await client.say(embed=embed)
    else:
        # Get a random picture from Google
        imageURL = google.downloadRandomPicture(tag)
        if imageURL == "No_Requests_Left":
            await client.say("I've reached my Google CSE API request limit, I need money to post more :< (PM Helmerz#8030 for more information)")
            return
        elif imageURL == "No_Results":
            await client.say("I didn't find a picture with those search terms, sorry. :(")
            return

        # Make a tag of the requester and add it to the embed description
        description = "Requested by: " + ctx.message.author.mention

        # Make a new embed message, set the image and send it
        embed = discord.Embed(title='`' + tag + '`', description=description, colour=0xFF00FF)
        embed.set_image(url=imageURL)
        await client.say(embed=embed)


@client.command(pass_context=True)
async def NSFWAnime(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)
    
    # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
    await client.send_typing(ctx.message.channel)
    
    # Get a random ecchi picture
    ecchiPic = EcchiSpider.downloadRandomNSFWAnimePic()

    # Make a tag of the requester and add it to the embed description
    description = "Requested by: " + ctx.message.author.mention

    # Make a new embed message
    embed = discord.Embed(title="NSFWAnime", description=description, colour=0x312952)
    embed.set_image(url=ecchiPic)
    await client.say(embed=embed)


@client.command(pass_context=True)
async def randEmoji(ctx):
    await client.say(ctx.message.server.emojis[random.randint(0, len(ctx.message.server.emojis) - 1)])


@client.command(pass_context=True)
async def playing(ctx, *, game : str):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    # In order to change your "playing" status, you need to make a discord game object and change the name
    Game = discord.Game(name=game, url="http://www.helmerz.xyz", type=0)
    await client.change_presence(game=Game)
    await client.add_reaction(ctx.message, '\U00002714')


@client.command(pass_context=True)
async def listening(ctx, *, listen : str):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return

    # In order to change your "listening" status, you need to make a discord game object and change the name and type
    Game = discord.Game(name=listen, url="http://www.helmerz.xyz", type=2)
    await client.change_presence(game=Game)
    await client.add_reaction(ctx.message, '\U00002714')


@client.command(pass_context=True)
async def watching(ctx, *, watch : str):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    if not isAdmin(str(ctx.message.author)):
        await adminBlock(ctx)
        return
    
    # In order to change your "listening" status, you need to make a discord game object and change the name and type
    Game = discord.Game(name=watch, url="http://www.helmerz.xyz", type=3)
    await client.change_presence(game=Game)
    await client.add_reaction(ctx.message, '\U00002714')


@client.command(pass_context=True)
async def coinflip(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    await client.say(str(random.sample(['Heads', 'Tails'], 1))[2:-2])


@client.command(pass_context=True)
async def messageMe(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    await client.whisper("Hello!")


@client.command(pass_context=True)
async def messageTo(ctx, chnl : str, *, msg : str):
    if not isAdmin(str(ctx.message.author)):
        return

    # Log the command user, server, channel and time
    await logCommand(ctx)

    await client.send_message(client.get_channel(chnl), msg)

@client.command(pass_context=True)
async def help(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    with open("help.txt", 'r') as myfile:
        textHelp = myfile.read()
        myfile.close()

    await client.say(textHelp)

@client.command(pass_context=True)
async def help_admin(ctx):
    # Log the command user, server, channel and time
    await logCommand(ctx)

    with open("helpAdmin.txt", 'r') as myfile:
        textHelp = myfile.read()
        myfile.close()

    await client.say(textHelp)


# This function gets called every time a new message has been sent to a channel that the bot can read
@client.event
async def on_message(msg):
    # This adds a reaction to every single message that the bot can react to
    global bReactToMessages
    if bReactToMessages == True and not isReactBlacklisted(str(msg.server)):
        await client.add_reaction(msg, msg.server.emojis[random.randint(0, len(msg.server.emojis) - 1)])
        await client.add_reaction(msg, u"\U0001F1F0")
        await client.add_reaction(msg, u"\U0001F1FE")
        await client.add_reaction(msg, u"\U0001F1F8")
        await client.add_reaction(msg, '😂')
        await client.add_reaction(msg, '👌')

    # This is to see if the bot gets tagged in a message, every text after that is a question for the chatbot to answer
    # Only works if you FIRST tag the bot and then write your question, because that's how I want it to work
    elif msg.content.startswith("<@397454492108324864>"):
        # Send an input so it shows "Ter$kaBot is typing..." in the discord text channel
        await client.send_typing(msg.channel)

        #chatbotAnswer = str(chatbot.get_response(message.content[22:])) # Chatterbot
        chatbotAnswer = await cleverbot.query(msg.content[22:]) # Cleverbot

        await client.send_message(msg.channel, "{0} {1}".format(msg.author.mention, chatbotAnswer))

    await client.process_commands(msg)
    return


'''
    # If a osu profile link gets posted, we get the user's country, country rank, PP and playcount and send the information
    # as an embed text so it's easy to read and looks nice and compact
    elif message.content.startswith("https://osu.ppy.sh/u/"):
        # Log the command user, server, channel and time
        await logCommand(message)

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
        await logCommand(message)
        
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
'''


# Run the bot with our API key
client.run(clientKey)
