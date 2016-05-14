# -*- coding: gbk -*-
import threading
import select
import socket
import multiprocessing
import logging
import player
import handler

class worker(threading.Thread):
    '''工作线程'''

    def __init__(self, **kwargs):
        threading.Thread.__init__(self, kwargs=kwargs)
        self.setDaemon(True)
        self._conn_sockets = {}
        self._lock = multiprocessing.Lock()
        self._logger = logging.getLogger('server')
    
    def get_list(self):
        self._lock.acquire()
        l = self._conn_sockets.keys()
        self._lock.release()
        return l
    
    def payload(self):
        self._lock.acquire()
        n = len(self._conn_sockets)
        self._lock.release()
        return n
    
    def append(self, socket):
        self._add_scoket(socket)
    
    def _add_scoket(self, socket):
        self._lock.acquire()
        if socket not in self._conn_sockets:
            conn = player.connection(socket, handler.handler())
            self._conn_sockets[socket] = conn
        self._lock.release()
        
    def _close_socket(self, socket):
        if socket:
            self._lock.acquire()

            if socket in self._conn_sockets:
                log = "%s:%d is closed" % socket.getpeername()
                socket.close()
                del self._conn_sockets[socket]
            else:
                log = "%s:%d is not existed!" % socket.getpeername()
            self._lock.release()
            self._logger.info(log)
        
    def run(self):
        while True:
            rlist = self.get_list()
            if not rlist:
                continue
            readable , _, exceptional = select.select(rlist, [], rlist, 0.5)

            for s in exceptional:
                address = s.getpeername()
                self._logger.error("exception condition on %s:%d"%(address[0], address[1]))
                #关闭出现异常的链接
                self._close_socket(s)
            
            for s in readable :
                try:
                    address = s.getpeername()
                    data = s.recv(10240)
                except socket.error, arg:
                    (errno, err_msg) = arg
                    self._logger.error("exception condition on %s:%d. errno[%d], err_msg: %s"% (address[0], address[1], errno, err_msg))
                    #关闭出现异常的链接
                    self._close_socket(s)
                else:
                    if not data:             
                        self._close_socket(s)
                    else:
                        conn = self._conn_sockets.get(s, None)
                        if conn:
                            try:
                                conn.handle(data)
                            except socket.error, arg:
                                (errno, err_msg) = arg
                                self._logger.error("exception condition on %s:%d. errno[%d], err_msg: %s"% (address[0], address[1], errno, err_msg))
                                #关闭出现异常的链接
                                self._close_socket(s)
    