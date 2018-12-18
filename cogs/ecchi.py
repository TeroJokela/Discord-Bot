from discord.ext import commands
import discord
import aiohttp
import random


class Ecchi(object):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(pass_context=True)
    async def ecchi(self, ctx: commands.Context):
        """Posts an ecchi picture from 4chan/e/"""
        await self.client.send_typing(ctx.message.channel)

        async with aiohttp.ClientSession() as session:
            res = await session.get("http://a.4cdn.org/e/catalog.json")
            res = await res.json()
            
            # Add all the images to our list
            images = []
            for i in res[0]["threads"]:
                images.append(f'http://i.4cdn.org/e/{i["tim"]}{i["ext"]}') # I hate how this needs to be in single quotes >:(
                if "last_replies" in i:
                    for j in i["last_replies"]:
                        if "filename" in j:
                            images.append(f'http://i.4cdn.org/e/{j["tim"]}{j["ext"]}') # I hate how this also needs to be in single quotes >:o

            # Make a new embed message, set the image and send it
            embed = discord.Embed(title="Ecchi", description=f"Requested by: {ctx.message.author.mention}", colour=0x312952)
            embed.set_image(url=random.choice(images))
            await self.client.say(embed=embed)


def setup(client: commands.Bot):
    client.add_cog(Ecchi(client))