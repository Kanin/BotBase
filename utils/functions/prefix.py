import discord


async def get(bot, message):
    # Get default prefixes
    prefixes = [bot.user.mention + " "]
    prefixes.extend(bot.config.prefixes["debug"] if bot.debug else bot.config.prefixes["main"])

    if isinstance(message.channel, discord.TextChannel):
        guild = message.guild

        # Nicks are different mentions
        if guild.get_member(bot.user.id).nick:
            prefixes.append(guild.me.mention + " ")

    # Now that we have the list, let's try to see if it's in the message, if not we just return the entire list
    for prefix in prefixes:
        if message.content.lower().startswith(prefix):
            return message.content[:len(prefix)]
    return prefixes
