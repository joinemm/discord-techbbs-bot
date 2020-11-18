import discord
from discord.ext import commands
from modules import log

logger = log.get_logger(__name__)


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Get the bot's ping."""
        pong_msg = await ctx.send(":ping_pong:")
        sr_lat = (pong_msg.created_at - ctx.message.created_at).total_seconds() * 1000
        content = discord.Embed(color=discord.Colour.red())
        content.add_field(
            name=":heartbeat: Heartbeat", value=f"`{self.bot.latency * 1000:.1f}`ms", inline=False
        )
        content.add_field(name=":handshake: ACK", value=f"`{sr_lat}`ms", inline=False)
        await pong_msg.edit(content=None, embed=content)

    @commands.command(name="db", aliases=["dbe", "dbq"])
    @commands.is_owner()
    async def database_query(self, ctx, *, statement):
        """Execute something against the local MariaDB instance."""
        data = await self.bot.db.execute(statement)
        await ctx.send(f"```py\n{data}\n```")


def setup(bot):
    bot.add_cog(Commands(bot))
