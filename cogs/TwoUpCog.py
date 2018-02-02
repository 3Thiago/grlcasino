import discord
from discord.ext import commands
from random import choice
import asyncio
from .BaseCog import BaseCog


class TwoUpCog(BaseCog):
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
        msg = "{}{}".format(choice(sides), choice(sides))
        return ''.join(sorted(msg))

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
        c.execute("SELECT rowid, * FROM twoup_entries WHERE gameId = ? AND userId = ?", (game['rowid'], ctx.author.id))
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
        if amount <= self.min_buy_in or amount > self.max_buy_in:
            await ctx.send(f"{ctx.author.mention}: Games must be between {self.min_buy_in} and {self.max_buy_in} GRLC")
            return
        fee = self.bot.bot_fee * amount
        if await self.check_balance(amount, ctx):
            c.execute("INSERT INTO twoup_entries VALUES (?, ?, ?, ?)", (bet, game['rowid'], amount, ctx.author.id))
            self.conn.commit()
            self.grlc.move_between_accounts(ctx.author.id, self.bot.bot_id, amount + fee)
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
        await self.draw_winner(ctx, roll, rowid)

    async def draw_winner(self, ctx, roll, rowid):
        # draw the winners
        c = self.conn.cursor()
        c.execute("UPDATE main.twoup SET done = 1 WHERE rowid = ?", (rowid,))
        self.conn.commit()
        out = f"Result of the game is: {roll}, results are:\n"
        for row in c.execute("SELECT rowid, * FROM twoup_entries WHERE gameId = ?", (rowid,)):
            user = self.bot.get_user(row['userId'])
            value = row['amount']
            if row['bet'] == roll:
                outcome = "wins"
                emoji = ":white_check_mark:"
                self.grlc.move_between_accounts(self.bot.bot_id, row['userId'], row['amount'] * 2)
            else:
                outcome = "loses"
                emoji = ":x:"
            out += f"{user.mention} bet: {row['bet']} {outcome} {value} GRLC {emoji}\n"
        await ctx.send(out)

    def get_current_game(self):
        c = self.conn.cursor()
        c.execute("SELECT rowid, * FROM main.twoup WHERE done = 0")
        return c.fetchone()


def setup(ctx):
    ctx.add_cog(TwoUpCog(ctx))
