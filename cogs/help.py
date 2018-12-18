from discord.ext import commands
from .helpers import checks
import discord


class Help(object):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(pass_context=True)
    async def help(self, ctx: commands.Context):
        """Rapes neko lolis with tentacles... What did you expect? >.<"""
        commandsText = f"Here are all the commands, {ctx.message.author.mention}:```css\n"

        for name, cmd in self.client.commands.items():
            # Ignore aliases
            if name != cmd.name:
                continue

            # Don't show these cogs' commands if the help asker isn't me (Helmerz)
            if cmd.cog_name in ["Helmerz", "Troll"] and not checks.isCreator(ctx):
                continue

            # Is the cog already stated in the list?
            if f".{cmd.cog_name}\n" not in commandsText:
                commandsText += f".{cmd.cog_name}\n"
            
            commandsText += f"    ~{cmd.name} "
            commandsText += f"{cmd.brief} " if cmd.brief != None else ""
            commandsText += f"/* {cmd.help} */\n"

        await self.client.say(commandsText + "```")


def setup(client: commands.Bot):
    client.add_cog(Help(client))