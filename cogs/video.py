from .helpers.error import sendErrorToOwner
from discord.ext.commands.cooldowns import BucketType
from discord.ext import commands
from moviepy.editor import *
import os


class Video(object):
    def __init__(self, client: commands.Bot):
        self.client = client

    def makeCrabRave(self, text: str, userID: str):
        video = VideoFileClip("./resources/Crab Rave.mp4")
        textVideo = TextClip(text, fontsize=100, font="Comic-Sans-MS", color="white", stroke_color="black", stroke_width=4).set_position("center").set_duration(15)
        finishedVideo = CompositeVideoClip([video, textVideo])
        finishedVideo.write_videofile(f"Crab_Rave_{userID}.mp4", temp_audiofile=f"Crab_Rave_audio_{userID}.mp3", preset="ultrafast", bitrate="4000k", verbose=False, progress_bar=False) 
        
    @commands.command(pass_context=True, brief="[wanted text]")
    @commands.cooldown(1, 60, BucketType.user)
    async def crabrave(self, ctx: commands.Context, *, text: str):
        """Make a dead meme"""
        userID = ctx.message.author.id
        await self.client.say(f"{ctx.message.author.mention} making your clip... Hold on... _(This should take only ~20 seconds)_")
        await self.client.loop.run_in_executor(None, self.makeCrabRave, text, userID)
        await self.client.send_file(ctx.message.channel, f"Crab_Rave_{userID}.mp4", content=f"Here's your clip, {ctx.message.author.mention}:")
        os.remove(f"Crab_Rave_{userID}.mp4")

    @crabrave.error
    async def crabrave_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.CommandOnCooldown):
            await self.client.say(f"{ctx.message.author.mention} {str(err)}")
        elif isinstance(err, commands.MissingRequiredArgument):
            await self.client.say(f"{ctx.message.author.mention} you forgot something... Baka...")
        else:
            await sendErrorToOwner(self.client, err)


def setup(client: commands.Bot):
    client.add_cog(Video(client))