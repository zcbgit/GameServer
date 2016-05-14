# -*- coding: gbk -*-
"""��Ϣ�����ͽ����ģ��"""
import struct
import json

#����Ϣ��json��ʽ���ַ���ת��dict
def json2dict(jstr):
    msg = json.loads(jstr, encoding='utf-8')
    return msg

#��dict���͵���Ϣ��ת��json��ʽ���ַ���
def dict2json(infoDict):
    res = json.dumps(infoDict, ensure_ascii=False, encoding='utf-8')
    res = res.encode('utf-8')
    return res

#����Ϣ�ַ���ǰ��������Ϣ�峤��
def pack(s):
    if not isinstance(s, basestring):
        raise TypeError("Input is not string")
    return struct.pack('!I%ds'%len(s), len(s), s)

#��ȡ��Ϣ�ĳ���
def unpackSize(s):
    size = struct.unpack('!I', s)[0]
    return size

#��ȡ��Ϣ�ַ���
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