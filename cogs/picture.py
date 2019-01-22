from .helpers.error import sendErrorToOwner
from PIL import Image, ImageOps, ImageDraw
from discord.ext import commands
from io import BytesIO
import discord
import aiohttp
import random
import json
import os


class Picture(object):
    def __init__(self, client: commands.Bot):
        self.client = client

    def makeHugImage(self, huggerAvatar: BytesIO, toHugAvatar: BytesIO):
        huggerAvatar = Image.open(huggerAvatar).resize((117, 117))
        toHugAvatar = Image.open(toHugAvatar).resize((117, 117))
        hugImage = Image.open(f"{os.getcwd()}/resources/hug.png") # Maybe add multiple images in the future?
        baseImage = Image.new("RGB", hugImage.size)
        baseImage.paste(huggerAvatar, (246, 98))
        baseImage.paste(toHugAvatar, (127, 70))
        baseImage.paste(hugImage, (0, 0), hugImage)
        ret = BytesIO()
        baseImage.save(ret, "PNG")
        ret.seek(0) # Go back to the start of the stream
        return ret

    def makeSlapFrame(self, frame: Image, slapperAvatar: Image, slapperPos: tuple, toSlapAvatar: Image, toSlapPos: tuple):
        slapperPos = (int(slapperPos[0] - slapperAvatar.width / 2), int(slapperPos[1] - slapperAvatar.height / 2))
        toSlapPos = (int(toSlapPos[0] - toSlapAvatar.width / 2), int(toSlapPos[1] - toSlapAvatar.height / 2))
        finishedImage = Image.new("RGBA", frame.size)
        finishedImage.paste(slapperAvatar, slapperPos)
        finishedImage.paste(toSlapAvatar, toSlapPos)
        finishedImage.paste(frame, (0, 0), frame)
        return finishedImage
        
    def makeSlapGif(self, dic: dict, slapperAvatar: BytesIO, toSlapAvatar: BytesIO):
        slapperAvatar = Image.open(slapperAvatar).resize(tuple(dic["size"]))
        toSlapAvatar = Image.open(toSlapAvatar).resize(tuple(dic["size"]))
        gif = Image.open(f"{os.getcwd()}/{dic['path']}")
        gifCounter = 0
        frames = []
        # Extract all the frames from the gif as PNGs
        while gif:
            toAppend = gif.copy().convert("RGBA")
            gifCounter += 1
            try:
                toAppend = self.makeSlapFrame(toAppend, slapperAvatar, tuple(dic["slapperPos"][gifCounter - 1]), toSlapAvatar, tuple(dic["toSlapPos"][gifCounter - 1]))
                frames.append(toAppend)
                gif.seek(gifCounter)
            except EOFError:
                break
        ret = BytesIO()
        retGif = frames[0].copy() # Stupidest fix I could think of right now
        retGif.save(ret, "GIF", append_images=frames[1:], save_all=True, optimize=False, loop=0)
        ret.seek(0)
        return ret

    async def getAvatarBytes(self, user: discord.User):
        async with aiohttp.ClientSession() as session:
            avatarURL = user.avatar_url if user.avatar_url else user.default_avatar_url
            res = await session.get(avatarURL)
            return BytesIO(await res.read())

    @commands.command(pass_context=True, brief="[tag someone]")
    async def hug(self, ctx: commands.Context, toHug: discord.Member):
        """Give someone you love a hug!"""
        await self.client.send_typing(ctx.message.channel)
        huggerAvatarBytes = await self.getAvatarBytes(ctx.message.author)
        toHugAvatarBytes = await self.getAvatarBytes(toHug)
        
        # Because "makeHugImage" isn't an async function, we can do this to prevent it blocking the main thread
        image = await self.client.loop.run_in_executor(None, self.makeHugImage, huggerAvatarBytes, toHugAvatarBytes)

        embed = discord.Embed(description=f"{ctx.message.author.mention} hugged {toHug.mention}, how cute!", colour=0xFF69B4)
        embed.set_image(url="attachment://UwU.png")
        # Nice one-liner (set the image locally without needing to upload it somewhere first and then using Embed.set_image()
        msgData = await self.client.http.send_file(ctx.message.channel.id, image, guild_id=ctx.message.server.id, filename="UwU.png", embed=embed.to_dict())
        self.client.connection._create_message(channel=ctx.message.channel, **msgData)

    @hug.error
    async def hug_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.MissingRequiredArgument):
            await self.client.say(f"{ctx.message.author.mention} you forgot something... Baka...")
        elif isinstance(err, commands.BadArgument):
            await self.client.say(f"{ctx.message.author.mention} what the fuck are you doing? Baka...")
        else:
            await sendErrorToOwner(self.client, err)

    @commands.command(pass_context=True, brief="[tag someone]")
    async def slap(self, ctx: commands.Context, toSlap: discord.Member):
        """Give someone a hard slap"""
        await self.client.send_typing(ctx.message.channel)
        slapperAvatarBytes = await self.getAvatarBytes(ctx.message.author)
        toSlapAvatarBytes = await self.getAvatarBytes(toSlap)

        with open("./resources/data.json") as file:
            dic = json.loads(file.read())
            file.close()

        slapGifData = random.choice(dic["slapData"])

        # Because "makeSlapGif" isn't an async function, we can do this to prevent it blocking the main thread
        gif = await self.client.loop.run_in_executor(None, self.makeSlapGif, slapGifData, slapperAvatarBytes, toSlapAvatarBytes)

        embed = discord.Embed(description=f"{ctx.message.author.mention} slapped {toSlap.mention}!", colour=0xFF0000)
        embed.set_image(url="attachment://OwO.gif")
        # Nice one-liner (set the image locally without needing to upload it somewhere first and then using Embed.set_image()
        msgData = await self.client.http.send_file(ctx.message.channel.id, gif, guild_id=ctx.message.server.id, filename="OwO.gif", embed=embed.to_dict())
        self.client.connection._create_message(channel=ctx.message.channel, **msgData)

    @slap.error
    async def slap_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.MissingRequiredArgument):
            await self.client.say(f"{ctx.message.author.mention} you forgot something... Baka...")
        elif isinstance(err, commands.BadArgument):
            await self.client.say(f"{ctx.message.author.mention} what the fuck are you doing? Baka...")
        else:
            await sendErrorToOwner(self.client, err)


def setup(client: commands.Bot):
    client.add_cog(Picture(client))