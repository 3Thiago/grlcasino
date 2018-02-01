import discord
from discord.ext import commands
from random import choice
import asyncio


class CoinTossCog:
    min_buy_in = 0.01
    max_buy_in = 10
    channel_id = 408497113857785868

    def __init__(self, bot):
        self.bot = bot
        self.grlc = bot.grlc
        self.conn = bot.conn
        # check if the table exists in the db
        c = self.conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS headstails (userIdA INT, userIdB INT, tossA TEXT, tossB TEXT, winnerUserId INT, amount REAL)")
        self.conn.commit()

    @commands.command()
    async def T(self, ctx, amount: float):
        """
        Start a game predicting TAILS
        :param ctx:
        :param amount:
        :return:
        """

        await self._start_game(ctx, amount, 'T')

    @commands.command()
    async def H(self, ctx, amount: float):
        """
        Start a game predicting HEADS
        :param ctx:
        :param amount:
        :return:
        """

        await self._start_game(ctx, amount, 'H')

    async def _start_game(self, ctx, amount: float, bet: str):
        """
        Place a bet on the current game: $bet
        :param ctx:
        :param amount:
        :return:
        """
        if ctx.message.channel.id != self.channel_id:
            return
        game = self.get_current_game(ctx.author.id)
        if game is not None:
            await ctx.send(f"{ctx.author.mention} you already have a game running")
            return
        c = self.conn.cursor()

        if amount < self.min_buy_in or amount > self.max_buy_in:
            await ctx.send(f"{ctx.author.mention}: Games must be between {self.min_buy_in} and {self.max_buy_in} GRLC")
            return
        balance = self.grlc.get_balance(ctx.author.id)
        fee = self.bot.bot_fee * amount
        if balance <= amount + fee:
            await ctx.send("{}: You have insufficient GRLC ({} + {} fee)".format(ctx.author.mention, balance, fee))
        else:
            c.execute("INSERT INTO headstails VALUES (?, ?, ?, ?, ?)",
                      (ctx.author.id, None, bet, None, None, amount))
            self.grlc.move_between_accounts(ctx.author.id, self.bot.bot_id, amount + fee)
            await ctx.send(f"{ctx.author.mention} predicted {bet} with a value of {amount}")

    @commands.command()
    async def toss(self, ctx, user: discord.User):
        """
        Accept for a specified amount: $start @peace
        :param message:
        :return:
        """
        if ctx.message.channel.id != self.channel_id:
            return
        # check if the user already has a game in progress
        c = self.conn.cursor()
        game = self.get_current_game(user.id)
        if game is None:
            await ctx.send(f"{ctx.author.id} that user no current games")
            return
        amount = game['amount']
        balance = self.grlc.get_balance(ctx.author.id)
        fee = self.bot.bot_fee * amount
        if balance <= amount + fee:
            await ctx.send("{}: You have insufficient GRLC ({} + {} fee)".format(ctx.author.mention, balance, fee))
            return
        if game['tossA'] == 'H':
            roll_b = 'T'
        else:
            roll_b = 'H'
        self.grlc.move_between_accounts(ctx.author.id, self.bot.bot_id, fee)
        roll = choice(['H', 'T'])
        if roll == game['tossA']:
            winner = game['userIdA']
        else:
            winner = game['userIdB']
        winner = self.bot.get_user(winner)
        c.execute("UPDATE TABLE headstails SET userIdB = ?, tossB = ?, winnerUserId = ? WHERE rowid = ?",
                  (ctx.author.id, roll_b, winner.id, game['rowid']))
        self.conn.commit()
        msg = f"{ctx.author.mention} the coin landed on {roll}, {winner.mention} wins {amount} GRLC"
        self.grlc.move_between_accounts(self.bot.bot_id, winner.id, amount)
        print(msg)
        await ctx.send(msg)

    @commands.command()
    async def canceltoss(self, ctx):
        """
        Cancel your current game
        :param ctx:
        :return:
        """
        game = self.get_current_game(ctx.author.id)
        if game is None:
            await ctx.send(f"{ctx.author.id} you have no game to cancel")
            return
        c = self.conn.cursor()
        c.execute("DELETE FROM main.dice WHERE rowid = ?", (game['rowid'],))
        self.conn.commit()
        fee = game['value'] * self.bot.bot_fee
        self.grlc.move_between_accounts(self.bot.bot_id, ctx.author.id, fee + game['value'])
        await ctx.send(f"{ctx.author.mention} cancelled and refunded game worth {game['value']} + {fee}")

    def get_current_game(self, userId):
        c = self.conn.cursor()
        c.execute("SELECT rowid, * FROM headstails WHERE userIdA = ? AND userIdB IS NULL", (userId,))
        return c.fetchone()


def setup(ctx):
    ctx.add_cog(CoinTossCog(ctx))
