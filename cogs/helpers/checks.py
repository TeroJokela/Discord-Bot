from discord.ext import commands


def isCreator(ctx: commands.Context):
    return ctx.message.author.id == "191608800619266048"