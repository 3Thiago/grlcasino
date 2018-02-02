import asyncio


class BaseCog:
    grlc_emoji = '<:grlc:408482412809420810>'

    async def check_balance(self, amount, ctx):
        """
        Checks if the current user can play a game including the fee
        :param amount:
        :param ctx:
        :return:
        """
        balance = self.grlc.get_balance(ctx.author.id)
        fee = self.bot.bot_fee * amount
        if balance <= amount + fee:
            await ctx.send("{}: You have insufficient GRLC ({} + {} fee)".format(ctx.author.mention, balance, fee))
            return False
        return True
