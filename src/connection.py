# -*- coding: gbk -*-
import handler
import time
import packer
import gameobject

CONNECTED = 0
LOGIN = 1
GAME = 2
class connection:
    """连接类，管理用户的信息以及缓存数据及发送消息"""
    def __init__(self, socket = None, handler = None):
        self.socket = socket
        self.address = socket.getpeername()
        self.__state = CONNECTED
        self.__loginTime = 0
        self.totalOnlineTime = 0
        self.handler = handler
        self.__idofenemies = 0;
        self.__waitToRead = 0
        self.__input = ''
        
    def handle(self, data):
        if isinstance(self.handler, handler.handler):
            self.appendInputBuffer(data)
            data = self.read()
            while data:
                res = self.handler.handle(self, data)
                if res:
                    self.socket.sendall(res)
                data = self.read()
        else:
            raise TypeError("The handler must be type of handler!")
    
    def isLogin(self):
        return self.__state == LOGIN
    
    def nextEnemyId(self):
        while (self.spiders.has_key(self.__idofenemies) or self.meches.has_key(self.__idofenemies)):
            self.__idofenemies += 1
        return self.__idofenemies
    
    def login(self, userid, totalOnlineTime):
        self.__state = LOGIN
        self.__loginTime = int(time.time())
        self.player = gameobject.player()
        self.player.userid = userid
        self.__idofenemies = 0;
        self.__waitToRead = 0
        self.__input = ''
        self.totalOnlineTime = totalOnlineTime
    
    def enter(self, roleid):
        self.__state = GAME
        self.spiders = {}
        self.meches = {}
        self.numofequipment = 0
        self.preEquipmentTime = 0.0
        return self.player.select_role(roleid)
        
    def onlineTime(self):
        return int(time.time()) - self.__loginTime
    
    def appendInputBuffer(self, data):
        self.__input += data
        
    def clearInputBuffer(self):
        self.__input = ''
        self.__waitToRead = 0
    
    def send(self, data):
        if (data):
            self.socket.sendall(data)
    #返回一个完整的消息，如果缓存的数据不完整则返回None
    def read(self):
        if not self.__waitToRead:  
            if len(self.__input) >= 4:
                self.__waitToRead = packer.unpackSize(self.__input[:4])
                self.__input = self.__input[4:]
            else:
                return None
        if len(self.__input) >= self.__waitToRead:
            ret = packer.unpackData(self.__input[:self.__waitToRead], self.__waitToRead)
            self.__input = self.__input[self.__waitToRead:]
            if len(self.__input) >= 4:
                self.__waitToRead = packer.unpackSize(self.__input[:4])
                self.__input = self.__input[4:]
            else:
                self.__waitToRead = 0
            return ret
            
        return None
