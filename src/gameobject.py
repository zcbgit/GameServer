# -*- coding: gbk -*-
import sencemap

class enemy:
    def __init__(self, i, t, HP):
        self.id = i
        self.type = t
        self.HP = HP
        self.position = sencemap.get_valid_position()
        self.pather = sencemap.A_Star(sencemap.map_col, sencemap.map_row)
    
    def Plan_Path(self, play_position):
        if 10.0 < sencemap.distance(self.position, play_position) < 25.0:
            path = self.pather.find_path(
                                         int(self.position[0] + sencemap.map_col / 2.0), 
                                         int(self.position[1] + sencemap.map_row / 2.0), 
                                         int(play_position[0] + sencemap.map_col / 2.0), 
                                         int(play_position[1] + sencemap.map_row / 2.0))
            if path:
                res = []
                for x, z in path:
                    res.append((x - sencemap.map_col / 2.0 + 0.5, z - sencemap.map_row / 2.0 + 0.5))
                return res
        
class equipment:
    def __init__(self):
        self.position = sencemap.get_valid_position()

class role:
    def __init__(self, data):
        self.roleid = data[0]
        self.name = data[1]
        self.level = data[2]
        self.maxHP = data[3]
        self.HP = self.maxHP
        self.EXP = data[4]
        self.nextLevelExp = data[5]
        self.weapon = data[6]
        self.attack = data[7]
        self.ammunition = data[8]

class player:
    def __init__(self):
        self.userid = ''
        self.roles = {}
        self.role = None
        self.position = (0.0, 0.0)
        
    def select_role(self, roleid):
        self.role = self.roles.get(roleid, None)
        if self.role:
            return True
        else:
            return False
        