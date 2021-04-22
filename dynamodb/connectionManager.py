import boto3

# Connect to dynamodb and get related info
class ConnectionManager:

    def __init__(self):

        # dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1')
        try:
            self.db = boto3.resource('dynamodb')
        except Exception as e:
            raise e("Error at connecting to dynamoDB")

        self.setupGameTable()
    
    def setupGameTable(self):

        try:
            self.gamesTable = self.db.Table("Games")
            print("setupGameTable: ", self.gamesTable.table_status)
        except Exception as e:
            raise e("Error at getting Games table")
         
        print(self.gamesTable.table_status)
    
    def getGamesTable(self):

        if self.gamesTable == None:
            self.setupGamesTable()

        return self.gamesTable
    
