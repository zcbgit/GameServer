# -*- coding: gbk -*-
"""数据库操作类"""
import sqlite3
import logging
import multiprocessing

_logger = logging.getLogger('dblog')

class DBDriver:
    lock = multiprocessing.Lock()
    def __init__(self, dbFile):
        self.__dbFile = dbFile
        self.__connection = sqlite3.connect(database = self.__dbFile, isolation_level = None)
        self.__cursor = self.__connection.cursor()
        self.__closed = False
        _logger.info("connected to database[%s]"%self.__dbFile)
    
    def insert(self, tableName, kvDict):
        keys, values = '', ''
        for k in kvDict:
            keys += "%s, "%k
            if isinstance(kvDict[k], (str, unicode)):
                values += ("'%s', "%kvDict[k])
            else:
                values += "%s, "%str(kvDict[k])
        sql = "insert into %s(%s) values (%s)"%(tableName, keys[:-2], values[:-2])
        DBDriver.lock.acquire()
        try:
            self.__cursor.execute(sql)
        except sqlite3.Error, e:
            _logger.error("insert record into table[%s] of database[%s] failed: %s. SQL[%s]"%(tableName, self.__dbFile, e.args[0], sql))
            raise
        else:
            _logger.info("insert record into table[%s] of database[%s] success. SQL[%s]"%(tableName, self.__dbFile, sql))
            self.__connection.commit()
        finally:
            DBDriver.lock.release()
    
    def update(self, tableName, values, condictions):
        sql = 'update %s set %s where %s'%(tableName, ', '.join(values), ' and '.join(condictions))
        DBDriver.lock.acquire()
        try:
            self.__cursor.execute(sql)
        except sqlite3.Error, e:
            _logger.error("update record into table[%s] of database[%s] failed: %s. SQL[%s]"%(tableName, self.__dbFile, e.args[0], sql))
            raise
        else:
            _logger.info("update record into table[%s] of database[%s] success. SQL[%s]"%(tableName, self.__dbFile, sql))
            self.__connection.commit()  
        finally:
            DBDriver.lock.release()
        
    def delete(self, tableName, condictions = ''):
        if condictions:
            sql = "delete from %s where %s" %(tableName, ' and '.join(condictions))
        else:
            sql = "delete from " + tableName
        DBDriver.lock.acquire()
        try:
            self.__cursor.execute(sql)
        except sqlite3.Error, e:
            _logger.error("delete record from table[%s] of database[%s] failed: %s. SQL[%s]"%(tableName, self.__dbFile, e.args[0], sql))
            raise
        else:
            _logger.info("delete record from table[%s] of database[%s] success. SQL[%s]"%(tableName, self.__dbFile, sql))
            self.__connection.commit()
        finally:
            DBDriver.lock.release()
        
    def drop(self, tableName):
        DBDriver.lock.release()
        try:
            self.__cursor.execute("drop table if exists " + tableName)
        except sqlite3.Error, e:
            _logger.error("drop table[%s] of database[%s] failed: %s"%(tableName, self.__dbFile, e.args[0]))
            raise
        else:
            _logger.info("drop table[%s] of database[%s] success."%(tableName, self.__dbFile))
            self.__connection.commit()
        finally:
            DBDriver.lock.release()

    def execDB(self, execsql):
        DBDriver.lock.acquire() 
        try:
            self.__cursor.execute(execsql)
        except sqlite3.Error, e:
            _logger.error("execute failed in database[%s]: %s. SQL[%s]"%(self.__dbFile, e.args[0], execsql))
            raise
        else:
            _logger.info("execute success in database[%s]. SQL[%s]"%(self.__dbFile, execsql))
            self.__connection.commit()
        finally:
            DBDriver.lock.release()

    def query(self, tableName, fields, condictions = ''):
        if condictions:
            sql = 'select %s from %s where %s' %(', '.join(fields), tableName, ' and '.join(condictions))
        else:
            sql = 'select %s from %s' %(', '.join(fields), tableName)
        DBDriver.lock.acquire()
        try:
            self.__cursor.execute(sql)
            res = self.__cursor.fetchall()
        except sqlite3.Error, e:
            _logger.error("query records failed from table[%s] of database[%s]: %s. SQL[%s]"%(tableName, self.__dbFile, e.args[0], sql))
            raise
        finally:
            DBDriver.lock.release()
        _logger.info("query records success from table[%s] of database[%s]. SQL[%s]"%(tableName, self.__dbFile, sql))
        return res
    
    def close(self):
        self.__cursor.close()
        self.__connection.close()
        self.__closed = True
    
    def __del__(self):
        if not self.__closed:
            self.close()

if __name__ == '__main__':
    dbFile = "server.db"
    tableName = 'userInfo'
    db = DBDriver(dbFile)
    fields = ['userid varchar(128) primary key', 'password varchar(128) not null', 'onlinetime integer default 0']
    db.cerateTable(tableName, fields)
    kvDict = {'userid' : 'netease1', 'password' : '123', 'onlinetime':0}
    db.insert(tableName, kvDict)
    needFields = ['userid', 'password', 'lastLogin']
    res = db.query(tableName, needFields)
    db.closeDB()

    print 'query result:'
    for line in res:
        print line