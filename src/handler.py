# -*- coding: gbk -*-
import logging
import multiprocessing
import sqlite3
import time
import traceback

import gameobject
import database
import errcode
import packer

CONNECTED = 0
LOGIN = 1
_logger = logging.getLogger('processor')
_roleLock = multiprocessing.Lock()

#普通响应
def S2CEcho(msg):
    if isinstance(msg, basestring):
        res = {'msgname': 'Echo', 'msg' : msg}
        js = packer.dict2json(res)
        return packer.pack(js)
    else:
        raise TypeError, 'Type error of input!'
#普通响应
def respone(errcode = 0, errmsg = 'success', resmsgname = ''):
    if isinstance(errcode, (int, long)) and isinstance(errmsg, (str, unicode)):
        res = {'msgname': 'Respone', 'errcode' : errcode, 'errmsg' : errmsg, 'resmsgname' : resmsgname}
        js = packer.dict2json(res)
        return packer.pack(js)
    else:
        raise TypeError, 'Type error of input!'

def updatePath(enemyId, path):
    if path:
        res = {'msgname': 'UpdatePath', 'id' : enemyId, 'path' : path}
        js = packer.dict2json(res)
        return packer.pack(js)
    else:
        return None

def updateHp(oid, HP):
    res = {'msgname': 'UpdateHP', 'id' : oid, 'HP' : HP}
    js = packer.dict2json(res)
    return packer.pack(js)

def updateAmmunition(ammunition):
    res = {'msgname': 'UpdateAmmunition', 'ammunition' : ammunition}
    js = packer.dict2json(res)
    return packer.pack(js)

def GetRoles(conn, data):
    userId= data.get('userId', None)
    if not userId:
        code = errcode.MISSING_ARGUMENT
        msg = errcode.ERROR_MSG[code] % ('userId, password')
        res = respone(code, msg, 'GetRoles')
        _logger.error("login error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        try:
            db = database.DBDriver("server.db")
            fields = ['userId', 'role1', 'role2', 'role3']
            condictions = ["userId = '%s'"%userId,]
            r = db.query('userInfo', fields, condictions)
            if not r:
                code = errcode.USERID_NOT_EXISTED
                msg = errcode.ERROR_MSG[code]
                _logger.error("Get role error. errcode[%d],errmsg[%s]" %(code, msg))
            else:
                res = {'msgname': 'Roles', 'userId' : userId, 'roles': []}
                for i in range(3):
                    if r[0][i + 1]:
                        fields = ['*']
                        condictions = ["roleid = %s"%r[0][i + 1],]
                        rr = db.query('roleInfo', fields, condictions)
                        if rr:
                            conn.player.roles[rr[0][0]] = gameobject.role(rr[0])
                            role = {'roleid' : rr[0][0],
                                    'name' : rr[0][1],
                                    'level' : rr[0][2],
                                    'HP' : rr[0][3],
                                    'EXP' : rr[0][4],
                                    'NextLevelExp' : rr[0][5],
                                    'weapon' : rr[0][6],
                                    'attack': rr[0][7],
                                    'ammunition' : rr[0][8],
                                    }
                            res['roles'].append(role)
                res = packer.dict2json(res)
                res = packer.pack(res)
        except sqlite3.Error:
            code = errcode.DATABASE_ERROR
            msg = errcode.ERROR_MSG[code]
            res = respone(code, msg, 'GetRoles')
            _logger.error("database error. errcode[%d],errmsg[%s]" %(code, msg))
        finally:
            db.close()
        
    return res

#登陆逻辑，先验证消息参数是否完整，再验证账号及密码，如果用户已经登陆，则当前连接会将之前登陆的连接挤下线
def Login(conn, data):
    userId, password = data.get('userId', None), data.get('password', None)
    if not userId or not password:
        code = errcode.MISSING_ARGUMENT
        msg = errcode.ERROR_MSG[code] % ('userId, password')
        res = respone(code, msg, 'Login')
        _logger.error("login error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        try:
            fields = ['password', 'onlinetime',]
            condictions = ["userId = '%s'"%userId,]
            db = database.DBDriver("server.db")
            r = db.query('userInfo', fields, condictions)
            if r and r[0][0] == password:
                    conn.login(userId, r[0][1])
                    res = respone(resmsgname = 'Login')
                    _logger.info("user[%s] login! Total online time: %d" %(conn.player.userid, conn.totalOnlineTime))
            else:
                code = errcode.WRONG_USERID_OR_PASSWORD
                msg = errcode.ERROR_MSG[code]
                res = respone(code, msg, 'Login')
                _logger.error("login error. errcode[%d],errmsg[%s]" %(code, msg))
        except sqlite3.Error:
            code = errcode.DATABASE_ERROR
            msg = errcode.ERROR_MSG[code]
            res = respone(code, msg, 'Login')
            _logger.error("database error. errcode[%d],errmsg[%s]" %(code, msg))
        finally:        
            db.close()
    return res
    
#注册用户逻辑，先验证消息参数是否完整，再校验用户名是否存在，若用户名没被使用才能注册成功
def Register(conn, data):
    userId, password = data.get('userId', None), data.get('password', None)
    if not userId or not password:
        code = errcode.MISSING_ARGUMENT
        msg = errcode.ERROR_MSG[code] % ('userId, password')
        res = respone(code, msg, 'Register')
        _logger.error("register error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        try:
            fields = ['userId']
            condictions = ["userId = '%s'"%userId,]
            db = database.DBDriver("server.db")
            r = db.query('userInfo', fields, condictions)
            if not r:
                kvDict = {'userId' : userId, 'password' : password}
                db.insert('userInfo', kvDict)
                res = respone(resmsgname = 'Register')
            else:
                code = errcode.USERID_EXISTED
                msg = errcode.ERROR_MSG[code]
                res = respone(code, msg, 'Register')
                _logger.error("register error. errcode[%d],errmsg[%s]" %(code, msg))
        except sqlite3.Error:
            code = errcode.DATABASE_ERROR
            msg = errcode.ERROR_MSG[code]
            res = respone(code, msg, 'Register')
            _logger.error("database error. errcode[%d],errmsg[%s]" %(code, msg))
        finally:        
            db.close()
    return res

def CreateRole(conn, data):
    userId, role = data.get('userId', None), data.get('role', None)
    if not userId or not role:
        code = errcode.MISSING_ARGUMENT
        msg = errcode.ERROR_MSG[code] % ('userId, role')
        res = respone(code, msg, 'CreateRole')
        _logger.error("Create role error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        try:
            _roleLock.acquire()
            fields = ['userId', 'role1', 'role2', 'role3']
            condictions = ["userId = '%s'"%userId,]
            db = database.DBDriver("server.db")
            r = db.query('userInfo', fields, condictions)
            if not r:
                code = errcode.USERID_NOT_EXISTED
                msg = errcode.ERROR_MSG[code]
                res = respone(code, msg, 'CreateRole')
                _logger.error("Create role error. errcode[%d],errmsg[%s]" %(code, msg))
            else:
                name, HP, EXP, nextLevelExp, weapon, attack, ammunition = role.get('name', None), 100.0, 0, 100, role.get('weapon', None), role.get('attack', None), role.get('ammunition', None)
                kvDict = {'name' : name, 'HP' : HP, 'EXP' : EXP, 'NextLevelExp' : nextLevelExp,'weapon' : weapon, 'attack' : attack, 'ammunition' : ammunition}
                db.insert('roleInfo', kvDict)
                if not r[0][1]:
                    values = ["role1 = (SELECT seq FROM sqlite_sequence where name = 'roleInfo')"]
                    db.update('userInfo', values, condictions)
                    res = respone(resmsgname='CreateRole')
                elif not r[0][2]:
                    values = ["role2 = (SELECT seq FROM sqlite_sequence where name = 'roleInfo')"]
                    db.update('userInfo', values, condictions)
                    res = respone(resmsgname='CreateRole')
                elif not r[0][3]:
                    values = ["role3 = (SELECT seq FROM sqlite_sequence where name = 'roleInfo')"]
                    db.update('userInfo', values, condictions)
                    res = respone(resmsgname='CreateRole')
                else:
                    code = errcode.MAX_ROLE
                    msg = errcode.ERROR_MSG[code]
                    res = respone(code, msg, 'CreateRole')
                    _logger.error("Create role error. errcode[%d],errmsg[%s]" %(code, msg))
        except sqlite3.Error:
            code = errcode.DATABASE_ERROR
            msg = errcode.ERROR_MSG[code]
            res = respone(code, msg, 'CreateRole')
            _logger.error("database error. errcode[%d],errmsg[%s]" %(code, msg))
        finally:
            db.close()
            _roleLock.release()
            
    return res
    
def DeleteRole(conn, data):
    userId, roleId = data.get('userId', None), data.get('roleId', None)
    if not userId or not roleId:
        code = errcode.MISSING_ARGUMENT
        msg = errcode.ERROR_MSG[code] % ('userId, role')
        res = respone(code, msg, 'DeleteRole')
        _logger.error("Delete role error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        try:
            fields = ['userId', 'role1', 'role2', 'role3']
            condictions = ["userId = '%s'"%userId,]
            db = database.DBDriver("server.db")
            r = db.query('userInfo', fields, condictions)
            if not r:
                code = errcode.USERID_NOT_EXISTED
                msg = errcode.ERROR_MSG[code]
                res = respone(code, msg, 'DeleteRole')
                _logger.error("Create role error. errcode[%d],errmsg[%s]" %(code, msg))
            else:
                if r[0][1] and int(r[0][1]) == roleId:
                    values = ["role1 = ''"]
                    db.update('userInfo', values, condictions)
                    res = respone(resmsgname='DeleteRole')
                elif r[0][2] and int(r[0][2]) == roleId:
                    values = ["role2 = ''"]
                    db.update('userInfo', values, condictions)
                    res = respone(resmsgname='DeleteRole')
                elif r[0][3] and int(r[0][3]) == roleId:
                    values = ["role3 = ''"]
                    db.update('userInfo', values, condictions)
                    res = respone(resmsgname='DeleteRole')
                else:
                    code = errcode.ROLEID_NOT_EXISTED
                    msg = errcode.ERROR_MSG[code]
                    res = respone(code, msg, 'DeleteRole')
                    _logger.error("Delete role error. errcode[%d],errmsg[%s]" %(code, msg))
        except sqlite3.Error:
            code = errcode.DATABASE_ERROR
            msg = errcode.ERROR_MSG[code]
            res = respone(code, msg, 'DeleteRole')
            _logger.error("database error. errcode[%d],errmsg[%s]" %(code, msg))
        finally:
            db.close()
            
    return res

def CreateEnemy(conn):
    if (not conn):
        return
    data = []
    while len(conn.spiders) < 1:
        spider = gameobject.enemy(conn.nextEnemyId(), 'spider', 100)
        conn.spiders[spider.id] = spider
        data.append({'id' : spider.id, 'type' : 0, 'HP' : spider.HP, 'x' : spider.position[0], 'z' : spider.position[1]})
    
    while len(conn.meches) < 1:
        mech = gameobject.enemy(conn.nextEnemyId(), 'mech', 150)
        conn.meches[mech.id] = mech
        data.append({'id' : mech.id, 'type' : 1, 'HP' : mech.HP, 'x' : mech.position[0], 'z' : mech.position[1]})
    
    if data:
        res = {'msgname': 'CreateEnemy', 'data' : data}
        res = packer.dict2json(res)
        res = packer.pack(res)
    else:
        res = None
    
    return res

def EnterGame(conn, data):
    userId, roleId = data.get('userId', None), data.get('roleId', None)
    if (userId == None or roleId == None):
        code = errcode.MISSING_ARGUMENT
        msg = errcode.ERROR_MSG[code] % ('userId, role')
        res = respone(code, msg, 'EnterGame')
        _logger.error("EnterGame error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        if conn.enter(roleId):
            res = respone(resmsgname='EnterGame')
        else:
            code = errcode.ROLEID_NOT_EXISTED
            msg = errcode.ERROR_MSG[code]
            res = respone(code, msg, 'EnterGame')
            _logger.error("EnterGame error. errcode[%d],errmsg[%s]" %(code, msg))
    return res

def EnemyData(conn, data):
    userId, objs = data.get('userId', None), data.get('data', None)
    if (userId == None or objs == None):
        code = errcode.MISSING_ARGUMENT
        msg = errcode.ERROR_MSG[code] % ('userId, role, data')
        res = respone(code, msg, 'EnemyData')
        _logger.error("EnemyData error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        res = None
        if objs[0] == 0:
            enemies = conn.spiders
        elif objs[0] == 1:
            enemies = conn.meches
        else:
            enemies = None
        if enemies:
            enemyId = int(objs[1])
            enemy = enemies.get(enemyId, None)
            #enemy.HP = objs[2]
            if (enemy):
                enemy.position = (objs[2], objs[3])
                path = enemy.Plan_Path(conn.player.position)
                return updatePath(enemyId, path)
             
    return res

def CreateEquipment(conn):
    if conn.numofequipment < 3:
        eq = gameobject.equipment()
        conn.numofequipment += 1
        res = {'msgname': 'CreateEquipment', 'X' : eq.position[0], 'Z' : eq.position[1]}
        js = packer.dict2json(res)
        res =  packer.pack(js)
        return res
    else:
        return None

def PlayerData(conn, data):
    userId, roleId, objs = data.get('userId', None), data.get('roleId', None), data.get('data', None)
    if (userId == None or roleId == None or objs == None):
        code = errcode.MISSING_ARGUMENT
        msg = errcode.ERROR_MSG[code] % ('userId, role, data')
        res = respone(code, msg, 'EnemyData')
        _logger.error("PlayerData error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        conn.player.position = (objs[0], objs[1])
        t = time.time()
        if int(t) % 5 == 0: # 每10s刷新一次怪
            r1 = CreateEnemy(conn)
        else:
            r1 = None
        #print (t, conn.preEquipmentTime + 300)
        if conn.preEquipmentTime == 0.0 or t > conn.preEquipmentTime + 300: # 每300s刷新一次箱子
            r2 = CreateEquipment(conn)
            conn.preEquipmentTime = t
        else:
            r2 = None 
        if r1 and r2:
            res = r1 + r2
        elif r1:
            res = r1
        elif r2:
            res = r2
        else:
            res = None
            
    return res

def LevelUp(conn):
    try:
        _roleLock.acquire()
        db = database.DBDriver("server.db")
        condictions = ['roleid = %d' % conn.player.role.roleid]
        if conn.player.role.EXP >= conn.player.role.nextLevelExp:
            conn.player.role.EXP = conn.player.role.EXP - conn.player.role.nextLevelExp
            conn.player.role.nextLevelExp = int(conn.player.role.nextLevelExp * 1.5)
            conn.player.role.level += 1
            conn.player.role.maxHP += 20 
            if (conn.player.role.ammunition != -1):
                conn.player.role.ammunition = int(conn.player.role.ammunition * 1.1)
            values = ['level = %d'%conn.player.role.level, 'HP = %d' %conn.player.role.maxHP, 'EXP = %d' % conn.player.role.EXP, 'NextLevelExp = %d' % conn.player.role.nextLevelExp, 'ammunition = %d' %conn.player.role.ammunition]
        else:
            values = ['EXP = %d' % conn.player.role.EXP,]
        
        db.update('roleInfo', values, condictions)
    except sqlite3.Error:
        code = errcode.DATABASE_ERROR
        msg = errcode.ERROR_MSG[code]
        res = respone(code, msg, 'LevelUp')
        _logger.error("database error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        res = {'msgname': 'LevelUp', 'EXP' : conn.player.role.EXP, 'NextLevelExp' : conn.player.role.nextLevelExp, 'Level' : conn.player.role.level, 'HP' : conn.player.role.maxHP}
        js = packer.dict2json(res)
        res =  packer.pack(js)
    finally:
        db.close()
        _roleLock.release()
        return res

def Damage(conn, data):
    damageType, victim, oid = data.get('type', None), data.get('victim', None), data.get('id', None)
    if (damageType == None or victim == None or oid == None):
        code = errcode.MISSING_ARGUMENT
        msg = errcode.ERROR_MSG[code] % ('type, victim, id')
        res = respone(code, msg, 'Damage')
        _logger.error("Create role error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        res = None
        
        if (type == 0):
            damage = 10
        elif (type == 1):
            damage = 20
        else:
            damage = 10
        
        if (victim == 0):
            conn.player.role.HP -= damage
            res = updateHp(-1, conn.player.role.HP)
        elif (victim == 1):
            spider = conn.spiders.get(oid, None)
            if (spider):
                spider.HP -= damage
                res = updateHp(spider.id, spider.HP)
                if (spider.HP <= 0.0):
                    del conn.spiders[oid]
                    conn.player.role.EXP += 10
                    res += LevelUp(conn)
        elif (victim == 2):
            mech = conn.meches.get(oid, None)
            if (mech):
                mech.HP -= damage
                res = updateHp(mech.id, mech.HP)
                if (mech.HP <= 0.0):
                    del conn.meches[oid]
                    conn.player.role.EXP += 20
                    res += LevelUp(conn)

    return res

def GetEquipment(conn, data):
    conn.numofequipment -= 1
    HP = conn.player.role.HP + 50
    if HP > conn.player.role.maxHP:
        HP = conn.player.role.HP = conn.player.role.maxHP
    
    return updateHp(-1, HP) + updateAmmunition(int(conn.player.role.ammunition * 0.5))

def Echo(conn, data):
    msg = data.get('msg', None)
    return S2CEcho(msg)
    
callbackMap = {
               'Login' : Login,
               'Register' : Register,
               'Echo' : Echo,
               'GetRoles': GetRoles,
               'CreateRole': CreateRole,
               'DeleteRole' : DeleteRole,
               'EnterGame' : EnterGame,
               'PlayerData' : PlayerData,
               'EnemyData' : EnemyData,
               'Damage' : Damage,
               'GetEquipment' : GetEquipment,
               }

class handler():
    
    def handle(self, conn, data):
        if conn and data:
            #_logger.debug("Recvive message from (%s:%d). data: %s" %(conn.address[0], conn.address[1], data))
            try:
                msg = packer.json2dict(data)
                msgName = msg['msgname']
                fun = callbackMap.get(msgName,None);
                if fun == None:
                    code = errcode.ERROR_MSGNAME
                    msg = errcode.ERROR_MSG[code] % (msgName)
                    res = respone(code, msg)
                    _logger.error("Error msgname[%s]." %(msgName))
                    return res
                else:
                    return fun(conn, msg)
            except:
                code = errcode.PARSE_ERROR
                msg = errcode.ERROR_MSG[code]
                res = respone(code, msg)
                _logger.error(traceback.format_exc())
                return res
        else:
            raise RuntimeError('conn or data is None!')

