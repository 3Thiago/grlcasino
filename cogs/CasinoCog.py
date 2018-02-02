import discord
from discord.ext import commands
import asyncio
from .BaseCog import BaseCog


class CasinoCog(BaseCog):
    channel_id = 408431681305837570

    def __init__(self, bot):
        self.bot = bot
        self.grlc = bot.grlc
        self.conn = bot.conn

    @commands.command()
    async def withdraw(self, ctx):
        """
        Transfer specified coins to address: $withdraw grlcaddress 0.5
        :param ctx:
        :param dest: the GRLC address to send to
        :param: amount: the amount of GRLC to withdraw
        :return:
        """
        try:
            _, dest, amount = ctx.message.content.split(' ')
        except ValueError:
            await ctx.send(f"{ctx.author.mention} usage is: $withdraw Grlcaddress amount")
            return

        result = self.grlc.transfer(ctx.author.id, dest, float(amount))
        await ctx.send(f'{ctx.author.mention} withdrew {amount}: https://explorer.grlc-bakery.fun/tx/{result}')

    @commands.command()
    async def stats(self, ctx):
        """
        Show your lifetime stats across all casino games
        :param ctx:
        :return:
        """
        wins = 0
        won_grlc = 0
        losses = 0
        lost_grlc = 0
        user_id = ctx.author.id
        c = self.conn.cursor()
        for row in c.execute("SELECT * FROM dice WHERE (userIdA = ? or userIdB = ?)", (user_id, user_id)):
            if row['winnerUserId'] is None:
                continue
            if user_id == row['winnerUserId']:
                wins += 1
                won_grlc += row['value']
            else:
                losses += 1
                lost_grlc += row['value']
        earnings = won_grlc - lost_grlc
        await ctx.send(
            f"Stats for {ctx.author.mention}:\n```\nWins: {wins}\nLosses: {losses}\nEarnings: {earnings} GRLC\n```")

    @commands.command(description="Show your sending address")
    async def address(self, ctx):
        """
        Show your sending address
        :param ctx:
        :return:
        """
        await ctx.send('{} Send Coins to: `{}`'.format(ctx.author.mention, self.grlc.get_user_address(ctx.author.id)))

    @commands.command()
    async def transfer(self, ctx, user: discord.User, amount: float):
        """
        Transfer to another player with a specified amount
        :param ctx:
        :return:
        """
        balance = self.grlc.get_balance(ctx.author.id)
        if amount <= 0:
            await ctx.send(f"{ctx.author.mention} you must transfer more than 0 GRLC")
            return
        if balance <= amount:
            await ctx.send(f"{ctx.author.mention} you have insufficient funds ({balance} GRLC)")
        else:
            self.grlc.move_between_accounts(ctx.author.id, user.id, amount)
            await ctx.send(f"{ctx.author.mention} moved {amount} to {user.mention}")

    @commands.command()
    async def balance(self, ctx):
        """
        Display your balance
        :param ctx:
        :return:
        """
        channel = self.bot.get_channel(self.channel_id)
        balance = self.grlc.get_balance(ctx.author.id)
        await ctx.message.delete()
        await channel.send("{} balance is: {} GRLC {}".format(ctx.author.mention, balance, self.grlc_emoji))

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""
        await ctx.message.delete()
        cog = "cogs." + cog + "Cog"
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            print(f"Failed to Reload {cog}: {type(e).__name__} - {e}")
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            print(f"Reloaded {cog}")
            await ctx.send('**`SUCCESS`**')


def setup(ctx):
    ctx.add_cog(CasinoCog(ctx))
