import discord
from discord.ext import commands

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if self.bot.debug_mode is True:
            self.approved_role = 1507627720195182762
            self.rejected_role = 1507627922612027483
            self.quarantine_role = 1507627790864744538

            self.log_channel = 1507628151625355335
            self.rejection_message_channel = 1507628182637903914

            self.intro_channel = 1507346971441106948
        else:
            self.approved_role = 876219823158345738
            self.rejected_role = 1480871861465125047
            self.quarantine_role = 1441219699521355837

            self.log_channel = 876219824068505611
            self.rejection_message_channel = 1450482074350784552
            self.intro_channel = 1446153675264491561


    @commands.slash_command(name="approve", default_member_permissions=discord.Permissions(manage_roles=True))
    async def verification_approve_automatic(self, ctx: discord.ApplicationContext):
        """Approve user (use in thread)"""
        await ctx.defer()

        # get the channel this was used in
        chan = ctx.channel
        if type(chan) != discord.Thread:
            await ctx.respond(f"This command only works in a thread", ephemeral=True)
            return

        # get starter message and author
        try:
            msg = await chan.parent.fetch_message(chan.id)
            user = msg.author
        except discord.NotFound:
            await ctx.respond(f"Could not find starting message, will not proceed")
            return

        # make sure user is not a bot
        if user.bot:
            await ctx.respond(f"{user} is a bot")
            return

        # check starter message is in introduction channel
        if msg.channel.id != self.intro_channel:
            await ctx.respond("This command needs to used in a thread in the introductions channel")
            return

        # check user isn't already approved (has member role) and check user doesn't have rejection role
        user_has_quarantine_role = False
        q_role = None

        roles = user.roles
        for role in roles:
            if role.id == self.approved_role:
                await ctx.respond(f"User {user.name} is already approved")
                return
            elif role.id == self.rejected_role:
                await ctx.respond(f"User {user.name} has the rejected role")
                return
            elif role.id == self.quarantine_role:
                user_has_quarantine_role = True
                q_role = role

            # print(role.id, role.name)

        # make sure bot has the manage roles permission
        bot_member = ctx.guild.me
        if not bot_member.guild_permissions.manage_roles:
            await ctx.respond(f"The bot does not have manage roles permission and cannot proceed")
            return

        # remove quarantine role
        if user_has_quarantine_role:
            await user.remove_roles(q_role)

        # add member role
        member = await ctx.guild.fetch_role(self.approved_role)
        await user.add_roles(member)

        # log in a channel (probably a staff related one)
        staff_channel = await ctx.guild.fetch_channel(self.log_channel)
        embed = discord.Embed(title="User Approved", color=discord.Color.green())
        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="User ID", value=str(user.id))
        await staff_channel.send(embed=embed)

        # send a message in thread with "user approved" user id, and their original intro
        await ctx.respond(f"User Approved\n\nUser ID: {user.id}\n\nIntro: {msg.content}")

    @commands.slash_command(name="approve_user", default_member_permissions=discord.Permissions(manage_roles=True)) # only roles with manage role perm can see/use
    async def verification_approve_manual_slash(self, ctx: discord.ApplicationContext,
            user: discord.Option(discord.Member, description="User to approve", required=True),):
        """Approve a given user"""
        await self.verification_approve_manual(ctx, user)

    @commands.user_command(name="Approve User", default_member_permissions=discord.Permissions(manage_roles=True))
    async def verification_approve_manual_user(self, ctx, user: discord.Member):
        """Approve a given user"""
        await self.verification_approve_manual(ctx, user)

    async def verification_approve_manual(self, ctx, user):
        await ctx.defer()

        # make sure user is not a bot
        if user.bot:
            await ctx.respond(f"{user} is a bot")
            return

        # check user isn't already approved (has member role) and check user doesn't have rejection role
        user_has_quarantine_role = False
        q_role = None

        roles = user.roles
        for role in roles:
            if role.id == self.approved_role:
                await ctx.respond(f"User {user.name} is already approved")
                return
            elif role.id == self.rejected_role:
                await ctx.respond(f"User {user.name} has the rejected role")
                return
            elif role.id == self.quarantine_role:
                user_has_quarantine_role = True
                q_role = role

            # print(role.id, role.name)

        # make sure bot has the manage roles permission
        bot_member = ctx.guild.me
        if not bot_member.guild_permissions.manage_roles:
            await ctx.respond(f"The bot does not have manage roles permission and cannot proceed")
            return

        # remove quarantine role
        if user_has_quarantine_role:
            await user.remove_roles(q_role)

        # add member role
        member = await ctx.guild.fetch_role(self.approved_role)
        await user.add_roles(member)

        # log in a channel (probably a staff related one)
        staff_channel = await ctx.guild.fetch_channel(self.log_channel)
        embed = discord.Embed(title="User Approved", color=discord.Color.green())
        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="User ID", value=str(user.id))
        await staff_channel.send(embed=embed)

        # send a message in thread with "user approved" user id
        await ctx.respond(f"User Approved\n\nUser ID: {user.id}")

    """
    above is approval
    
    -----
    
    below is rejection
    """

    @commands.slash_command(name="reject", default_member_permissions=discord.Permissions(manage_roles=True),)
    async def verification_reject_automatic(self, ctx: discord.ApplicationContext,
            reason: discord.Option(str, description="Reason for rejection", default="No Reason Provided")):
        """Reject a user (use in thread)"""
        await ctx.defer()

        # get the channel this was used in
        chan = ctx.channel
        if type(chan) != discord.Thread:
            await ctx.respond(f"This command only works in a thread", ephemeral=True)
            return

        # get starter message and author
        try:
            msg = await chan.parent.fetch_message(chan.id)
            user = msg.author
        except discord.NotFound:
            await ctx.respond(f"Could not find starting message, will not proceed")
            return

        # check starter message is in introduction channel
        if msg.channel.id != self.intro_channel:
            await ctx.respond("This command needs to used in a thread in the introductions channel")
            return

        # check user isn't already approved (has member role) and check user doesn't have rejection role
        user_has_quarantine_role = False
        q_role = None

        roles = user.roles
        for role in roles:
            if role.id == self.approved_role:
                await ctx.respond(f"User {user.name} is already approved")
                return
            elif role.id == self.rejected_role:
                await ctx.respond(f"User {user.name} already has the rejected role")
                return
            #elif role.id == self.quarantine_role:
            #    user_has_quarantine_role = True
            #    q_role = role

            # print(role.id, role.name)

        # make sure bot has the manage roles permission
        bot_member = ctx.guild.me
        if not bot_member.guild_permissions.manage_roles:
            await ctx.respond(f"The bot does not have manage roles permission and cannot proceed")
            return

        # add reject role
        reject = await ctx.guild.fetch_role(self.rejected_role)
        await user.add_roles(reject)

        # make sure reason isn't blank
        if len(reason) == 0:
            reason = "No Reason Provided"

        # log in a channel (probably a staff related one)
        staff_channel = await ctx.guild.fetch_channel(self.log_channel)
        embed = discord.Embed(title="User Rejected", color=discord.Color.green())
        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="User ID", value=str(user.id))
        embed.add_field(name="Reason", value=reason)
        await staff_channel.send(embed=embed)

        # send a message in thread with "user rejected" user id, and their original intro
        await ctx.respond(f"User Rejected\n\nReason: {reason}\n\nUser ID: {user.id}\n\nIntro: {msg.content}")



def setup(bot):
    bot.add_cog(Verification(bot))
