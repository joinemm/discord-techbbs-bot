import discord
from discord.ext import commands, tasks
from modules import log, menus
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

logger = log.get_logger(__name__)


class TechBBS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fetch_loop.start()

    @commands.command()
    async def add(self, ctx, channel: discord.TextChannel, *, term):
        await self.bot.db.execute(
            "INSERT INTO search_term (term, guild_id, channel_id) VALUES (%s, %s, %s)",
            term,
            ctx.guild.id,
            channel.id,
        )
        await ctx.send(
            f':ok_hand: now searching for "{term}" and sending results to {channel.mention}'
        )

    @commands.command()
    async def remove(self, ctx, channel: discord.TextChannel, *, term):
        await self.bot.db.execute(
            "DELETE FROM search_term WHERE term = %s AND guild_id = %s AND channel_id = %s",
            term,
            ctx.guild.id,
            channel.id,
        )
        await ctx.send(f':ok_hand: no longer searching for "{term}" in {channel.mention}')

    @commands.command()
    async def list(self, ctx):
        filters = await self.bot.db.execute(
            "SELECT term, channel_id FROM search_term WHERE guild_id = %s", ctx.guild.id
        )
        rows = []
        for term, channel_id in filters:
            channel = ctx.guild.get_channel(channel_id)
            rows.append(f'"{term}" -> {channel.mention}')

        content = discord.Embed(title="Followed search terms")
        pages = menus.Menu(source=menus.ListMenu(rows, embed=content), clear_reactions_after=True)
        await pages.start(ctx)

    @tasks.loop(minutes=1)
    async def fetch_loop(self):
        try:
            results = await self.fetch_posts()
            await self.post_results(results)
        except Exception as e:
            logger.error("Unhandled exception in fetch loop")
            logger.error(e)
            return

    @fetch_loop.before_loop
    async def before_fetch_loop(self):
        await self.bot.wait_until_ready()
        logger.info("Starting fetch loop")

    async def post_results(self, threads):
        sent_threads = await self.bot.db.execute("SELECT thread_id FROM sent_thread")
        sent_threads = [r[0] for r in sent_threads]
        filters = await self.bot.db.execute("SELECT term, channel_id FROM search_term")
        if not filters:
            logger.info("no ones searching for anything")
        else:
            for thread in threads:
                if thread["id"] in sent_threads:
                    continue

                already_sent_to = []
                for term, channel_id in filters:
                    if channel_id in already_sent_to:
                        continue

                    if term.lower() in thread["title"].lower() or term.lower() == "all":
                        channel = self.bot.get_channel(channel_id)
                        logger.info(f"Sending thread {thread['id']} to {channel}")
                        content = discord.Embed(title=f"`[{thread['status']}]` {thread['title']}")
                        content.colour = (
                            int("00a600", 16)
                            if thread["status"] == "Myydään"
                            else int("f61010", 16)
                        )
                        content.description = thread["url"]
                        content.timestamp = datetime.utcfromtimestamp(thread["created_at"])
                        content.set_footer(text=f'{thread["id"]} | matched "{term}"')
                        await channel.send(embed=content)
                        already_sent_to.append(channel_id)

                await self.bot.db.execute("INSERT INTO sent_thread VALUES (%s)", thread["id"])

    async def fetch_posts(self):
        results = []
        base_url = "https://bbs.io-tech.fi"
        async with aiohttp.ClientSession() as session:
            url = "/forums/myydaeaen.80/"
            async with session.get(base_url + url) as response:
                data = await response.text()
                soup = BeautifulSoup(data, "html.parser")
                rows = soup.findAll("div", {"class": "structItem--thread"})
                for element in rows:
                    for c in element["class"]:
                        if "js-threadListItem" in c:
                            thread_id = int(c.split("-")[-1])
                    title = element.find("div", {"class": "structItem-title"}).findAll("a")[-1]
                    status = element.find("div", {"class": "structItem-title"}).find(
                        "span", {"class": "label"}
                    )
                    status = status.text if status is not None else None
                    timestamp = int(
                        element.find("li", {"class": "structItem-startDate"}).find("time")[
                            "data-time"
                        ]
                    )

                    results.append(
                        {
                            "id": thread_id,
                            "status": status,
                            "title": title.text,
                            "url": base_url + title["href"],
                            "created_at": timestamp,
                        }
                    )
        return results


def setup(bot):
    bot.add_cog(TechBBS(bot))
