from flask import Flask, session, request, render_template, redirect
from flask import flash, jsonify
from uuid import uuid4
import json

import dynamodb.connectionManager as CM
import dynamodb.gameController as GM
import models.game

application = Flask(__name__)
application.secret_key = str(uuid4())

cm = CM.ConnectionManager()
controller = GM.GameController(cm)

# Update user after log-in
# Fetch gaming info of the user
@application.route('/')
@application.route('/index', methods = ["GET", "POST"])
def index():
    
    # get session username
    if session == {} or session.get("username", None) == None:
        form = request.form
        if form:
            formInput = form["username"]
            if formInput and formInput.strip():
                session["username"] = request.form["username"]
            else:
                session["username"] = None
        else:
            session["username"] = None

    if request.method == "POST":
        return redirect('/index')

    inviteGames = controller.getGameInvites(session["username"])
    inviteGames = [models.game.Game(inviteGame) for inviteGame in inviteGames]

    inProgressGames = controller.getGameInProgress(session["username"])
    inProgressGames = [models.game.Game(inProgressGame) for inProgressGame in inProgressGames]

    finishedGames   = controller.getGameFinished(session["username"])
    fs = [models.game.Game(finishedGame) for finishedGame in finishedGames]

    return render_template("index.html",
                            user=session["username"],
                            invites=inviteGames,
                            inprogress=inProgressGames,
                            finished=fs)

# Create game for logged in user
@application.route('/create')
def create():

    if session.get("username", None) == None:
        flash("Need to login to create game")
        return redirect("/index")
    return render_template("create.html",
                            user=session["username"])

# Take user to game page
@application.route('/play', methods=["POST"])
def play():

    form = request.form
    if form:
        creator = session["username"]
        gameId  = str(uuid4())
        invitee = form["invitee"].strip()

        if not invitee or creator == invitee:
            flash("Use valid a name (not empty or your name)")
            return redirect("/create")

        if controller.createNewGame(gameId, creator, invitee):
            return redirect("/game="+gameId)

    flash("Something went wrong creating the game.")
    return redirect("/create")

# Accept pending invites by logged in user
@application.route('/accept=<invite>', methods=["POST"])
def accept(invite):

    gameId = request.form["response"]
    game = controller.getGame(gameId)

    if game == None:
        flash("That game does not exist anymore.")
        redirect("/index")

    if not controller.acceptGameInvite(game):
        flash("Error validating the game...")
        redirect("/index")

    return redirect("/game="+game["GameId"])

# Reject pending invites by logged in user
@application.route('/reject=<invite>', methods=["POST"])
def reject(invite):

    gameId = request.form["response"]
    game = controller.getGame(gameId)

    if game == None:
        flash("That game doesn't exist anymore.")
        redirect("/index")

    if not controller.rejectGameInvite(game):
        flash("Something went wrong when deleting invite.")
        redirect("/index")

    return redirect("/index")

# Get status of the game and update them
@application.route('/game=<gameId>')
def game(gameId):
    
    item = controller.getGame(gameId)
    if item == None:
        flash("Game does not exist.")
        return redirect("/index")

    game = models.game.Game(item)
    status   = game.get_status()
    turn     = game.turn

    rangeState = controller.getRange(item)
    result_win, result_lose = controller.checkResult(item, session["username"])

    if result_win != None:
        if controller.finishGame(gameId, result_win) == False:
            flash("Some error occured while trying to finish game.")

    gameData = {'gameId': gameId, 
                'status': status, 
                'turn': turn}
    gameJson = json.dumps(gameData)
    return render_template("play.html",
                            gameId=gameId,
                            gameJson=gameJson,
                            user=session["username"],
                            status=status,
                            turn=turn,
                            opponent=game.getOpposingPlayer(session["username"]),
                            result_win=result_win,
                            result_lose=result_lose,
                            range_low=rangeState[0],
                            range_high=rangeState[1])

# Validate user's move and update the game
@application.route('/select=<gameId>', methods=["POST"])
def selectNumber(gameId):

    try:   
        item = controller.getGame(gameId)
    except:
        flash("This is not a valid game.")
        return redirect("/index")

    form = request.form
    userPick = form['userPick']
    
    if controller.updateRangeAndTurn(item, userPick, session["username"]) == False:
        flash("You have selected a invalide number or it's not your turn \
               or the game is not 'In-Progress'.", "updateError")
        return redirect("/game="+gameId)

    return redirect("/game="+gameId)

# Validate the existence of the game
@application.route('/gameData=<gameId>')
def gameData(gameId):

    item = controller.getGame(gameId)
    if item == None:
        return jsonify(error='That game does not exist')

    game = models.game.Game(item)
    status   = game.get_status()
    turn     = game.turn

    rangeState = controller.getRange(item)

    return jsonify(gameId = gameId,
                   status = status,
                   turn = turn,
                   range_low=rangeState[0],
                   range_high=rangeState[1])


@application.route('/logout')
def logout():
    session["username"] = None
    return redirect("/index")

if __name__ == "__main__":
    # application.run(debug = True)
    application.run(host="0.0.0.0", port = 5000)
