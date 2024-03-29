from player import Player
from battle import Battle
from world import World
import pymysql 
import config

class Game():
    def __init__(self, userID):
        self.player = None
        dbinfo = config.getInfoToConnectDB()
        self.connection = pymysql.connect(host = dbinfo['host'],
                            user = dbinfo['user_name'],
                            password = dbinfo['password'],
                            db = dbinfo['db_name'],
                            charset = 'utf8',
                            cursorclass = pymysql.cursors.DictCursor)
        if self._exist(userID):
            self.player = Player(userID)
            self.Registered = True
        else:
            self.Registered = False


    def _exist(self, id):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM USER WHERE id = %s", (id))
            recordNum = cursor.fetchone()['count(*)']
        if recordNum == 0:
            return False
        else:
            return True

    def registUser(self, userID, userName):
        with self.connection.cursor() as cursor:
            name = userName
            money = 1000
            position_x = 200
            position_y = 200
            hp = 30
            state = "WORLD"
            battleID = None
            sql = "INSERT INTO EQUIPMENT(equip_weapon, equip_armor) VALUES(1, 1)"
            cursor.execute(sql)
            equipID = cursor.lastrowid
            sql = "INSERT INTO USER VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (userID, name, money, position_x, position_y, hp, state, battleID, equipID)
            print(values)
            cursor.execute(sql, values)
        self.connection.commit()
        world = World(userID)
        imageURI = world.getInitMap()
        return {"worldImg": [imageURI], "text": ["あなたのセーブデータを作成しました！"]}
        
    def step(self, text):
        if self.player is not None:
            if self.player.state == "BATTLE":
                battle = Battle(self.player.userId)
                reply = battle.battle()
                if battle.isFinish == True:
                    world = World(self.player.userId)
                    imageURI = world.getInitMap()
                    reply['battlefinished'] = imageURI
                return reply
            elif self.player.state == "WORLD":
                world = World(self.player.userId)
                imageURI = world.move(text)
                encount, enemyInfo = world.randomEncount()
                if encount:
                    self.player.state = "BATTLE"
                    return {"img": [imageURI, enemyInfo["img"]], "text": [enemyInfo["text"]]}
                return {"worldImg": [imageURI]}
            else:
                return {"text": ["still not implemented"]}