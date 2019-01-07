from discord.ext import commands
import datetime
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

    @commands.command(pass_context=True)
    async def coinflip(self, ctx: commands.Context):
        """Roll a coin"""
        res = random.choice(["heads", "tails"])
        await self.client.say(f"{ctx.message.author.mention} -> {res}")

    @commands.command(pass_context=True)
    async def battleroyale(self, ctx: commands.Context):
        """The truth about battleroyale"""
        await self.client.reply("UwU battleroyale gamemodes **SUCK**! OwO :3 Rawr") # I'm not a furry I swear to god

    @commands.command(pass_context=True, brief="[tag user]")
    async def love(self, ctx: commands.Context, toCompare: discord.User):
        """Tells you how much love there is between you and someone else"""
        if int(toCompare.id) > int(ctx.message.author.id):
            percentage = int(ctx.message.author.id) / int(toCompare.id)
        else:
            percentage = int(toCompare.id) / int(ctx.message.author.id)
        percentage *= 100
        percentage = round(percentage, 2)
        loveHeart = [":broken_heart:", ":heart:", ":sparkling_heart:", ":heartpulse:", ":cupid:"][round(percentage / 25)]
        embed = discord.Embed(colour=0xFF69B4)
        embed.set_author(name="❤️ Love calculator ❤️")
        embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y at %H:%M"))
        embed.add_field(name=f"{ctx.message.author} {loveHeart} {toCompare}", value=f"There's `{percentage}%` love between you two!")
        await self.client.say(embed=embed)

    @love.error
    async def love_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.MissingRequiredArgument):
            await self.client.say(f"{ctx.message.author.mention} you forgot something... Baka...")
        elif isinstance(err, commands.BadArgument):
            await self.client.say(f"{ctx.message.author.mention} what the fuck are you doing? Baka...")
            
    @commands.command(pass_context=True)
    async def serverInfo(self, ctx: commands.Context):
        """Get information about the server"""
        await self.client.send_typing(ctx.message.channel)
        server = ctx.message.server
        botCount = len(list(filter(lambda member: member.bot, server.members)))
        adminsCount = len(list(filter(lambda member: member.server_permissions.administrator, server.members)))
        serverCreationTime = datetime.datetime.utcnow() - server.created_at
        ordinal = lambda n: "%d%s" % (n, "tsnrhtdd" [(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4]) # Shoutout to Fartemis_ on Twitch for this <3
        embed = discord.Embed(colour=0x00FF00)
        embed.set_author(name=str(server), icon_url=server.icon_url)
        embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y at %H:%M"))
        embed.add_field(name="ID", value=server.id, inline=True)
        embed.add_field(name="Owner", value=server.owner.mention, inline=True)
        embed.add_field(name="Channel count", value=len(server.channels), inline=True)
        embed.add_field(name="Admin count", value=adminsCount, inline=True)
        embed.add_field(name="Member count", value=server.member_count, inline=True)
        embed.add_field(name="Bot count", value=botCount, inline=True)
        embed.add_field(name="Emoji count", value=len(server.emojis), inline=True)
        embed.add_field(name="Role count", value=len(server.roles) - 1, inline=True)
        embed.add_field(name="Region", value=str(server.region), inline=True)
        embed.add_field(name="Large", value=server.large, inline=True)
        embed.add_field(name="Creation time", value=f"{ordinal(server.created_at.day)} of {server.created_at.strftime('%B, %Y')} ({serverCreationTime.days} days ago)", inline=True)
        await self.client.say(embed=embed)

    @commands.command(pass_context=True, brief="[tag user]")
    async def userInfo(self, ctx: commands.Context, user: discord.Member):
        """Get information about a user"""
        await self.client.send_typing(ctx.message.channel)
        ordinal = lambda n: "%d%s" % (n, "tsnrhtdd" [(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4]) # Shoutout to Fartemis_ on Twitch for this <3
        userCreationTime = datetime.datetime.utcnow() - user.created_at
        userJoinTime = datetime.datetime.utcnow() - user.joined_at
        avatarURL = user.avatar_url if user.avatar_url else user.default_avatar_url
        colour = user.top_role.colour.value if user.top_role.colour.value else 0xFFFFFF
        embed = discord.Embed(colour=colour)
        embed.set_author(name=str(user), icon_url=avatarURL)
        embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y at %H:%M"))
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Bot", value=user.bot, inline=True)
        if user.nick:
            embed.add_field(name="Nick", value=user.nick, inline=True)
        if ctx.message.server.owner == user:
            embed.add_field(name="Owner", value="True", inline=True)
        else:
            embed.add_field(name="Admin", value=user.server_permissions.administrator, inline=True)
        embed.add_field(name="Status", value=user.status, inline=True)
        if user.game != None:
            mode = ["playing", "streaming", "listening", "watching"][user.game.type]
            embed.add_field(name="Game", value=f"\"{mode}\" {user.game.name}", inline=True)
        embed.add_field(name="Account creation time", value=f"{ordinal(user.created_at.day)} of {user.created_at.strftime('%B, %Y')} ({userCreationTime.days} days ago)", inline=True)
        embed.add_field(name="Joining time", value=f"{ordinal(user.joined_at.day)} of {user.joined_at.strftime('%B, %Y')} ({userJoinTime.days} days ago)", inline=True)
        await self.client.say(embed=embed)

    @userInfo.error
    async def userInfo_eh(self, err: Exception, ctx: commands.Context):
        if isinstance(err, commands.BadArgument):
            await self.client.reply("you need to tag a user... Baka...")
        elif isinstance(err, commands.MissingRequiredArgument):
            await self.client.reply("you forgot something... Baka...")


def setup(client: commands.Bot):
    client.add_cog(Misc(client))