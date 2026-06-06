import discord
from discord import Option, OptionChoice, AutocompleteContext
from discord.ext import commands

from cogs.utils import role_lookup
from cogs.data import constants


class How(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    how = discord.commands.SlashCommandGroup("how", "Help commands")

    @how.command(name="approve", default_member_permissions=discord.Permissions(manage_roles=True))
    async def how_approve(self, ctx: discord.ApplicationContext):
        """Help for the approve commands"""
        msg = ("# Using the approve commands\n"
               "\n"
               "There are a few different ways to use the approve commands.\n\n"
               "## /approve\n"
               "The easiest is `/approve`, when used within the intro thread this will approve the user, and "
               "automatically send a message containing their User ID and Intro message."
               "\n\n"
               "## /approve_user\n"
               "If for some reason the `/approve` command fails, then you can use `/approve_user <user>` instead.\n"
               "It requires a user to be given as an input, and will then approve the given user and send a message "
               "containing their ID. Unlike the main `/approve` command can't automatically include their intro message, "
               "so that will still need to be copied manually."
               "\n\n"
               "## User Command -> Approve User\n"
               "This functions identically to `/approve_user` except for its method of activation. \nOn Desktop, "
               "right click the username or profile picture of the user to approve, click 'Apps' "
               "and then 'Deaf Zone Bot', finally click Approve User.\nIf you have used the command previously, it may"
               "appear without needing to first navigate into the 'Deaf Zone Bot' sub menu.\n"
               "On Mobile, tap the users profile picture, or long tap on their username, Click the `...` in the top "
               "right corner, and then Apps. From here you find the command the same as on desktop.")
        await ctx.respond(msg)

def setup(bot):
    bot.add_cog(How(bot))
