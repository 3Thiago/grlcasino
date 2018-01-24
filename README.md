GRLCasino
=========

A discord bot to play casino games with

Usage
-----

1. Use `c!address` in discord chat to show the bot's wallet for you.
2. Send coins to that address with your discord name as the transaction description (eg. `@pe✌ce#1135` )
3. Use `c!balance` to check your balance
4. Start a game with `c!start <amount>` to start a game with that amount of GRLC. Must be more than  0 and less than your balance
5. Another player can use `c!accept @username#1234` to accept the game. The bot will roll 2 dice for each player. Player with the highest score takes the other player's GRLC. No change will take place in case of a draw
6. Use `c!stats` to see your stats
7. Use `c!games` to list current games
8. Use `c!help` to list commands
9. Use `c!withdraw <GRLC addr>` to move all your GRLC to the specified address

Documentation
-------------

DB looks like:

Table Users:
 - username : String unique,
 - wallet : String 

Table History:
 - username: String
 - action : String

Table Games:
 - usernameA : String
 - usernameB : String # Will be null to start with
 - value : float
 - winner : String # null
 - created : timestamp
