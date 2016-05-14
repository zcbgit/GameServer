import socket
import packer
from time import sleep

class client:
    def __init__(self, ip = '127.0.0.1', port = 8888):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_address= (ip,port)
        self.socket.connect(server_address)
    
    def run(self):
        try:
            msg = {'msgname' : 'echo', 'msg' : 'test'}
            jstr = packer.dict2json(msg)
            msgstr = packer.pack(jstr)
            for _ in range(50):
                self.socket.sendall(msgstr)
                data = self.socket.recv(1024)
                print data
                sleep(1)
            self.socket.close()
        except Exception:
            exit(1)
            
if __name__ == "__main__":
    c = client()
    c.run()