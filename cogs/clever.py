from discord.ext import commands
import discord
import aiohttp


class Clever(object):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.cleverKey = client.cfgParser.get("cleverbot", "key")
        self.cleverUser = client.cfgParser.get("cleverbot", "user")
        client.getResponse = self.getResponse # lmao no fucking way this works (I can use this in the main file now)

    async def getResponse(self, message: str):
        body = {
            "user": self.cleverUser,
            "key": self.cleverKey,
            "nick": "Ter$kaBot",
            "text": message
        }

        async with aiohttp.ClientSession() as session:
            res = await session.post("https://cleverbot.io/1.0/ask", data=body)
            # Was our session ever initialized?
            if (res.status == 400):
                async with aiohttp.ClientSession() as session:
                    await session.post("https://cleverbot.io/1.0/create", data=body)
                    # Bad recursion, I know...
                    return await self.getResponse(message)

            res = await res.json()
            return res["response"]

    @commands.command(pass_context=True, brief="[message]")
    async def answer(self, ctx: commands.Context, *, msg: str):
        """Talk with the bot. You can also just tag the bot and then send your message"""
        await self.client.send_typing(ctx.message.channel)
        answer = await self.getResponse(msg)
        await self.client.say(f"{ctx.message.author.mention} {answer}")


def setup(client: commands.Bot):
    client.add_cog(Clever(client))