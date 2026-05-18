from discord.ext import commands
import discord
import random


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="pick",
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        }
    )
    async def pick_random(self, ctx,
                          first_option: discord.Option(str, "The first option to pick from", required=True),
                          second_option: discord.Option(str, "The second option to pick from", required=True),
                          third_option: discord.Option(str, "The third option to pick from", required=False),
                          fourth_option: discord.Option(str, "The fourth option to pick from", required=False),
                          fifth_option: discord.Option(str, "The fifth option to pick from", required=False),
                          sixth_option: discord.Option(str, "The sixth option to pick from", required=False),
                          seventh_option: discord.Option(str, "The seventh option to pick from", required=False),
                          eighth_option: discord.Option(str, "The eighth option to pick from", required=False),
                          ninth_option: discord.Option(str, "The ninth option to pick from", required=False),
                          tenth_option: discord.Option(str, "The tenth option to pick from", required=False),
                          ):
        """Pick something from given options"""

        choice_list = [first_option, second_option]
        if third_option is not None:
            choice_list.append(third_option)

        if fourth_option is not None:
            choice_list.append(fourth_option)

        if fifth_option is not None:
            choice_list.append(fifth_option)

        if sixth_option is not None:
            choice_list.append(sixth_option)

        if seventh_option is not None:
            choice_list.append(seventh_option)

        if eighth_option is not None:
            choice_list.append(eighth_option)

        if ninth_option is not None:
            choice_list.append(ninth_option)

        if tenth_option is not None:
            choice_list.append(tenth_option)

        random.seed()
        await ctx.respond("{}".format(random.choice(choice_list)))


def setup(bot):
    bot.add_cog(Fun(bot))
