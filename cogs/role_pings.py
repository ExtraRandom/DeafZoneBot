import discord
from discord import Option, OptionChoice, AutocompleteContext
from discord.ext import commands

from cogs.utils import role_lookup
from cogs.data import constants


class RolePing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def lfg_autocomplete(self, ctx: AutocompleteContext):
        final = []

        # print(ctx.value.lower())

        data = role_lookup.game_roles_basic
        for game in data.keys():
            # print(game)
            if game is not None:
                if ctx.value.lower() in game.lower():
                    final.append(OptionChoice(name=game, value=data[game]))

            if len(final) >= 20:
                break

        return final

    @commands.slash_command(name="lfg")
    async def ping_gaming(
            self,
            ctx: discord.ApplicationContext,
            role: Option(str, description="The role to ping", required=True, autocomplete=lfg_autocomplete),
            info: Option(str, "Add some info about the game", required=True),
    ):
        # check which guild we are in and set lookup based on it
        current_guild = ctx.guild.id

        if current_guild == constants.testing_guild_id:
            lookup_string = "testing_role_id"
        elif current_guild == constants.deafzone_guild_id:
            lookup_string = "deafzone_role_id"
        else:
            await ctx.respond("This server is not set up for use with this command.")
            return

        # get role info
        try:
            role_info = role_lookup.game_roles[role]
        except KeyError:
            await ctx.respond(f"There is no '{role}' role currently.")
            return

        # form the message and send it
        await ctx.respond(
            f"{ctx.user.mention} is looking to play <@&{role_info[lookup_string]}> ({role_info['game_name_full']})!"
            f"\nAdditional Info: {info}")


    @commands.slash_command(name="lfg_test", default_member_permissions=discord.Permissions(manage_roles=True))
    async def lfg_test(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        # check which guild we are in and set lookup based on it
        current_guild = ctx.guild.id

        if current_guild == constants.testing_guild_id:
            lookup_string = "testing_role_id"
        elif current_guild == constants.deafzone_guild_id:
            lookup_string = "deafzone_role_id"
        else:
            await ctx.respond("This server is not set up for use with this command.")
            return

        msg = ""

        for game in role_lookup.game_roles_basic.keys():
            # print(game)

            game_info = role_lookup.game_roles[role_lookup.game_roles_basic[game]]
            msg += f"{game_info['game_name_full']} - <@&{game_info[lookup_string]}>\n"

        await ctx.respond(msg)
        return


def setup(bot):
    bot.add_cog(RolePing(bot))
