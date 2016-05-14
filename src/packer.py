# -*- coding: gbk -*-
"""消息体打包和解包的模块"""
import struct
import json

#将消息从json格式的字符串转成dict
def json2dict(jstr):
    msg = json.loads(jstr, encoding='utf-8')
    return msg

#将dict类型的消息体转成json格式的字符串
def dict2json(infoDict):
    res = json.dumps(infoDict, ensure_ascii=False, encoding='utf-8')
    res = res.encode('utf-8')
    return res

#再消息字符串前，加上消息体长度
def pack(s):
    if not isinstance(s, basestring):
        raise TypeError("Input is not string")
    return struct.pack('!I%ds'%len(s), len(s), s)

#获取消息的长度
def unpackSize(s):
    size = struct.unpack('!I', s)[0]
    return size

#获取消息字符串
def unpackData(s, size):
    ret = struct.unpack('%ds'%size, s)[0]
    return ret

if __name__ == '__main__':
    msg = {"msgname" : "CreateRole", "userId": "", "role":{"id":0,"name":"aa","level":0,"blood":100,"armor":0,"weapon":"Ak-47","attack":1,"ammunition":11}}
    jstr = dict2json(msg)
    msgstr = pack(jstr)
    size = unpackSize(msgstr[:4])
    jstr = unpackData(msgstr[4:], size)
    d = json2dict(jstr)
    print str(d)