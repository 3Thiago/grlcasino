import discord
from discord.ext import commands
from random import randint
from numpy import choice
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

class LottoCog:

    min_buy_in = 0.1
    max_buy_in = 10

    def __init__(self, bot):
        self.bot = bot
        self.grlc = bot.grlc
        self.conn = bot.conn

        
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.lotto_do, 'interval', seconds=3600)
        scheduler.start()
   
    def lotto_create(self):
        """
        Create a game of lotto if none exists,
        
        """
        c = self.conn.cursor()
        c.execute("UPDATE lotto_games SET current = 0 WHERE current = 1")
        c.execute("INSERT INTO lotto_games VALUES (1, ?)",(null,))
        self.conn.commit()
    def lotto_winner(self):
        c = self.conn.cursor()
        entrants = []
        amounts = []
        game = self.get_current_game()
        for row in c.execute("SELECT * FROM lotto_entries WHERE game = ?",(game.rowid,)):
            entrants.append(row.userId)
            amounts.append(row.amount)
        amounts = np.array(amounts)
        winnerId = choice(entrants, p=amounts.sum()/amounts)
        c.execute("UPDATE lotto_games SET winnerId = ?", (winnerId,))
        self.conn.commit()
        return winnerId

    @commands.command()
    async def enterlotto(self, ctx, *, amount: float):
        """
        Start a dicegame, another player must accept it
        :param message:
        :return:
        """
        # check if the user already has a game in progress
        current_game = self.get_current_game(ctx.author.id)
        if current_game is not None:
            await ctx.send(f'{ctx.author.mention}: There\'s no lottery running at the moment')
            return
        if amount <= self.min_buy_in and amount > self.max_buy_in:
            await ctx.send(
                f"{ctx.author.mention}: Entries must be between {self.min_buy_in} and {self.max_buy_in} GRLC")
            return
        balance = self.grlc.get_balance(ctx.author.id)
        if balance < amount:
            await ctx.send("{}: You have insufficient GRLC ({})".format(ctx.author.mention, balance))
        else:  
            c.execute("INSERT INTO lotto_entries VALUES (?, ?, ?)",
                      (ctx.author.id,
                       amount,
                       current_game.rowid)
                      )
            self.conn.commit()
            msg = "{} your entry {} GRLC has been received!".format(ctx.author.mention, amount)
            await ctx.send(msg)

    @commands.command()
    async def lottopot(self, ctx):
        """
        Show the pot and end time for the current lottery
        """
        game = self.get_current_game()
        total = 0
        c = self.conn.cursor()
        for row in conn.execute("SELECT * FROM lotto_entries WHERE game = ?",():
            total += row.amount
        msg = "Current lottery has a pot of {} and will be draw in {}".format(total, datetime.now() - game.drawtime)
        await ctx.send(msg)
 
    def get_current_game(self):
        c = self.conn.cursor()
        c.execute("SELECT rowid, * FROM lotto_games WHERE current = 1")
        return c.fetchone()

        
    

def setup(ctx):
    ctx.add_cog(LottoCog(ctx))
