from discord.ext import commands
import re
from cogs.utils import time_formatting as timefmt, IO
import datetime
from cogs.utils import perms
import discord

from zoneinfo import ZoneInfo

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.pacific_usa_tz = ZoneInfo("America/Los_Angeles")
        self.pacific_usa_desc = "West Coast USA"

        self.eastern_usa_tz = ZoneInfo("America/New_York")
        self.eastern_usa_desc = "East Coast USA"

        self.england_tz = ZoneInfo("Europe/London")
        self.england_desc = "The UK"

        self.central_europe_tz = ZoneInfo("Europe/Warsaw")
        self.central_europe_desc = "Central Europe"

        self.time_format = "%H:%M %Z" # "%I:%M%p %Z"

    @staticmethod
    def get_gmt_offset_neat(time: datetime.datetime, timezone):
        offset = time.astimezone(timezone).strftime("%z")



    @commands.slash_command(name="timezones")
    async def timezone_info(self, ctx):
        await ctx.defer()

        now = datetime.datetime.now()

        now_pacific = now.astimezone(self.pacific_usa_tz).strftime(self.time_format)
        now_eastern = now.astimezone(self.eastern_usa_tz).strftime(self.time_format)
        now_england = now.astimezone(self.england_tz).strftime(self.time_format)
        now_central = now.astimezone(self.central_europe_tz).strftime(self.time_format)

        msg = (f"{now_pacific} | {self.pacific_usa_desc}\n"
               f"{now_eastern} | {self.eastern_usa_desc}\n"
               f"{now_england} | {self.england_desc}\n"
               f"{now_central} | {self.central_europe_desc}\n"
               f"\n"
               f"<t:{str(now.timestamp()).split(".")[0]}:t> | Your Timezone\n")

        await ctx.respond(msg)

def setup(bot):
    bot.add_cog(General(bot))
