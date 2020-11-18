from discord.ext import commands


async def global_cooldown(ctx):
    """Global bot cooldown to prevent spam."""
    bucket = ctx.bot.global_cd.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()
    if retry_after:
        raise commands.CommandOnCooldown(bucket, retry_after)
    else:
        return True
