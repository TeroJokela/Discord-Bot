from .helpers.error import sendErrorToOwner
from discord.ext import commands
import discord
import asyncio
import aiohttp
import random
import json
import os


class Mod(object):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(pass_context=True)
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    async def initialize(self, ctx: commands.Context):
        """Initialize the roles for this server. Requires administrator for the bot and user of the command user"""
        modRole = await self.client.create_role(ctx.message.server, name="Ter$kaMod")
        await self.client.say(f"Successfully created role `Ter$kaMod`!")

        # Make the muted role and add an overwrite to all channels to properly mute anyone with the role
        mutedPerms = discord.Permissions(send_messages=False, add_reactions=False, manage_messages=False, speak=False)
        mutedRole = await self.client.create_role(ctx.message.server, name="Ter$kaMuted", permissions=mutedPerms, colour=discord.Colour(0x551A8B))
        mutedOverwrite = discord.PermissionOverwrite(send_messages=False, add_reactions=False, manage_messages=False, speak=False)
        for i in ctx.message.server.channels:
            if i.type == discord.ChannelType.text or i.type == discord.ChannelType.voice:
                await self.client.edit_channel_permissions(i, mutedRole, mutedOverwrite)

        await self.client.say("Successfully created role `Ter$kaMuted`!")
        await self.client.say("Initialization done! c:")

    @initialize.error
    async def initialize_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.CheckFailure):
            await self.client.say("Either you or I are not administrators here :c")
        else:
            await sendErrorToOwner(self.client, err)

    @commands.command(pass_context=True, brief="[tag user]")
    @commands.has_role("Ter$kaMod")
    async def mute(self, ctx: commands.Context, user: discord.Member):
        """Mute an user from talking on the server"""
        await self.client.delete_message(ctx.message)
        await self.client.add_roles(user, discord.utils.get(ctx.message.server.roles, name="Ter$kaMuted"))
        await self.client.say(f"Successfully muted {user.mention}! c:<")
        # Move the user in voice channels so the mute is applied
        if user.voice_channel != None:
            # Get voice channels where the user is not in (also nice one-liner)
            possibleVoiceChannels = list(filter(lambda chnl: chnl.type == discord.ChannelType.voice and chnl != user.voice_channel, ctx.message.server.channels))
            await self.client.move_member(user, random.choice(possibleVoiceChannels))
            await self.client.move_member(user, user.voice_channel)

    @commands.command(pass_context=True, brief="[tag user]")
    @commands.has_role("Ter$kaMod")
    async def unmute(self, ctx: commands.Context, user: discord.Member):
        """Unmute an user in the server"""
        await self.client.delete_message(ctx.message)
        await self.client.remove_roles(user, discord.utils.get(ctx.message.server.roles, name="Ter$kaMuted"))
        await self.client.say(f"Successfully unmuted {user.mention}!")
        # Move the user in voice channels so the mute is applied
        if user.voice_channel != None:
            # Get voice channels where the user is not in (also nice one-liner)
            possibleVoiceChannels = list(filter(lambda chnl: chnl.type == discord.ChannelType.voice and chnl != user.voice_channel, ctx.message.server.channels))
            await self.client.move_member(user, random.choice(possibleVoiceChannels))
            await self.client.move_member(user, user.voice_channel)

    @commands.command(pass_context=True, brief="[tag user]")
    @commands.has_role("Ter$kaMod")
    async def kick(self, ctx: commands.Context, user: discord.Member):
        """Kick an user from the server"""
        await self.client.delete_message(ctx.message)
        await self.client.kick(user)
        await self.client.say(f"Successfully kicked `{str(user)}`!")

    @commands.command(pass_context=True, brief="[amount]", aliases=["clear", "purge"])
    @commands.has_role("Ter$kaMod")
    async def removeMessages(self, ctx: commands.Context, amount: int):
        """Remove an X amount of messages from the channel"""
        await self.client.delete_message(ctx.message)
        await self.client.purge_from(ctx.message.channel, limit=amount)
        msg = await self.client.say(f"Successfully removed `{abs(amount)}` messages!")
        await asyncio.sleep(5)
        await self.client.delete_message(msg)

    @mute.error
    @unmute.error
    @kick.error
    @removeMessages.error
    async def muteUnmuteKickPurge_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.CheckFailure):
            await self.client.reply("you don't have the `Ter$kaMod` role!")
        elif isinstance(err, commands.MissingRequiredArgument):
            if ctx.command.name == "removeMessages":
                await self.client.reply("you forgot to give me an amount... Baka...")
            else:
                await self.client.reply("you forgot to tag the person... Baka...")
        elif isinstance(err, commands.BadArgument):
            await self.client.reply("what the fuck is that argument..? Baka...")
        elif isinstance(err, commands.CommandInvokeError):
            if isinstance(err.original, discord.Forbidden):
                await self.client.reply("I'm don't have the permissions to kick people here >:[")
            elif isinstance(err.original, discord.HTTPException):
                await self.client.reply("`You can only bulk delete messages that are under 14 days old.` (_Discord restriction, blame them_)")                
        else:
            await sendErrorToOwner(self.client, err)

    @commands.command(pass_context=True, brief="[direct link to image] [name]")
    @commands.has_role("Ter$kaMod")
    async def createEmoji(self, ctx: commands.Context, imageURL: str, name: str):
        """Create a custom emoji. GIFs aren't supported ;_;"""
        async with aiohttp.ClientSession() as session:
            res = await session.get(url=imageURL)
            img = await res.read()
            # if img[:3] == b"GIF": -- discord.py's async version doesn't support GIFs... ;_;
            emoji = await self.client.create_custom_emoji(ctx.message.server, image=img, name=name)
            await self.client.say(f"{ctx.message.author.mention} -> {str(emoji)}")

    @createEmoji.error
    async def createEmoji_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.CheckFailure):
            await self.client.reply("you don't have the `Ter$kaMod` role!")
        elif isinstance(err, commands.MissingRequiredArgument):
            await self.client.say(f"{ctx.message.author.mention} you forgot something... Baka...")
        elif isinstance(err, commands.CommandInvokeError):
            if isinstance(err.original, discord.Forbidden):
                await self.client.reply("I don't have permissions to create emojis here >:(")
            elif isinstance(err.original, discord.HTTPException):
                await self.client.say(f"{ctx.message.author.mention} all the custom emoji slots are already in use... Baka...")
            else:
                await self.client.reply("I wasn't able to get an image from that URL... Are you sure it's a direct link?")
        else:
            await sendErrorToOwner(self.client, err)

    @commands.command(pass_context=True)
    @commands.has_role("Ter$kaMod")
    async def deleteEmoji(self, ctx: commands.Context):
        """Delete a custom emoji"""
        reactToThis = await self.client.say(f"React to this message with the custom emoji that you want to delete, {ctx.message.author.mention}!")
        customEmoji = await self.client.wait_for_reaction(user=ctx.message.author, message=reactToThis, timeout=60)
        await self.client.delete_custom_emoji(customEmoji.reaction.emoji)
        await self.client.reply(f"successfully deleted emoji `{customEmoji.reaction.emoji.name}`!")

    @deleteEmoji.error
    async def deleteEmoji_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.CheckFailure):
            await self.client.reply("you don't have the `Ter$kaMod` role!")
        elif isinstance(err, commands.CommandInvokeError):
            if "NoneType" in err.__str__(): # Nice hack
                await self.client.say(f"Time's up {ctx.message.author.mention}! You were too slow...")
            else:
                await self.client.reply("that's not a custom emoji! Baka!")
        else:
            await sendErrorToOwner(self.client, err)

    @commands.command(pass_context=True, brief="[tag user] [reason (optional)]")
    @commands.has_role("Ter$kaMod")
    async def warn(self, ctx: commands.Context, toWarn: discord.Member, *, reason="unspecified"):
        """Warn a user in the server"""
        await self.client.send_typing(ctx.message.channel)
        await self.client.delete_message(ctx.message)
        # Add the warning to our json file (better spaghetti producer than your favourite italian restaraunt)
        r = open(f"{os.getcwd()}/resources/warnings.json", "r")
        data = json.loads(r.read())
        r.close()
        if not ctx.message.server.id in data:
            data[ctx.message.server.id] = {}
        if not toWarn.id in data[ctx.message.server.id]:
            data[ctx.message.server.id][toWarn.id] = []
        data[ctx.message.server.id][toWarn.id].append(reason)
        w = open(f"{os.getcwd()}/resources/warnings.json", "w")
        json.dump(data, w)
        w.close()
        await self.client.say(f"{ctx.message.author.mention} has warned {toWarn.mention} for `{reason}`")

    @warn.error
    async def warn_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.MissingRequiredArgument):
            await self.client.reply("you're missing something... Baka...")
        elif isinstance(err, commands.BadArgument):
            await self.client.reply("what the fuck is that argument..? Baka...")
        elif isinstance(err, commands.CheckFailure):
            await self.client.reply("you don't have the `Ter$kaMod` role!")
        else:
            await sendErrorToOwner(self.client, err)

    @commands.command(pass_context=True, brief="[tag user]")
    async def warnings(self, ctx: commands.Context, target: discord.Member):
        """Show all warnings for a user"""
        await self.client.send_typing(ctx.message.channel)
        r = open(f"{os.getcwd()}/resources/warnings.json", "r")
        data = json.loads(r.read())
        try:
            warnings = data[ctx.message.server.id][target.id]
        except:
            await self.client.say(f"{target.mention} is a good lad and has behaved well! [0 warnings]")
        if len(warnings) == 0:
            await self.client.say(f"{target.mention} is a good lad and has behaved well! [0 warnings]")
            return
        msg = f"The user {target.mention} has `{len(warnings)}` warning{'s' if len(warnings) > 1 else ''}!```"
        for i in warnings:
            msg += f"{i}\n"
        await self.client.say(f"{msg}```")

    @warnings.error
    async def warnings_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.MissingRequiredArgument):
            await self.client.reply("you're missing something... Baka...")
        elif isinstance(err, commands.BadArgument):
            await self.client.reply("what the fuck is that argument..? Baka...")
        else:
            await sendErrorToOwner(self.client, err)

    @commands.command(pass_context=True, brief="[tag user]")
    @commands.has_role("Ter$kaMod")
    async def clearWarnings(self, ctx: commands.Context, toClear: discord.Member):
        """Clear all warnings for a user"""
        await self.client.send_typing(ctx.message.channel)
        await self.client.delete_message(ctx.message)
        # Clear the warnings in our json file (better spaghetti producer than your favourite italian restaraunt)
        r = open(f"{os.getcwd()}/resources/warnings.json", "r")
        data = json.loads(r.read())
        r.close()
        try:
            data[ctx.message.server.id][toClear.id] = []
        except:
            await self.client.say(f"{toClear.mention} is already a good lad! [No warnings]")
        w = open(f"{os.getcwd()}/resources/warnings.json", "w")
        json.dump(data, w)
        w.close()
        await self.client.say(f"{toClear.mention} is now a good lad! [Warnings cleared]")

    @clearWarnings.error
    async def clearWarnings_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.MissingRequiredArgument):
            await self.client.reply("you're missing something... Baka...")
        elif isinstance(err, commands.BadArgument):
            await self.client.reply("what the fuck is that argument..? Baka...")
        else:
            await sendErrorToOwner(self.client, err)

            
def setup(client: commands.Bot):
    client.add_cog(Mod(client))