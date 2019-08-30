# PUBG calc_rank.py

This is a python 3 program for doing solo match custom game tournaments.<br>

It allows for games to be played when people can get enough players together.<br>
A match is then entered into the program and it will spit out a player rankings based on their ELO.<br>

We have players post a screenshot of the end game scoreboard into a discord channel and one person is responsible for entering the games, in order, and posting the new ratings.<br>

It has a minimum games to qualify setting that will score show the players who have qualified and the ones who have not yet qualified.<br>
This way games do not have to be at set times or with set players.<br>
The tournament starts everyone at the default rating, 1500 is what I entered, and adjusts based on performance.

<b>How to use the program</b><br>
There are some settings that can be changed.<br>
RANKING_FILE = "current_rankings.txt"   # The name of the file holding the current tournament standings<br>
NQ_FILE = "not_qualified.txt"           # The file to hold the players without enough games to qualify<br>
GAME_FILE = "game_{}.txt"               # The name structure for the file saved for each tournament game<br>
NEW_PLAYER_START_RATING = 1500          # The start rating given to players (first game will adjust from this value)<br>
KILLS_VALUE = 1.0                       # The multiplier used for game kills (used if USE_PLAYER_KILLS is True)<br>
QUALIFYING_GAME_COUNT = 10              # The number of games a player must play before their rating counts<br>
MINIMUM_PLAYERS = 5                     # The minimum players needed for a tournament game<br>

USE_PLAYER_KILLS = True                 # True = Uses player kills in game in rating adjustment calculation<br>
PRINT_ERRORS = False                    # Prints some possible errors to the console (I never enable this)<br>

When have not run many tournaments yet and are figuring out exactly what we want the settings to be. 
The only ones we are messing with are the NEW_PLAYER_START_RATING, KILLS_VALUE, QUALIFYING_GAME_COUNT, and MINIMUM_PLAYERS. 
The only one we have different than the setting seen above is the KILLS_VALUE. We currently have it set to 0.5. 
This setting will be multiplied by the kills gotten by a player in the game and then added to the calculated ELO.

The program also includes the ability to recalculate the ELOs based on games already entered. If the program is run and there are one or more GAME_FILE present in the same directory, and there is no RANKING_FILE and no NQ_FILE, it will ask if you want to reprocess the game files. This gives the ability to change settings and see how they would change the player ELO results once a few games have been played. Just remember that to reprocess the games the RANKING_FILE and NQ_FILE must not be there and there must be some GAME_FILE(s).<br>

Other than that, The program will ask you how many people participated in the game.<br>
Then the program will ask you to enter each player and their game results. It will ask for a name (length is not enforced but I recommend 5 characters or less to give a nice output format). The name is the key used, this means that when the same player plays another game the name must be the same to continue with the ELO calculation or it will count the player as a new player. It will then ask for the player's finishing position and game kills. It will ask you to verify that the entered information is good before going on to the next player entry. It will calculate the entered information when you have entered the amount of players you said were in the game.<br>

When it start the program, or finishes recalculating the games, it will display the current player listings, starting with the qualified players and then the not yet qualified players, so that you can get the player names correct as you enter the new information.<br>
After the calculations are complete, it will output the new player standings that are in a format that is easy to read and display to the players. We take a screenshot and post that in discord.

Hopefully this works as well for you as it has, so far, for us. Enjoy<br>
