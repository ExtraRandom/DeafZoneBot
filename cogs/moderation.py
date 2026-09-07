from discord.ext import commands
import datetime

import mongo
from cogs.utils import perms
from cogs.utils import time_formatting as timefmt, ez_utils
from cogs.utils.logger import Logger
import discord
import re
import os



class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class ActionModal(discord.ui.DesignerModal):
        def __init__(self,
                     log_channel: discord.TextChannel,
                     passed_message: discord.Message | None = None):
            super().__init__(title="Action Form")

            self.log_channel = log_channel

            if passed_message:
                self.input_user = discord.ui.Label(
                    "User",
                    discord.ui.UserSelect(required=True, default_values=[passed_message.author]),
                )
            else:
                self.input_user = discord.ui.Label(
                    "User",
                    discord.ui.UserSelect(required=True,),
                )
            self.add_item(self.input_user)


            self.input_action_taken = discord.ui.Label(
                "What action was taken?",
                discord.ui.InputText(required=True, style=discord.InputTextStyle.long, max_length=3000),
            )
            self.add_item(self.input_action_taken)


            self.input_image = discord.ui.Label(
                "Screenshot (Optional)",
                discord.ui.FileUpload(required=False)
            )
            self.add_item(self.input_image)


            self.input_message_url = discord.ui.Label(
                "Link to Message for Context (Optional)",
                discord.ui.TextInput(required=False, value=passed_message.jump_url if passed_message else ''),
            )
            self.add_item(self.input_message_url)


        async def callback(self, interaction: discord.Interaction):
            user: discord.User = self.input_user.item.values[0]
            action = self.input_action_taken.item.value

            image = self.input_image.item.values[0] if self.input_image.item.values else None

            url = self.input_message_url.item.value if self.input_message_url.item.value else None

            embed = discord.Embed(
                title="Staff Action Report",
                description=f"**Action:** {action}",
                # description="Action taken by {}".format(interaction.user),
                color=discord.Color.red(),
            )
            embed.set_author(name=user.display_name, icon_url=user.display_avatar)
            embed.set_footer(text=f"Action Taken by {interaction.user.display_name}", icon_url=interaction.user.display_avatar)

            # embed.add_field(name="Action Description", value=action)
            embed.add_field(name="Taken Against", value=f"{str(user)}\n{user.mention}")
            now = datetime.datetime.now()
            embed.timestamp = now

            if image:
                embed.set_image(url=image)
            if url:
                embed.add_field(name="Message Link", value=str(url))

            msg = await self.log_channel.send(embed=embed)

            await interaction.response.send_message(f"Action Report posted here: {msg.jump_url}", ephemeral=True)

    # https://docs.pycord.dev/en/master/api/data_classes.html#discord.Permissions
    @commands.slash_command(name="setup", default_member_permissions=discord.Permissions(manage_roles=True, manage_messages=True))
    async def setup(self, ctx):
        modal = mongo.ChannelUpdateModal(ctx.guild.id)
        await ctx.send_modal(modal)

    @commands.slash_command(name="actionform")
    async def action_form(self, ctx):
        """staff action form"""
        channel_id = mongo.get_channel(ctx.guild.id, mongo.CHANNELS.ACTION_REPORTS.value)
        if channel_id is None:
            await ctx.respond(f"{ mongo.CHANNELS.ACTION_REPORTS.value } channel not set")
            return

        action_form_channel = await self.bot.fetch_channel(int(channel_id))

        modal = self.ActionModal(action_form_channel)
        await ctx.send_modal(modal)

    @commands.message_command(name="msgactionform")
    async def message_action_form(self, ctx, message: discord.Message):
        channel_id = mongo.get_channel(ctx.guild.id, mongo.CHANNELS.ACTION_REPORTS.value)
        if channel_id is None:
            await ctx.respond(f"{ mongo.CHANNELS.ACTION_REPORTS.value } channel not set")
            return

        action_form_channel = await self.bot.fetch_channel(int(channel_id))

        modal = self.ActionModal(action_form_channel, message)
        await ctx.send_modal(modal)

def setup(bot):
    bot.add_cog(Moderation(bot))
