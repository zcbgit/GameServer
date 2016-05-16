# -*- coding: gbk -*-
import sencemap

class spider:
    def __init__(self, i):
        self.id = i
        self.HP = 100.0
        self.position = sencemap.get_valid_position()

class mech:
    def __init__(self, i):
        self.id = i
        self.HP = 100.0
        self.position = sencemap.get_valid_position()
        
class player:
    def __init__(self):
        self.userid = ''
        self.roleid = ''
        self.HP = 100.0
        self.position = (0.0, 0.0)