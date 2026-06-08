import discord
from discord.ext import commands
import imagehash
from PIL import Image
from pathlib import Path
import aiohttp
import io


class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


        self.anti_spam_enabled = True


        self.scam_hashes = {}

        for img_path in Path("cogs/data/bad_images").glob("*"):
            img = Image.open(img_path)
            self.scam_hashes[img_path.name] = imagehash.phash(img)

        print(f"Added {len(self.scam_hashes)} images hashes to check")

    @staticmethod
    async def get_attachment_image(attachment):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                data = await resp.read()

        return Image.open(io.BytesIO(data))

    async def spam_check(self, message: discord.Message):
        if not self.anti_spam_enabled:
            return

        if message.author.bot:
            return

        # TODO decide on check against images that are linked (maybe only if a discord link?)
        for file in message.attachments:
            # print(file.content_type)

            lowest_distance = 100

            msg = ""

            if file.content_type in ["image/webp", "image/png", "image/jpeg"]:
                # check against known bad images
                uploaded_img = await self.get_attachment_image(file)
                uploaded_hash = imagehash.phash(uploaded_img)

                for image_hash in self.scam_hashes:
                    distance = uploaded_hash - self.scam_hashes[image_hash]

                    if lowest_distance > distance:
                        lowest_distance = distance

                    if distance == 0:
                        msg+= f"image is identical to a known bad image (dist: {distance}) {image_hash}\n"
                    elif 6 > distance > 1:
                        msg+= f"image is extremely similar to a known bad image (dist: {distance}) {image_hash}\n"
                    elif 11 > distance > 6:
                        msg+= f"image is somewhat similar to a known bad image (dist: {distance}) {image_hash}\n"
                    elif 19 > distance > 11:
                        msg+= f"image is possibly related or similar to a known bad image (dist: {distance}) {image_hash}\n"
                    elif distance > 19:
                        pass
                        # msg += f"image is likely unrelated to a known bad image (dist: {distance})\n"

                if lowest_distance < 11:
                    await message.reply(msg+"\nbad image detected, deleting")
                    await message.delete()
                    return
                else:
                    await message.reply(msg)
                    return
        return


    @commands.slash_command(name="anti_spam_off")
    async def pause_anti_spam(self, ctx: discord.ApplicationContext):
        self.anti_spam_enabled = False
        await ctx.respond("paused anti spam")

    @commands.slash_command(name="anti_spam_on")
    async def resume_anti_spam(self, ctx: discord.ApplicationContext):
        self.anti_spam_enabled = True
        await ctx.respond("enabled anti spam")



def setup(bot):
    b = AntiSpam(bot)
    bot.add_cog(b)
    bot.add_listener(b.spam_check, "on_message")