GRLCasino
=========

A discord bot to play casino games with

Usage
-----

1. Use `$address` in discord chat to show the bot's wallet for you.
2. Send coins to that address with your discord name as the transaction description (eg. `@pe✌ce#1135` )
3. Use `$balance` to check your balance
4. Start a game with `$start <amount>` to start a game with that amount of GRLC. Must be more than  0 and less than your balance
5. Another player can use `$accept @username#1234` to accept the game. The bot will roll 2 dice for each player. Player with the highest score takes the other player's GRLC. No change will take place in case of a draw
6. Use `$stats` to see your stats
7. Use `$games` to list current games
8. Use `$help` to list commands
9. Use `$withdraw <GRLC addr>` to move all your GRLC to the specified address

Documentation
-------------

DB looks like:


Casino History:
 - userId: INT
 - action : String

Dice Games:
 - userIdA : INT
 - userIdB : INT # Will be null to start with
 - value : REAL # GRLC value of game
 - winnerUserId : INT # null
 - created : timestamp
 - rollA : TEXT
 - rollB : TEXT

lotto_games:
 - current : INT # Is this the current game?
 - winnerUserId : INT
 - drawTime : DATETIME
 
lotto_entries:
 - userId : INT
 - amount : REAL
 - gameId : INT # the rowid of the lotto_game 