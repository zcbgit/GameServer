# -*- coding: gbk -*-
import logging
import multiprocessing
import sqlite3

import database
import errcode
import packer
from __builtin__ import str

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
def respone(errcode = 0, errmsg = 'success'):
    if isinstance(errcode, (int, long)) and isinstance(errmsg, (str, unicode)):
        res = {'msgname': 'Respone', 'errcode' : errcode, 'errmsg' : errmsg}
        js = packer.dict2json(res)
        return packer.pack(js)
    else:
        raise TypeError, 'Type error of input!'

def GetRoles(conn, data):
    userId= data.get('userId', None)
    if not userId:
        code = errcode.MISSING_ARGUMENT
        msg = errcode.ERROR_MSG[code] % ('userId, password')
        res = respone(code, msg)
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
                            role = {'roleid' : rr[0][0],
                                    'name' : rr[0][1],
                                    'level' : rr[0][2],
                                    'blood' : rr[0][3],
                                    'armor' : rr[0][4],
                                    'weapon' : rr[0][5],
                                    'attack': rr[0][6],
                                    'ammunition' : rr[0][7],
                                    }
                            res['roles'].append(role)
                res = packer.dict2json(res)
                res = packer.pack(res)
        except sqlite3.Error:
            code = errcode.DATABASE_ERROR
            msg = errcode.ERROR_MSG[code]
            res = respone(code, msg)
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
        res = respone(code, msg)
        _logger.error("login error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        try:
            fields = ['password', 'onlinetime',]
            condictions = ["userId = '%s'"%userId,]
            db = database.DBDriver("server.db")
            r = db.query('userInfo', fields, condictions)
            if r and r[0][0] == password:
                    conn.login(userId, r[0][1])
                    res = respone()
                    _logger.info("user[%s] login! Total online time: %d" %(conn.userid, conn.totalOnlineTime))
            else:
                code = errcode.WRONG_USERID_OR_PASSWORD
                msg = errcode.ERROR_MSG[code]
                res = respone(code, msg)
                _logger.error("login error. errcode[%d],errmsg[%s]" %(code, msg))
        except sqlite3.Error:
            code = errcode.DATABASE_ERROR
            msg = errcode.ERROR_MSG[code]
            res = respone(code, msg)
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
        res = respone(code, msg)
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
                res = respone()
            else:
                code = errcode.USERID_EXISTED
                msg = errcode.ERROR_MSG[code]
                res = respone(code, msg)
                _logger.error("register error. errcode[%d],errmsg[%s]" %(code, msg))
        except sqlite3.Error:
            code = errcode.DATABASE_ERROR
            msg = errcode.ERROR_MSG[code]
            res = respone(code, msg)
            _logger.error("database error. errcode[%d],errmsg[%s]" %(code, msg))
        finally:        
            db.close()
    return res

def CreateRole(conn, data):
    userId, role = data.get('userId', None), data.get('role', None)
    if not userId or not role:
        code = errcode.MISSING_ARGUMENT
        msg = errcode.ERROR_MSG[code] % ('userId, role')
        res = respone(code, msg)
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
                res = respone(code, msg)
                _logger.error("Create role error. errcode[%d],errmsg[%s]" %(code, msg))
            else:
                name, blood, armour, weapon, attack, ammunition = role.get('name', None), role.get('blood', None), role.get('armor', None), role.get('weapon', None), role.get('attack', None), role.get('ammunition', None)
                kvDict = {'name' : name, 'blood' : blood, 'armor' : armour, 'weapon' : weapon, 'attack' : attack, 'ammunition' : ammunition}
                db.insert('roleInfo', kvDict)
                if not r[0][1]:
                    values = ['role1 = (SELECT max(roleid) FROM roleInfo)']
                    db.update('userInfo', values, condictions)
                    res = respone()
                elif not r[0][2]:
                    values = ['role2 = (SELECT max(roleid) FROM roleInfo)']
                    db.update('userInfo', values, condictions)
                    res = respone()
                elif not r[0][3]:
                    values = ['role3 = (SELECT max(roleid) FROM roleInfo)']
                    db.update('userInfo', values, condictions)
                    res = respone()
                else:
                    code = errcode.MAX_ROLE
                    msg = errcode.ERROR_MSG[code]
                    res = respone(code, msg)
                    _logger.error("Create role error. errcode[%d],errmsg[%s]" %(code, msg))
        except sqlite3.Error:
            code = errcode.DATABASE_ERROR
            msg = errcode.ERROR_MSG[code]
            res = respone(code, msg)
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
        res = respone(code, msg)
        _logger.error("Create role error. errcode[%d],errmsg[%s]" %(code, msg))
    else:
        try:
            fields = ['userId', 'role1', 'role2', 'role3']
            condictions = ["userId = '%s'"%userId,]
            db = database.DBDriver("server.db")
            r = db.query('userInfo', fields, condictions)
            if not r:
                code = errcode.USERID_NOT_EXISTED
                msg = errcode.ERROR_MSG[code]
                res = respone(code, msg)
                _logger.error("Create role error. errcode[%d],errmsg[%s]" %(code, msg))
            else:
                if r[0][1] and int(r[0][1]) == roleId:
                    values = ["role1 = ''"]
                    db.update('userInfo', values, condictions)
                    res = respone()
                elif r[0][2] and int(r[0][2]) == roleId:
                    values = ["role2 = ''"]
                    db.update('userInfo', values, condictions)
                    res = respone()
                elif r[0][3] and int(r[0][3]) == roleId:
                    values = ["role3 = ''"]
                    db.update('userInfo', values, condictions)
                    res = respone()
                else:
                    code = errcode.ROLEID_NOT_EXISTED
                    msg = errcode.ERROR_MSG[code]
                    res = respone(code, msg)
                    _logger.error("Delete role error. errcode[%d],errmsg[%s]" %(code, msg))
        except sqlite3.Error:
            code = errcode.DATABASE_ERROR
            msg = errcode.ERROR_MSG[code]
            res = respone(code, msg)
            _logger.error("database error. errcode[%d],errmsg[%s]" %(code, msg))
        finally:
            db.close()
            
    return res

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
               }

class handler():
    
    def handle(self, conn, data):
        if conn and data:
            _logger.debug("Recvive message from (%s:%d). data: %s" %(conn.address[0], conn.address[1], data))
            msg = packer.json2dict(data)
            msgName = msg['msgname']
            fun = callbackMap[msgName]
            return fun(conn, msg) 
        else:
            raise RuntimeError('conn or data is None!')

