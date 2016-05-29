# -*- coding: gbk -*-
import sencemap
# 用户管理对象
class enemy:
    def __init__(self, i, t, HP):
        self.id = i
        self.type = t
        self.HP = HP
        self.position = sencemap.get_valid_position()
        # 记录上一次怪物及玩家的位置，以决定是否重新进行路径规划
        self.preEnemyPos = None
        self.prePlayerPos = None
        
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
        