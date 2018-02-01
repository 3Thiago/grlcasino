import discord
from discord.ext import commands
from random import choice
from datetime import datetime
import asyncio


class TwoUpCog:
    min_buy_in = 0.05
    max_buy_in = 10
    channel_id = 408431187011567616

    def __init__(self, bot):
        self.bot = bot
        self.grlc = bot.grlc
        self.conn = bot.conn
        # check if the table exists in the db
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS twoup (toss TEXT, done INT)")
        c.execute("CREATE TABLE IF NOT EXISTS twoup_entries (bet TEXT, gameId INT, amount REAL, userId INT)")
        self.conn.commit()

    @staticmethod
    def _roll_string():
        sides = "HT"
        return "{}{}".format(choice(sides), choice(sides))

    @commands.command(aliases=['TH'])
    async def HT(self, ctx, amount: float):
        """
        Bet HT for current game
        :param ctx:
        :param amount:
        :return:
        """

        await self._do_bet(ctx, amount, 'HT')
    @commands.command()
    async def HH(self, ctx, amount: float):
        """
        Bet HH for current game
        :param ctx:
        :param amount:
        :return:
        """

        await self._do_bet(ctx, amount, 'HH')
    @commands.command()
    async def TT(self, ctx, amount: float):
        """
        Bet TT for current game
        :param ctx:
        :param amount:
        :return:
        """
        await self._do_bet(ctx, amount, 'TT')

    async def _do_bet(self, ctx, amount: float, bet: str):
        """
        Place a bet on the current game: $bet
        :param ctx:
        :param amount:
        :return:
        """
        game = self.get_current_game()
        c = self.conn.cursor()
        c.execute("SELECT rowid, * FROM twoup_entries WHERE gameId = ?", (game['rowid'],))
        if c.fetchone() is not None:
            await ctx.send(f"{ctx.author.mention} only one bet per game please")
            return

        valid_bets = ['HH', 'TT', 'HT']
        if bet not in valid_bets:
            await ctx.send(f"{ctx.author.mention} Invalid bet, please do one of: {valid_bets}")
            return
        if ctx.message.channel.id != self.channel_id:
            return

        if game is None:
            await ctx.send(f"{ctx.author.mention} There's no game running right now. Start one with `$twoup`")
        if amount <= self.min_buy_in and amount > self.max_buy_in:
            await ctx.send(f"{ctx.author.mention}: Games must be between {self.min_buy_in} and {self.max_buy_in} GRLC")
            return
        balance = self.grlc.get_balance(ctx.author.id)
        fee = self.bot.bot_fee * amount
        if balance <= amount + fee:
            await ctx.send("{}: You have insufficient GRLC ({} + {} fee)".format(ctx.author.mention, balance, fee))
        else:
            c.execute("INSERT INTO twoup_entries VALUES (?, ?, ?, ?)", (bet, game['rowid'], amount, ctx.author.id))
            self.grlc.move_between_accounts(ctx.author.id, self.bot.bot_id, amount)
            await ctx.send(f"{ctx.author.mention} received bet of {amount} for {bet}")

    @commands.command()
    async def twoup(self, ctx):
        """
        Start a dicegame for a specified amount: $start 0.75
        :param message:
        :return:
        """
        if ctx.message.channel.id != self.channel_id:
            return
        # check if the user already has a game in progress
        current_game = self.get_current_game()
        if current_game is not None:
            await ctx.send(f'{ctx.author.mention}: already a game running')
            return
        c = self.conn.cursor()
        roll = self._roll_string()
        c.execute("INSERT INTO twoup VALUES (?, 0)", (roll,))
        rowid = c.lastrowid
        self.conn.commit()
        msg = f"{ctx.author.mention} has tossed up two coins, use `$TT|$HT|$HH amount` to place a bet on the outcome in 30s"
        print(msg)
        await ctx.send(msg)
        await asyncio.sleep(30)
        # draw the winners
        c.execute("UPDATE main.twoup SET done = 1 WHERE rowid = ?", (rowid,))
        self.conn.commit()
        roll = ''.join(sorted(roll))
        out = f"Result of the game is: {roll}, results are:\n"
        for row in c.execute("SELECT rowid, * FROM twoup_entries WHERE gameId = ?", (rowid,)):
            user = self.bot.get_user(row['userId'])
            value = row['amount']
            if row['bet'] == roll:
                outcome = ":white_check_mark: wins"
            else:
                outcome = ":x: loses"
            out += f"{user.mention} bet: {row['bet']} {outcome} {value} GRLC\n"
            self.grlc.move_between_accounts(self.bot.bot_id, row['userId'], row['amount'] * 2)

        await ctx.send(out)

    def get_current_game(self):
        c = self.conn.cursor()
        c.execute("SELECT rowid, * FROM main.twoup WHERE done = 0")
        return c.fetchone()


def setup(ctx):
    ctx.add_cog(TwoUpCog(ctx))
