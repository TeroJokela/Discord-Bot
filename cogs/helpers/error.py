from discord.ext import commands


async def sendErrorToOwner(client: commands.Bot, err: Exception):
    owner = await client.get_user_info("191608800619266048")
    await client.send_message(owner, f"`{type(err).__name__}`\n```\n{err}```")