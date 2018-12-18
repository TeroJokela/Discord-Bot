from discord.ext import commands
import discord
import random
import time


class Misc(object):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def ping(self):
        """Pong!"""
        startTime = time.time()
        msg = await self.client.say("Pong!")
        endTime = time.time() - startTime
        await self.client.edit_message(msg, new_content=f"Pong! :: {str(round(endTime, 2))}s")

    @commands.command(pass_context=True, brief="[max (100 without specifying)]")
    async def roll(self, ctx: commands.Context, maxNumber=100):
        """Get a random number"""
        await self.client.say(f"{ctx.message.author.mention} -> {random.randint(0, maxNumber)}")

    @roll.error
    async def roll_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.BadArgument):
            await self.client.reply("please give me whole numbers only c:")


def setup(client: commands.Bot):
    client.add_cog(Misc(client))