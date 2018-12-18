from discord.ext import commands
import discord
import aiohttp
import random


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

        await self.client.say(f"Successfully created role `Ter$kaMuted`!")
        await self.client.say("Initialization done! c:")

    @initialize.error
    async def initialize_eh(self, err, ctx: commands.Context):
        if isinstance(err, commands.CheckFailure):
            await self.client.say(f"Either you or I are not administrators here :c")
        else:
            print(f"Error {type(err).__name__}: {err}")

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
        await self.client.say(f"Successfully removed `{abs(amount)}` messages!")

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
            if "HTTPException" in err.__str__(): # Nice hack
                await self.client.reply("all the custom emoji slots are already in use!")
            elif "FORBIDDEN" in err.__str__():
                await self.client.reply("I don't have permissions to create emojis here >:(")
            else:
                await self.client.reply("I wasn't able to get an image from that URL... Are you sure it's a direct link?")

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


def setup(client: commands.Bot):
    client.add_cog(Mod(client))