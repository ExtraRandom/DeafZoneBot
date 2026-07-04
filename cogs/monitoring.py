import discord
from discord.ext import commands
import datetime


class Monitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1516384364907466793
        self.monitor_vc_id = 1516384130114261032

        self.log_channel: discord.TextChannel = None

    async def on_voice_state_update(self, member, before: discord.VoiceState, after: discord.VoiceState):
        if self.log_channel == None:
            self.log_channel = self.bot.get_channel(self.log_channel_id)

        if before.channel == after.channel:
            print("was a voice state change rather than channel change, skipping logging")
            return

        embed = discord.Embed(title="voice update", color=discord.Color.blue())
        embed.add_field(name="member", value=member.mention)

        if before.channel is not None:
            embed.add_field(name="Previous Channel", value=before.channel.mention)
        else:
            embed.add_field(name="Previous Channel", value="No VC")

        if after.channel is not None:
            embed.add_field(name="New Channel", value=after.channel.mention)
        else:
            embed.add_field(name="New Channel", value="No VC")

        embed.timestamp = datetime.datetime.now()

        await self.log_channel.send(embed=embed)


        #await self.log_channel.send(f"{member.display_name} changed from \n'{before.channel}' with self muted: {before.self_mute} \n"
        #                            f"to '{after.channel}' with self muted: {after.self_mute} \n")


        print(member)
        print(before)
        print(after)

    async def on_voice_channel_status_update(self, channel, before, after):
        if self.log_channel == None:
            self.log_channel = self.bot.get_channel(self.log_channel_id)

        if before == after:
            return

        await self.log_channel.send(f"'{channel}' status changed from '{before}' to '{after}'")

def setup(bot):
    b = Monitor(bot)
    bot.add_cog(b)
    bot.add_listener(b.on_voice_state_update, "on_voice_state_update")
    bot.add_listener(b.on_voice_channel_status_update, "on_voice_channel_status_update")