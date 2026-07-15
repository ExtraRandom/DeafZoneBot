import discord
from aiohttp.web_routedef import delete
from discord import Option, OptionChoice, AutocompleteContext, Interaction
from discord.ext import commands, tasks

from cogs.utils import role_lookup
from cogs.data import constants

import datetime

import mongo, time

TIMEOUT = 30  # view timeout (in seconds)
AUTO_DELETE_SHORT = 15
AUTO_DELETE_LONG = 30

class RolePing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_loop.start()

        self.channel_for_ping_id = 1505872906666905670

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

    @tasks.loop(seconds=5)
    async def check_loop(self):
        if self.bot.is_ready():
            # print("practice check")
            now = int(time.time())
            query = {"ts": {"$lte": now}}
            res = mongo.col_practice.find(query)
            if res is None:
                return

            channel = await self.bot.fetch_channel(self.channel_for_ping_id)
            for r in res:
                print(r)
                await channel.send(f"<@role ping> '{r['what']}' practice scheduled by <@{r['_id']}> begins now! "
                                   f"\n-# <t:{r['ts']}:R>")
                mongo.col_practice.delete_one(r)

    class ExistingPracticeView(discord.ui.DesignerView):
        class ExistingRow(discord.ui.ActionRow):
            @discord.ui.button(label="Leave as is", style=discord.ButtonStyle.green)
            async def leave_callback(self, button, interaction):
                await self.parent.remove()
                self.parent.stop()
                await interaction.response.send_message("Scheduled practice was not changed or deleted",
                                                        delete_after=AUTO_DELETE_SHORT, ephemeral=True)

            @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
            async def delete_callback(self, button, interaction):
                existing = mongo.check_for_existing_practice(interaction.user.id)
                mongo.col_practice.delete_one(existing)
                await interaction.message.edit(
                    content=f"The following Practice ping was ***deleted***:\n"
                            f"**What?:** {existing['what']}\n"
                            f"**When?:** <t:{existing['ts']}:F>\n"
                            f"**Who?:** <@{existing['_id']}> ")
                await self.parent.remove()
                self.parent.stop()
                await interaction.respond("Scheduled Practice was deleted!\n"
                                          "Run the `/practice` command again to schedule a new practice ping.",
                                          delete_after=AUTO_DELETE_SHORT, ephemeral=True)

            """
            @discord.ui.button(label="Delete and create new", style=discord.ButtonStyle.danger)
            async def delete_existing_callback(self, button, interaction):
                await interaction.message.reply("will delete the original at some point okie dokie", ephemeral=True)
                # await interaction.response.send_message("you clicked delete existing", ephemeral=True)
                await self.parent.remove()
                m = RolePing.PractiseModal()
                await interaction.response.send_modal(m)
            """

        def __init__(self):
            super().__init__(timeout=TIMEOUT)
            my_row = self.ExistingRow() #RolePing.ExistingRow()
            self.add_item(my_row)

        async def on_timeout(self) -> None:
            # await self.parent.message.delete()
            await self.parent.respond("Interaction timed out, Scheduled practice was not changed or deleted",
                                      delete_after=AUTO_DELETE_SHORT)
            self.disable_all_items()
            await self.parent.edit(view=self, delete_after=1)

        async def remove(self):
            self.disable_all_items()
            await self.parent.edit(view=self)

    class PractiseModal(discord.ui.DesignerModal):
        def __init__(self,
                     prefill_text: str | None = None,
                     prefill_hours: int | None = None,
                     prefill_minutes: int | None = None):
            super().__init__(title="test")

            self.input_language = discord.ui.Label(
                "What do you want to practise?",
                discord.ui.InputText(
                    placeholder="ASL, BSL....?",
                    value=prefill_text or ""
                ),
                description="Which Sign Language and what topics to practice?"
            )

            self.add_item(self.input_language)

            hours: list[discord.SelectOption] = []
            for i in range(25):
                hours.append(discord.SelectOption(label=f"{i}", value=f"{i}", default=(str(i) == prefill_hours)))


            self.input_hours = discord.ui.Label(
                "In how many hours from now?",
                discord.ui.Select(
                    options=hours
                ),
                description="How many hours from the current time should the practice be? E.g. 1 = 1 hour from now"
            )
            self.add_item(self.input_hours)

            mins = [0,1,5,10,15,20,25,30,35,40,45,50,55]
            minutes: list[discord.SelectOption] = []

            for minn in mins:
                minutes.append(discord.SelectOption(label=f"{minn}", value=f"{minn}", default=(str(minn) == prefill_minutes)))

            self.input_minutes = discord.ui.Label(
                "In how many minutes from now?",
                discord.ui.Select(options=minutes),
                description="How many minutes from current time should the practice be? E.g. 10 = 10 minutes from now (+ hours)"
            )
            self.add_item(self.input_minutes)

        async def callback(self, interaction: Interaction):
            now = datetime.datetime.now(datetime.UTC)
            now = now.replace(microsecond=0)

            hours = self.input_hours.item.values[0]
            mins = self.input_minutes.item.values[0]

            then = now + datetime.timedelta(hours=int(hours), minutes=int(mins))

            doc = {
                "_id": str(interaction.user.id),
                "ts": int(then.timestamp()),
                "what": self.input_language.item.value
            }
            print(doc)


            confirm = RolePing.ConfirmationView(doc, hours, mins, interaction.user.id)
            await interaction.response.send_message(f"<@{interaction.user.id}> You are scheduling a practice ping:\n"
                                                    f"**What?:** {doc['what']}\n"
                                                    f"**When?:** <t:{doc['ts']}:F> (<t:{doc['ts']}:R>). \n"
                                                    f"Is this information correct?\n"
                                                    f"-# This interaction will automatically timeout in 30 seconds", view=confirm)


    class ConfirmationView(discord.ui.DesignerView):
        class ConfirmRow(discord.ui.ActionRow):
            @discord.ui.button(label="Yes, it is correct", style=discord.ButtonStyle.green)
            async def confirm(self, button, interaction):
                await interaction.response.send_message("Confirmed", delete_after=15)
                await self.parent.remove()
                self.parent.stop()
                print("add doc: ", self.parent.doc)
                mongo.col_practice.insert_one(self.parent.doc)

            @discord.ui.button(label="No, I need to edit it", style=discord.ButtonStyle.danger)
            async def do_not_confirm_callback(self, button, interaction):
                # await interaction.message.reply("will delete the original at some point okie dokie", delete_after=15)
                await self.parent.remove()
                await interaction.message.delete()
                self.parent.stop()
                m = RolePing.PractiseModal(self.parent.doc['what'], self.parent.hours, self.parent.mins)
                await interaction.response.send_modal(m)

        def __init__(self, doc, hours, mins, user_id: int):
            super().__init__(timeout=TIMEOUT)
            my_row = self.ConfirmRow()
            self.add_item(my_row)

            self.doc = doc
            self.hours = hours
            self.mins = mins

            self.user_id = user_id

        async def interaction_check(self, interaction: Interaction) -> bool:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(f"These buttons can only be used by <@{self.user_id}>", ephemeral=True)
                return False
            return True

        async def on_timeout(self) -> None:
            self.disable_all_items()
            await self.parent.edit(content="Timed out before confirmation, no practice has been scheduled.\n"
                                           "-# Message will auto delete in 30 seconds",
                                   view=self, delete_after=AUTO_DELETE_LONG)

        async def remove(self):
            self.disable_all_items()
            await self.parent.edit(view=self)


    @commands.slash_command(name="practice")
    async def practise(self, ctx: discord.ApplicationContext):
        testing_id = 1525770074059702373

        check = mongo.check_for_existing_practice(ctx.user.id)
        if check is not None:
            existing_view = self.ExistingPracticeView()
            await ctx.respond(
                f"<@{check['_id']}> You already have a practice ping scheduled.\n"
                f"**What?:** {check['what']}\n"
                f"**When?:** <t:{check['ts']}:F> (<t:{check['ts']}:R>)\n"
                f"-# Interaction will automatically timeout in 30 seconds",
                view=existing_view)

            return


        modal = self.PractiseModal()
        await ctx.send_modal(modal)


def setup(bot):
    b = RolePing(bot)
    bot.add_cog(b)
