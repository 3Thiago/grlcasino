import asyncio
class BaseCog:
    async def check_balance(self, amount, ctx):
        balance = self.grlc.get_balance(ctx.author.id)
        fee = self.bot.bot_fee * amount
        if balance <= amount + fee:
            await ctx.send("{}: You have insufficient GRLC ({} + {} fee)".format(ctx.author.mention, balance, fee))