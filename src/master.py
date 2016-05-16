# -*- coding: gbk -*-
import socket
import logging
import worker

class master():

    def __init__(self, workers = 5):
        self._num_workers = workers
        self._workers = []
        self._logger = logging.getLogger('server')
        
    def init(self, ip, port):
        self._server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR , 1)
        if not ip:
            ip = '127.0.0.1'
        if not port:
            port = 8888
        self._server.bind((ip, port))
        self._server.listen(10)
        
        for _ in range(self._num_workers):
            w = worker.worker()
            self._workers.append(w)
    
    def run(self):
        for w in self._workers:
            w.start()
            
        self._logger.info("server running.")
        while True:
            try:
                client, address = self._server.accept()#建立连接
                client.setblocking(0)
                self._logger.info("connection from %s:%d" % address)
                min_payload, min_payload_worker = self._workers[0].payload(), self._workers[0]
                for w in self._workers:
                    pl = w.payload()
                    if pl < min_payload:
                        min_payload, min_payload_worker = pl, w
                
                min_payload_worker.append(client)
    
                
            except KeyboardInterrupt:
                self._logger.info("server shutdown.")
                break