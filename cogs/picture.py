from discord.ext import commands
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw
import discord
import aiohttp
import os


class Picture(object):
    def __init__(self, client: commands.Bot):
        self.client = client

    def makeHugImage(self, senderAvatar: BytesIO, toHugAvatar: BytesIO):
        senderAvatar = Image.open(senderAvatar).resize((117, 117))
        toHugAvatar = Image.open(toHugAvatar).resize((117, 117))
        hugImage = Image.open(f"{os.getcwd()}/resources/hug.png") # Maybe add multiple images in the future?
        baseImage = Image.new("RGB", hugImage.size)
        baseImage.paste(senderAvatar, (246, 98))
        baseImage.paste(toHugAvatar, (127, 70))
        baseImage.paste(hugImage, (0, 0), hugImage)
        ret = BytesIO()
        baseImage.save(ret, "PNG")
        ret.seek(0) # Go back to the start of the stream
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
        userAvatarBytes = await self.getAvatarBytes(ctx.message.author)
        toHugAvatarBytes = await self.getAvatarBytes(toHug)
        
        # Because "makeHugImage" isn't an async function, we can do this to prevent it blocking the main thread
        image = await self.client.loop.run_in_executor(None, self.makeHugImage, userAvatarBytes, toHugAvatarBytes)

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


def setup(client: commands.Bot):
    client.add_cog(Picture(client))