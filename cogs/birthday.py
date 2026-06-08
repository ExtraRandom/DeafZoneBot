import discord
from discord import Option, OptionChoice, AutocompleteContext
from discord.ext import commands

from cogs.utils import role_lookup
from cogs.data import constants


class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name="birthday")
    async def give_birthday_role(
            self,
            ctx: discord.ApplicationContext,
            user: Option(discord.User , description="user", required=True),
 ):
        """Birthday"""
        # check server


        await ctx.respond(f"user {user}")

def setup(bot):
    bot.add_cog(Birthday(bot))
