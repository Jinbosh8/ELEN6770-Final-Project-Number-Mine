# Used for getting different information of one game 
class Game:

    def __init__(self, item):

        self.item = item
        self.gameId = item["GameId"]
        self.hostId = item["HostId"]
        self.opponent = item["OpponentId"]
        self.statusDate = item["StatusDate"].split("_")
        self.owner = item["OUser"]
        self.turn = item["Turn"]

    def get_status(self):
        return self.statusDate[0]
    
    def getOpposingPlayer(self, current_player):
        if current_player == self.hostId:
            return self.opponent
        else:
            return self.hostId

    def getResult(self, current_player):

        if self.item["GameResult"] == None:
            return None
        else:
            if self.item["GameResult"] == self.opponent:
                result = self.item['OpponentId'] + ' wins:) \n'
                result += self.item['HostId'] + ' loses:('
                return result
            else:
                result = self.item['HostId'] + ' wins:) \n'
                result += self.item['OpponentId'] + ' loses:('
                return result
            

if __name__ == "__main__":
    Item = {
                'Turn': 'user1', 
                'HostId': 'hi', 
                'StatusDate': 'PENDING_2021-04-04 14:44:59.057930', 
                'GameId': '0f3175c3-4407-4f3c-85e9-219ea0f9af59', 
                'OpponentId': 'user1', 
                'OUser': 'hi'
            }

    g = Game(Item)
    s = g.get_status()


    

        