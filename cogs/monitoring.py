import discord
from discord.ext import commands
import datetime
import mongo

class Monitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_guild(before, after):
        if before.channel:
            return before.channel.guild.id
        if after.channel:
            return after.channel.guild.id
        return None

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel == after.channel:
            # print("was a voice state change rather than channel change, skipping logging")
            return


        log_id = mongo.get_setting(Monitor.get_guild(before, after), "vc_updates_log")
        if log_id is None:
            print(f"{before.channel.guild.name} ({before.channel.guild.id}) does not have vc_updates_log channel set")
            return
        log_channel = self.bot.get_setting(int(log_id))

        embed = discord.Embed()

        if before.channel is not None and after.channel is None:
            embed.colour = discord.Colour.red()
            embed.description = f"User {member.mention} ({member.name})\nLeft Voice Channel {before.channel.mention} ({before.channel.name})"
        elif before.channel is None and after.channel is not None:
            embed.colour = discord.Colour.green()
            embed.description = f"User {member.mention} ({member.name})\nJoined Voice channel {after.channel.mention} ({after.channel.name})"
        elif before.channel is not None and after.channel is not None:
            embed.colour = discord.Colour.blue()
            embed.description = f"User {member.mention} ({member.name}) Moved Voice Channels\nFrom {before.channel.mention} ({before.channel.name})\nTo {after.channel.mention} ({after.channel.name})"

        embed.set_author(name=f"{member.display_name}", icon_url=member.display_avatar)

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=f"ID: {member.id}")

        await log_channel.send(embed=embed)


    async def on_voice_channel_status_update(self, channel, before, after):
        log_id = mongo.get_setting(channel.guild.id, "vc_updates_log")
        if log_id is None:
            print(f"{channel.guild.name} ({channel.guild.id}) does not have vc_updates_log channel set")
            return

        # print(log_id)
        log_channel = self.bot.get_setting(int(log_id))
        # print(log_channel)

        if before == after:
            return

        embed = discord.Embed(title="Voice Channel Status Update", color=discord.Color.blue())
        embed.add_field(name="Voice Channel", value=f"{channel.name}\n{channel.mention}")
        embed.add_field(name="Previous Status", value=before)
        embed.add_field(name="New Status", value=after)
        embed.timestamp = datetime.datetime.now()
        # await log_channel.send(f"'{channel}' status changed from '{before}' to '{after}'")
        await log_channel.send(embed=embed)

def setup(bot):
    b = Monitor(bot)
    bot.add_cog(b)
    bot.add_listener(b.on_voice_state_update, "on_voice_state_update")
    bot.add_listener(b.on_voice_channel_status_update, "on_voice_channel_status_update")