import os
import sys
import sqlite3
import logging.config

import master
import database
from ConfigParser import ConfigParser

_logger = logging.getLogger('server')

def init_logger():
    if not os.path.exists('log'):
        os.makedirs('log')
        sys.path.append('log')
        
    logging.config.fileConfig('logging.conf')
    _logger.info("Initialise logger!")

def init_database(dbFile):
    db = database.DBDriver(dbFile)
    try:
        sql = 'create table if not exists userInfo (userid varchar(128) primary key, password varchar(128) not null, role1 varchar(128), role2 varchar(128), role3 varchar(128), onlinetime integer default 0)'
        db.execDB(sql)
        sql = 'create table if not exists roleInfo (roleid integer primary key autoincrement, name varchar(128), level integer default 1, blood integer default 100, armor integer default 0, weapon varchar(128), attack integer default 1, ammunition integer default -1)'
        db.execDB(sql)
    except sqlite3.Error:
        _logger.error("Initialise database[%s] failed! SQL[%s]"%(dbFile, sql))
    finally:
        db.close()
    _logger.info("Initialise database!")

if __name__ == '__main__':
    init_logger()

    _logger.info("Initializtion finished!")
    cf = ConfigParser()
    cf.read("settings.ini")
    db_file = cf.get('database', 'db_file')
    init_database(db_file)
    ip, port, workers = cf.get('server', 'ip'), cf.getint('server', 'port'), cf.getint('server', 'workers')
    server = master.master(workers)
    server.init(ip, port)
    server.run()
    