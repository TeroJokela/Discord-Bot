from discord.ext import commands
from .helpers import checks
import discord
import os


# No error handlers for these commands, because I want these to be "secret"
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

    def leaveVoice(self, _voice: discord.VoiceClient):
        coro = _voice.disconnect()
        fut = discord.compat.run_coroutine_threadsafe(coro, self.client.loop)
        fut.result()

    @commands.command(pass_context=True, brief="[channel ID]")
    @commands.check(checks.isCreator)
    async def earrape(self, ctx: commands.Context, channelID: str):
        """Earrape everyone in a voice channel"""
        channel = self.client.get_channel(channelID)
        if channel.type != discord.ChannelType.voice:
            return
        voice = await self.client.join_voice_channel(channel)
        player = voice.create_ffmpeg_player(f"{os.getcwd()}/resources/earrape.mp3", after=lambda: self.leaveVoice(voice))
        player.volume = 2.0
        player.start()
        await self.client.delete_message(ctx.message)


def setup(client: commands.Bot):
    client.add_cog(Troll(client))