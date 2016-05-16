# -*- coding: gbk -*-
import math
import logging.config
import random
_logger = logging.getLogger('server')
#��ͼ
tm = [
'111111111111111111111111111111111111111111111111111111111111',
'1..........................................................1',
'1.............................1............................1',
'1.............................1............................1',
'1.............................1............................1',
'1.......S.....................1............................1',
'1.............................1............................1',
'1.............................1............................1',
'1.............................1............................1',
'1.............................1............................1',
'1.............................1............................1',
'1.............................1............................1',
'1.............................1............................1',
'1111111.111111111111111111111111111111111111111............1',
'1....1........1............................................1',
'1....1........1............................................1',
'1....1111111111............................................1',
'1..........................................................1',
'1..........................................................1',
'1..........................................................1',
'1..........................................................1',
'1..........................................................1',
'1...............................11111111111111.............1',
'1...............................1........E...1.............1',
'1...............................1............1.............1',
'1...............................1............1.............1',
'1...............................1............1.............1',
'1...............................11111111111..1.............1',
'1..........................................................1',
'1..........................................................1',
'111111111111111111111111111111111111111111111111111111111111']

#��Ϊpython��string����ֱ�Ӹı�ĳһԪ�أ�������test_map���洢����ʱ�ĵ�ͼ
sence_map = []
map_row = 0
map_col = 0
class Node_Elem:
    """
    �����б�͹ر��б��Ԫ�����ͣ�parent�����ڳɹ���ʱ�����·��
    """
    def __init__(self, parent, x, y):
        self.parent = parent
        self.x = x
        self.y = y
        self.G = self.cal_G()
        self.H = 0.0
        self.F = self.G + self.H
        
    def cal_G(self):
        if self.parent:
            #��������ֱ�ߣ�����Ϊ10��б�ߣ�����Ϊ14
            if self.parent.x == self.x or self.parent.y == self.y:
                return self.parent.G + 1.0
            else:
                return self.parent.G + 1.4
        else:
            return 0
    
    def cal_H(self, e_x, e_y):
        return math.sqrt((e_x-self.x)*(e_x-self.x)+ (e_y-self.y)*(e_y-self.y))*1.2
    
    def cal_F(self, e_x, e_y):
        self.F = self.cal_G() + self.cal_H(e_x, e_y)
        return self.F
            
class A_Star:
    def __init__(self, s_x, s_y, e_x, e_y, width=60, height=30):
        self.s_x = s_x
        self.s_y = s_y
        self.e_x = e_x
        self.e_y = e_y
        
        self.width = width
        self.height = height
        
        self.open = {}
        self.close = {}
        self.path = []
        
    #����·������ں���
    def find_path(self):
        #������ʼ�ڵ�
        node = Node_Elem(None, self.s_x, self.s_y)
        while True:
            #��չFֵ��С�Ľڵ�
            self.extend_round(node)
            #��������б�Ϊ�գ��򲻴���·��������
            if not self.open:
                return
            #��ȡFֵ��С�Ľڵ�
            node = self.get_best()
            #�ҵ�·��������·��������
            if node.x == self.e_x and node.y == self.e_y:
                self.make_path(node)
                return
            #�Ѵ˽ڵ�ѹ��ر��б����ӿ����б���ɾ��
            self.close[(node.x, node.y)] = node
            del self.open[(node.x, node.y)]
            
    def make_path(self,p):
        #�ӽ�������ݵ���ʼ�㣬��ʼ���parent == None
        while p:
            self.path.append((p.x, p.y))
            p = p.parent
        
    def get_best(self):
        nodes = self.open.values()
        best = nodes[0]
        for node in nodes:
            if node.F < best.F:#����ǰ�ĸ��ã���Fֵ��С
                best = node
        return best
        
    def extend_round(self, parent):
        #���Դ�8��������
        xs = (-1, 0, 1, -1, 1, -1, 0, 1)
        ys = (-1,-1,-1,  0, 0,  1, 1, 1)
        for x, y in zip(xs, ys):
            new_x, new_y = x + parent.x, y + parent.y
            #��Ч���߲�����������������
            if not self.is_valid_coord(new_x, new_y):
                continue
            #�����µĽڵ�
            node = Node_Elem(parent, new_x, new_y)
            node.cal_F(self.e_x, self.e_y)
            #�½ڵ��ڹر��б������
            if (node.x, node.y) in self.close:
                continue
            existed_node = self.open.get((node.x, node.y), None)
            if existed_node:
                #�½ڵ��ڿ����б�
                if existed_node.G > node.G:
                    #���ڵ�·��������ǰ������ڵ��·��������ʹ�����ڵ�·��
                    self.open[(node.x, node.y)] = node
            else:
                self.open[(node.x, node.y)] = node
            
    def is_valid_coord(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return sence_map[y][x] != '1'
    
    def get_searched(self):
        return self.open.keys() + self.close.keys()


def print_test_map():
    """
    ��ӡ������ĵ�ͼ
    """
    for line in sence_map:
        print ''.join(line)

def get_start_XY():
    return get_symbol_XY('S')
    
def get_end_XY():
    return get_symbol_XY('E')
    
def get_symbol_XY(s):
    for y, line in enumerate(sence_map):
        try:
            x = line.index(s)
        except:
            continue
        else:
            break
    return x, y
        
def mark_path(l):
    mark_symbol(l, '*')
    
def mark_searched(l):
    mark_symbol(l, ' ')
    
def mark_symbol(l, s):
    for x, y in l:
        sence_map[y][x] = s
    
def mark_start_end(s_x, s_y, e_x, e_y):
    sence_map[s_y][s_x] = 'S'
    sence_map[e_y][e_x] = 'E'
    
def tm_to_test_map():
    for line in tm:
        sence_map.append(list(line))

def file_to_map(path):
    global map_row, map_col, sence_map
    sence_map = []
    with open(path) as f:
        lines  = f.readlines()
        map_row = len(lines);
        if map_row > 0:
            map_col = len(lines[0]) - 1
        for line in lines:
            sence_map.append(list(line[:-1]))
    
    _logger.info("Initialize map finished!")

def get_valid_position():
    x, z = -1, -1
    global map_row, map_col, sence_map
    while x < 0 or z < 0 or sence_map[z][x] == '1':
        x, z = random.randrange(0, map_col), random.randrange(0, map_row)
    
    x, z = x - map_col / 2.0 + 0.5, z - map_row / 2.0 + 0.5
    return (x,z)

def find_path():
    s_x, s_y = get_start_XY()
    e_x, e_y = get_end_XY()
    a_star = A_Star(s_x, s_y, e_x, e_y)
    a_star.find_path()
    searched = a_star.get_searched()
    path = a_star.path
    #�������������
    mark_searched(searched)
    #���·��
    mark_path(path)
    print "path length is %d"%(len(path))
    print "searched squares count is %d"%(len(searched))
    #��ǿ�ʼ��������
    mark_start_end(s_x, s_y, e_x, e_y)
    
if __name__ == "__main__":
    #���ַ���ת���б�
    tm_to_test_map()
    find_path()
    print_test_map()