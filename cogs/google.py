from discord.ext import commands
import discord
import aiohttp
import random


class Google(object):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.baseURL = "https://www.googleapis.com/customsearch/v1"
        self.googleKey = client.cfgParser.get("google", "key")
        self.googleCX = client.cfgParser.get("google", "CX")

    async def getRandomImage(self, tag: str, gif=False):
        args = {
            "q": tag, # Query string
            "key": self.googleKey,
            "cx": self.googleCX,
            "filter": "1", # Turn on duplication filter
            "searchType": "image", # Images only
			"safe": "off" # Safe search off
        }

        # Set the filetype to a gif?
        if gif == True:
            args["fileType"] = "gif"

        async with aiohttp.ClientSession() as session:
            res = await session.get(url=self.baseURL, params=args)
            res = await res.json()
            if int(res["queries"]["request"][0]["totalResults"]) == 0:
                return False
            else:
                # Filter function for removing pictures that are too big for Discord
                def removeTooBig(item):
                    if int(item["image"]["byteSize"]) < 8000000:
                        return True
                    else:
                        return False
                
                images = list(filter(removeTooBig, res["items"]))
                return random.choice(images)

    @commands.command(pass_context=True, brief="[tag]")
    async def picture(self, ctx: commands.Context, *, tag: str):
        """Get a picture from Google with the wanted tag"""
        await self.client.send_typing(ctx.message.channel)

        image = await self.getRandomImage(tag)

        if image == False:
            await self.client.reply(f"I couldn\"t get a picture with `{tag}`, sorry :<")
            return

        # Make a new embed message, set the image and send it
        embed = discord.Embed(title=f"Picture: `{tag}`", description=f"Requested by: {ctx.message.author.mention}", colour=0xFF00FF)
        embed.set_image(url=image["link"])
        await self.client.say(embed=embed)

    @commands.command(pass_context=True, brief="[tag]")
    async def gif(self, ctx: commands.Context, *, tag: str):
        """Get a gif from Google with the wanted tag"""
        await self.client.send_typing(ctx.message.channel)

        image = await self.getRandomImage(tag, gif=True)

        if image == False:
            await self.client.reply(f"I couldn\"t get a gif with `{tag}`, sorry :<")
            return

        # Make a new embed message, set the image and send it
        embed = discord.Embed(title=f"Gif: `{tag}`", description=f"Requested by: {ctx.message.author.mention}", colour=0x00FFFF)
        embed.set_image(url=image["link"])
        await self.client.say(embed=embed)


def setup(client: commands.Bot):
    client.add_cog(Google(client))