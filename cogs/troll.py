from discord.ext import commands
from .helpers import checks
import discord


class Troll(object):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(pass_context=True, brief="[message]")
    @commands.check(checks.isCreator)
    async def tts(self, ctx: commands.Context, *, toSay: str):
        """Send a text-to-speech message"""
        await self.client.delete_message(ctx.message)
        msg = await self.client.say(toSay, tts=True)
        await self.client.delete_message(msg)


def setup(client: commands.Bot):
    client.add_cog(Troll(client))