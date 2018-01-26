from discord.ext import commands


class CasinoCog:
    def __init__(self, bot):
        self.bot = bot
        self.grlc = bot.grlc
        self.conn = bot.conn

    @commands.command(description='Withdraw all your coins to the specified address')
    async def withdraw(self, ctx, *, dest: str, amount: float):
        """
        Transfer all your stored coins to the specified GRLC address
        :param ctx:
        :param dest:
        :return:
        """
        result = self.grlc.transfer(ctx.author.id, dest, amount)
        await ctx.send(f'{ctx.author.mention} {result}')

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
        for row in c.execute("SELECT * FROM dice WHERE userIdA = ? or userIdB = ? and winnerUserId NOT NULL", (user_id, user_id)):
            if user_id == row[3]:
                wins += 1
                won_grlc += row[2]
            else:
                losses += 1
                lost_grlc += row[2]
        earnings = won_grlc - lost_grlc
        await ctx.send(f"Stats for {ctx.author.mention}:\n```\nWins: {wins}\nLosses: {losses}\nEarnings: {earnings} GRLC\n```")

    @commands.command(description="Show your sending address")
    async def address(self, ctx):
        """
        Show your sending address
        :param ctx:
        :return:
        """
        await ctx.send('{} Send Coins to: `{}`'.format(ctx.author.mention, self.grlc.get_user_address(ctx.author.id))

    @commands.command()
    async def balance(self, ctx):
        """
        Display your balance
        :param ctx:
        :return:
        """
        balance = self.grlc.get_balance(ctx.author.id)
        await ctx.send("{} balance is: {} GRLC".format(ctx.author.mention, balance))

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

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
