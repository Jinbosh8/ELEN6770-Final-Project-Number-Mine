import boto3
from boto3.dynamodb.conditions import Attr
from datetime import datetime
from random import randrange

class GameController:

    def __init__(self, connectionManager):

        self.cm = connectionManager

    def createNewGame(self, gameId, creator, invitee):

        table = self.cm.getGamesTable()
        statusDate = "PENDING_" + str(datetime.now())
        mine = randrange(100)
        numRange = [0, 100] # default range
        response = table.put_item(
            Item={
                    "GameId"     : gameId,
                    "HostId"     : creator,
                    "StatusDate" : statusDate,
                    "OUser"      : creator,
                    "Turn"       : invitee,
                    "OpponentId" : invitee,
                    "Mine"       : mine,
                    "NumRange"   : numRange,
                    "Host_pick"  : -1,
                    "Oppo_pick"  : -1
                }
            )
        return response

    def getGame(self, gameId):

        table = self.cm.getGamesTable()
        try:
            response = table.get_item(
                TableName = 'Games',
                Key={
                    'GameId': gameId
                }
            )
        except:
            response = None

        return response["Item"]

    def getGameInvites(self, user):

        table = self.cm.getGamesTable()
        # query only support primary key
        resp = table.scan(
            FilterExpression=Attr("OpponentId").eq(user) & Attr('StatusDate').begins_with('PENDING')
            )
        
        if len(resp['Items']) <= 5:
            return resp['Items']
        else:
            return resp['Items'][0:5]
    
    def getGameInProgress(self, user):

        table = self.cm.getGamesTable()
        host_resp = table.scan(
            FilterExpression=Attr("HostId").eq(user) & Attr('StatusDate').begins_with('INPROGRESS')
            )
        oppo_resp = table.scan(
            FilterExpression=Attr("OpponentId").eq(user) & Attr('StatusDate').begins_with('INPROGRESS')
            )
        
        return host_resp['Items'] + oppo_resp['Items']

    def getGameFinished(self, user):

        table = self.cm.getGamesTable()
        host_resp = table.scan(
            FilterExpression=Attr("HostId").eq(user) & Attr('StatusDate').begins_with('FINISHED')
            )
        oppo_resp = table.scan(
            FilterExpression=Attr("OpponentId").eq(user) & Attr('StatusDate').begins_with('FINISHED')
            )
        
        return host_resp['Items'] + oppo_resp['Items']

    def acceptGameInvite(self, game):

        statusDate = "INPROGRESS_" + str(datetime.now())
        table = self.cm.getGamesTable()
        try:
            table.update_item(
                    Key={
                        'GameId': game['GameId']
                    },
                    UpdateExpression="SET StatusDate=:s",
                    ExpressionAttributeValues={
                        ':s': statusDate
                    }
                )
            return True
        except:
            return False

    def rejectGameInvite(self, game):

        table = self.cm.getGamesTable()
        try:
            table.delete_item(
                    Key={
                        'GameId': game['GameId']
                    }
                )
            return True
        except:
            return False

    def finishGame(self, gameId, result):

        statusDate = "FINISHED_" + str(datetime.now())
        winner = result.split(' ')[0]
        table = self.cm.getGamesTable()
        # try:
        table.update_item(
                Key={
                    'GameId': gameId
                },
                UpdateExpression="SET StatusDate=:s, GameResult=:r",
                ExpressionAttributeValues={
                    ':s': statusDate,
                    ':r': winner
                }
            )
        #     return True
        # except:
        #     return False

    def getRange(self, item):
        return [str(item['NumRange'][0]), str(item['NumRange'][1])]

    def checkResult(self, item, current_player):

        # print(type(item['Mine']), item['Mine'])
        # print(type(item['Host_pick']), item['Host_pick'])
        
        mine = item['Mine']
        if mine == int(item['Host_pick']):
            result_win = item['OpponentId'] + ' wins :) \n'
            result_lose = item['HostId'] + ' loses :('
            item["Result"] = item['OpponentId']
            return result_win, result_lose
        elif mine == int(item['Oppo_pick']):
            result_win = item['HostId'] + ' wins :) \n'
            result_lose = item['OpponentId'] + ' loses :('
            item["Result"] = item['HostId']
            return result_win, result_lose
        else:
            return None, None

    def updateRangeAndTurn(self, item, userPick, current_player):

        if item['Turn'] != current_player:
            return False
        else:
            if item['Turn'] == item['HostId']:
                nextTurn = item['OpponentId']
                hostPick = userPick
                oppoPick = item['Oppo_pick']
            else:
                nextTurn = item['HostId']
                hostPick = item['Host_pick']
                oppoPick = userPick
        
        if int(userPick) <= int(item['NumRange'][0]) or int(userPick) >= int(item['NumRange'][1]):
            return False
        else:
            if int(userPick) >= int(item['Mine']):
                newRange = [item['NumRange'][0], userPick]
            else:
                newRange = [userPick, item['NumRange'][1]]
          
        table = self.cm.getGamesTable()
        try:
            table.update_item(
                Key={
                    'GameId': item['GameId']
                },
                UpdateExpression="SET Turn=:t, Host_pick=:h, Oppo_pick=:o, NumRange=:r",
                ExpressionAttributeValues={
                    ':t': nextTurn,
                    ':h': hostPick,
                    ':o': oppoPick,
                    ':r': newRange
                }
            )
        except:
            return False

        return True

