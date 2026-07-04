import discord
from discord.ext import commands, tasks
import datetime


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # self.reminder.start()

        self.channel_ids = [1505625737485357190, 1516384130114261032, 1516389364769493033]
        self.channels = []

    @tasks.loop(seconds=30)
    async def reminder(self):
        if self.channels == []:
            try:
                self.channels.append(self.bot.get_channel(self.channel_ids[0]))
            except Exception as e:
                print("oops")
                print(e)
                # self.reminder.cancel()

        print(self.channels[0])
        print(self.channels)
        if self.channels[0] is None:
            return
        await self.channels[0].send("test")



def setup(bot):
    b = Reminder(bot)
    bot.add_cog(b)



