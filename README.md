# ELEN6770-Final-Project-Number-Mine
Final Project for ELEN 6770 Spring 2021

# Introduction
  In this project, we plan to build a new version of the bulls-and-cows multiplayer game, which will be a web application built on Amazon DynamoDB. 
  The traditional bulls-and-cows is a code-breaking game that the player who gets the correct hidden number wins, but our version of the game is slightly different and more strategic and exciting. 
  In order to start the game, one player needs to log in to the game and then choose to either create a new game or accept the invitation from others. Once the invitation has been accepted, the game will start.  
  The overall rule of our game is that the system will randomly plant a “mine”, generating a number in a range, and the range is known for all players all the time. Players take turns to pick a number in the range and the range will shrink according to the players’ choices. 
  Eventually, the one who picks the hidden “mine” will lose the game. 
  
# Organization of this directory

dynamodb folder contains to python files: connectionManager.py and gamController.py. connectionManager.py is used to connect to dynamodb and get the related info. gamController.py is used to make changes on games as well as makes updates.

models folder contains one python file: game.py which is used to getting different information of one game, such as IDs for games and users

static folder contains some local implementations

templates folder contains six html files which are used to create our UI
