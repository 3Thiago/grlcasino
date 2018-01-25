from discord.ext import commands


class CasinoCog:
    def __init__(self, bot):
        self.bot = bot
        self.user_manager = bot.user_manager
        self.grlc = bot.grlc
        self.conn = bot.conn

    @commands.command(description='Withdraw all your coins to the specified address')
    async def withdraw(self, ctx, dest: str):
        """
        Transfer all your stored coins to the specified GRLC address
        :param ctx:
        :param dest:
        :return:
        """
        if self.user_manager.get_user(ctx.author.id) is None:
            await ctx.send(f'{ctx.author.mention} You have no GRLC to withdraw')
            return
        result = self.grlc.transfer(dest)
        await ctx.send(f'{ctx.author.mention} {result}')

    @commands.command()
    async def stats(self, ctx):
        """
        Show your lifetime stats across all casino games
        :param ctx:
        :return:
        """
        await ctx.send(f"Stats for {ctx.author.mention}")

    @commands.command(description="Show your sending address", pass_context=True)
    async def address(self, ctx):
        """
        Show your sending address
        :param ctx:
        :return:
        """
        await ctx.send('{} Send Coins to: `{}`'.format(ctx.author.mention, self.user_manager.get_user(ctx.author.id)[1]))

    @commands.command()
    async def balance(self, ctx):
        """
        Display your balance
        :param ctx:
        :return:
        """
        balance = self.user_manager.get_balance(ctx.author.id)
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
