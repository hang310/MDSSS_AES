import gf256
import galois
import numpy as np
import datetime
from threading import Thread
import socket
import random
import time

GF256 = galois.GF(2**8, irreducible_poly=galois.Poly.Degrees([8,4,3,1,0]))

alpha_3p = GF256([2,3,4])
alpha_4p = GF256([2,3,4,5])

broadcast_time = 0
#broadcast_time = datetime.datetime.now()
#broadcast_time = time.time()
#original_time = broadcast_time
def initialize_globals():
    global broadcast_time
    broadcast_time = 0
    #original_time = broadcast_time
    #global origin_time
    #broadcast_time = 0
    #origin_time = None

initialize_globals()


def reconstruct(alpha,i1,i2):
    A = GF256([[1,alpha[0]],[1,alpha[1]]])
    B = np.linalg.inv(A)
    C = GF256([[i1],[i2]])
    D = B@C
    return D[0,0]

def reconstruct_34(alpha,i1,i2):
    A = GF256([[1,alpha[2]],[1,alpha[3]]])
    B = np.linalg.inv(A)
    C = GF256([[i1],[i2]])
    D = B@C
    return D[0,0]

def reconstruce_13(alpha,i1,i2):
    A = GF256([[1,alpha[0]],[1,alpha[2]]])
    B = np.linalg.inv(A)
    C = GF256([[i1],[i2]])
    D = B@C
    return D[0,0]


def list_to_string(list_input):
    result_string = " ".join(str(int(element)) for element in list_input)
    return result_string

def string_to_list(string_input):
    string_list = string_input.split()
    result_list = list(map(int, string_list))
    for i in range(len(result_list)):
        result_list[i] = GF256(result_list[i])
    return result_list


class shamir_secret_sharing256():         #only for n=4,k=2
    def __init__(self,input,alpha,n):     #the input "alpha" should be GF256 array
        self.n = n
        if self.n == 4:
            self.alpha = alpha
            #self.alpha = GF256.Random(4)     #可能出现范德蒙矩阵的非满秩，可以使用以下代码指定alpha
            #self.alpha = GF256([2,3,4,5])
            self.poly_coff = GF256.Random(1)[0]
            self.f_1 = input + self.alpha[0]*self.poly_coff
            self.f_2 = input + self.alpha[1]*self.poly_coff
            self.f_3 = input + self.alpha[2]*self.poly_coff
            self.f_4 = input + self.alpha[3]*self.poly_coff
        if self.n == 3:
            self.alpha = alpha   #同理
            #self.alpha = GF256([2,3,4])
            self.poly_coff = GF256.Random(1)[0]
            self.f_1 = input + self.alpha[0] * self.poly_coff
            self.f_2 = input + self.alpha[1] * self.poly_coff
            self.f_3 = input + self.alpha[2] * self.poly_coff

    def getval(self):
        if self.n == 4:
            return [self.f_1,self.f_2,self.f_3,self.f_4]
        if self.n == 3:
            return [self.f_1,self.f_2,self.f_3]

    def getalpha(self):
        return self.alpha

    def getlambda(self):
        if self.n==4:
            A = GF256([[1,self.alpha[0],self.alpha[0]**2,self.alpha[0]**3],
                       [1,self.alpha[1],self.alpha[1]**2,self.alpha[1]**3],
                       [1,self.alpha[2],self.alpha[2]**2,self.alpha[2]**3],
                       [1,self.alpha[3],self.alpha[3]**2,self.alpha[3]**3]])
            B = np.linalg.inv(A)
            return B[0]
        if self.n==3:
            A = GF256([[1,self.alpha[0],self.alpha[0]**2],
                       [1,self.alpha[1],self.alpha[1]**2],
                       [1,self.alpha[2],self.alpha[2]**2]])
            B = np.linalg.inv(A)
            return B[0]

    def reconstruct(self,i1,i2):
        A = GF256([[1,self.alpha[0]],[1,self.alpha[1]]])
        B = np.linalg.inv(A)
        C = GF256([[i1],[i2]])
        D = B@C
        return D[0,0]

class Player():
    Num_player = 0
    def __init__(self,ip='localhost', rec_port=5000):
        self.no = Player.Num_player
        Player.Num_player += 1
        self.ip = ip
        self.rec_port = rec_port


    def send_num(self,number, target_ip, target_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        rec_data = s.recv(100).decode()
        self.rec_data = GF256(int(rec_data))
        s.send(str(int(number)).encode())
        s.close()
        #print(self.rec_data)

    def prep_rec(self,send_msg):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.rec_port))
        s.listen(1)
        self.conn, self.addr = s.accept()
        self.soc=s
        self.conn.send(str(int(send_msg)).encode())
        data = self.conn.recv(100).decode()
        data = GF256(int(data))
        self.conn.close()
        self.soc.close()
        #self.rec_port += 1
        self.other = data
        #print(self.other)


    def oneway_send(self, send_msg, target_ip, target_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        s.send(str(int(send_msg)).encode())
        s.close()


    def oneway_rec(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.rec_port))
        s.listen(1)
        self.conn, self.addr = s.accept()
        self.soc=s
        data = self.conn.recv(100).decode()
        self.conn.close()
        self.soc.close()
        self.oneway_other = GF256(int(data))


class ComputePlayer3p_method1(Player):
    read_bits_cnt_0 = 0
    read_bits_cnt_1 = 0
    read_bits_cnt_2 = 0
    def __init__(self,ip='localhost', rec_port=5000):
        super().__init__(ip,rec_port)
        self.x = 0
        self.x2 = 0
        self.x4 = 0
        self.x8 = 0
        self.x9 = 0
        self.x18 = 0
        self.x19 = 0
        self.x36 = 0
        self.x55 = 0
        self.x72 = 0
        self.x127 = 0
        self.x254 = 0
        self.rand = 0
        self.mult_send0 = 0
        self.mult_send1 = 0
        self.mult_send2 = 0
        self.mult_recv0 = 0
        self.mult_recv1 = 0
        self.mult_recv2 = 0
        self.tobemul1 = 0
        self.tobemul2 = 0
        self.res_mul = 0
        self.mult_send0_1 = 0
        self.mult_send1_1 = 0
        self.mult_send2_1 = 0
        self.mult_recv0_1 = 0
        self.mult_recv1_1 = 0
        self.mult_recv2_1 = 0
        self.tobe1 = 0
        self.tobe2 = 0
        self.res_mul1 = 0

        self.open = 0

        self.mem = 0

    def set_input(self,input):
        self.input = input

    def set_key(self,key):
        self.key = key

    def read_prepared_bits(self,no):
        with open(f"./prepared/three_party/party{no}.txt", 'r') as f:
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip().split(" ")
            self.prepared_bits = tmp

    def get_prepared_bits(self):
        if self.no == 0:
            res = GF256(self.prepared_bits[ComputePlayer3p_method1.read_bits_cnt_0])
            ComputePlayer3p_method1.read_bits_cnt_0 +=1
            return res
        if self.no == 1:
            res = GF256(self.prepared_bits[ComputePlayer3p_method1.read_bits_cnt_1])
            ComputePlayer3p_method1.read_bits_cnt_1 +=1
            return res
        if self.no == 2:
            res = GF256(self.prepared_bits[ComputePlayer3p_method1.read_bits_cnt_2])
            ComputePlayer3p_method1.read_bits_cnt_2 +=1
            return res

    def set_x(self,x):
        self.x = x

    def gen_rand(self):
        self.rand = GF256(random.randint(1,255))

    def set_mult(self,a,b):
        self.tobemul1 = a
        self.tobemul2 = b

    def set_mult_parallel(self,a,b):
        self.tobe1 = a
        self.tobe2 = b

    def send_num_parallel(self,number1,number2, target_ip, target_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        rec_data = s.recv(100).decode()
        self.rec_data_parallel0 = GF256(int(rec_data.split(" ")[0]))
        self.rec_data_parallel1 = GF256(int(rec_data.split(" ")[1]))
        s.send(str(str(int(number1))+" "+str(int(number2))).encode())
        s.close()

    def prep_rec_parallel(self,send_msg1,send_msg2):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.rec_port))
        s.listen(1)
        self.conn, self.addr = s.accept()
        self.soc=s
        self.conn.send(str(str(int(send_msg1))+" "+str(int(send_msg2))).encode())
        data = self.conn.recv(100).decode()
        self.conn.close()
        self.soc.close()
        #self.rec_port += 1
        self.other_parallel0 = GF256(int(data.split(" ")[0]))
        self.other_parallel1 = GF256(int(data.split(" ")[1]))


class ComputePlayer3p_method2(Player):
    read_bits_cnt_0 = 0
    read_bits_cnt_1 = 0
    read_bits_cnt_2 = 0
    def __init__(self,ip='localhost', rec_port=5000):
        super().__init__(ip,rec_port)
        self.x = 0
        self.x2 = 0
        self.x3 = 0
        self.x4 = 0
        self.x7 = 0
        self.x8 = 0
        self.x15 = 0
        self.x16 = 0
        self.x31 = 0
        self.x32 = 0
        self.x63 = 0
        self.x64 = 0
        self.x127 = 0
        self.x254 = 0
        self.rand = 0
        self.mult_send0 = 0
        self.mult_send1 = 0
        self.mult_send2 = 0
        self.mult_recv0 = 0
        self.mult_recv1 = 0
        self.mult_recv2 = 0
        self.tobemul1 = 0
        self.tobemul2 = 0
        self.res_mul = 0
        self.mult_send0_1 = 0
        self.mult_send1_1 = 0
        self.mult_send2_1 = 0
        self.mult_recv0_1 = 0
        self.mult_recv1_1 = 0
        self.mult_recv2_1 = 0
        self.tobe1 = 0
        self.tobe2 = 0
        self.res_mul1 = 0

        self.open = 0

        self.mem = 0

    def set_input(self,input):
        self.input = input

    def set_key(self,key):
        self.key = key

    def read_prepared_bits(self,no):
        with open(f"./prepared/three_party/party{no}.txt", 'r') as f:
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip().split(" ")
            self.prepared_bits = tmp

    def get_prepared_bits(self):
        if self.no == 0:
            res = GF256(self.prepared_bits[ComputePlayer3p_method1.read_bits_cnt_0])
            ComputePlayer3p_method1.read_bits_cnt_0 +=1
            return res
        if self.no == 1:
            res = GF256(self.prepared_bits[ComputePlayer3p_method1.read_bits_cnt_1])
            ComputePlayer3p_method1.read_bits_cnt_1 +=1
            return res
        if self.no == 2:
            res = GF256(self.prepared_bits[ComputePlayer3p_method1.read_bits_cnt_2])
            ComputePlayer3p_method1.read_bits_cnt_2 +=1
            return res

    def set_x(self,x):
        self.x = x

    def gen_rand(self):
        self.rand = GF256(random.randint(1,255))

    def set_mult(self,a,b):
        self.tobemul1 = a
        self.tobemul2 = b

    def set_mult_parallel(self,a,b):
        self.tobe1 = a
        self.tobe2 = b

    def send_num_parallel(self,number1,number2, target_ip, target_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        rec_data = s.recv(100).decode()
        self.rec_data_parallel0 = GF256(int(rec_data.split(" ")[0]))
        self.rec_data_parallel1 = GF256(int(rec_data.split(" ")[1]))
        s.send(str(str(int(number1))+" "+str(int(number2))).encode())
        s.close()

    def prep_rec_parallel(self,send_msg1,send_msg2):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.rec_port))
        s.listen(1)
        self.conn, self.addr = s.accept()
        self.soc=s
        self.conn.send(str(str(int(send_msg1))+" "+str(int(send_msg2))).encode())
        data = self.conn.recv(100).decode()
        self.conn.close()
        self.soc.close()
        #self.rec_port += 1
        self.other_parallel0 = GF256(int(data.split(" ")[0]))
        self.other_parallel1 = GF256(int(data.split(" ")[1]))


class ComputePlayer3p_method3(Player):
    read_shares_cnt_0 = 0
    read_shares_cnt_1 = 0
    read_shares_cnt_2 = 0
    read_bits_cnt_0 = 0
    read_bits_cnt_1 = 0
    read_bits_cnt_2 = 0
    def __init__(self,ip='localhost', rec_port=5000):
        super().__init__(ip,rec_port)
        self.x = 0
        self.x2 = 0
        self.x4 = 0
        self.x8 = 0
        self.x16 = 0
        self.x32 = 0
        self.x64 = 0
        self.x128 = 0
        self.x254 = 0
        self.x6 = 0
        self.x24 = 0
        self.x96 = 0
        self.x30 = 0
        self.x224 = 0
        self.rand = 0
        self.mult_send0 = 0
        self.mult_send1 = 0
        self.mult_send2 = 0
        self.mult_recv0 = 0
        self.mult_recv1 = 0
        self.mult_recv2 = 0
        self.tobemul1 = 0
        self.tobemul2 = 0
        self.res_mul = 0

        self.mult_send0_1 = 0
        self.mult_send1_1 = 0
        self.mult_send2_1 = 0
        self.mult_recv0_1 = 0
        self.mult_recv1_1 = 0
        self.mult_recv2_1 = 0
        self.tobe1 = 0
        self.tobe2 = 0
        self.res_mul1 = 0

        self.mult_send0_2 = 0
        self.mult_send1_2 = 0
        self.mult_send2_2 = 0
        self.mult_recv0_2 = 0
        self.mult_recv1_2 = 0
        self.mult_recv2_2 = 0
        self.tob1 = 0
        self.tob2 = 0
        self.res_mul2 = 0

        self.open = 0

        self.mem = 0

    def set_input(self,input):
        self.input = input

    def set_key(self,key):
        self.key = key

    def read_prepared_bits(self,no):
        with open(f"./prepared/three_party/party{no}.txt", 'r') as f:
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip().split(" ")
            self.prepared_bits = tmp

    def get_prepared_bits(self):
        if self.no == 0:
            res = GF256(self.prepared_bits[ComputePlayer3p_method3.read_bits_cnt_0])
            ComputePlayer3p_method3.read_bits_cnt_0 +=1
            return res
        if self.no == 1:
            res = GF256(self.prepared_bits[ComputePlayer3p_method3.read_bits_cnt_1])
            ComputePlayer3p_method3.read_bits_cnt_1 +=1
            return res
        if self.no == 2:
            res = GF256(self.prepared_bits[ComputePlayer3p_method3.read_bits_cnt_2])
            ComputePlayer3p_method3.read_bits_cnt_2 +=1
            return res

    def read_prepared_shares(self,no):
        with open(f"./prepared_random/three_party/party{no}.txt", 'r') as f:
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip().split(" ")
            self.prepared_shares = tmp

    def get_prepared_shares(self):
        if self.no == 0:
            res = GF256(self.prepared_shares[ComputePlayer3p_method3.read_shares_cnt_0])
            ComputePlayer3p_method3.read_shares_cnt_0 +=1
            return res
        if self.no == 1:
            res = GF256(self.prepared_shares[ComputePlayer3p_method3.read_shares_cnt_1])
            ComputePlayer3p_method3.read_shares_cnt_1 +=1
            return res
        if self.no == 2:
            res = GF256(self.prepared_shares[ComputePlayer3p_method3.read_shares_cnt_2])
            ComputePlayer3p_method3.read_shares_cnt_2 +=1
            return res

    def set_x(self,x):
        self.x = x

    def gen_rand(self):
        self.rand = GF256(random.randint(1,255))

    def set_mult(self,a,b):
        self.tobemul1 = a
        self.tobemul2 = b

    def set_mult_parallel(self,a,b):
        self.tobe1 = a
        self.tobe2 = b

    def set_mult_treble(self,a,b):
        self.tob1 = a
        self.tob2 = b

    def send_num_parallel(self,number1,number2, target_ip, target_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        rec_data = s.recv(100).decode()
        tmp = rec_data.split(" ")
        self.rec_data_parallel0 = GF256(int(tmp[0]))
        self.rec_data_parallel1 = GF256(int(tmp[1]))
        s.send(str(str(int(number1))+" "+str(int(number2))).encode())
        s.close()

    def prep_rec_parallel(self,send_msg1,send_msg2):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.rec_port))
        s.listen(1)
        self.conn, self.addr = s.accept()
        self.soc=s
        self.conn.send(str(str(int(send_msg1))+" "+str(int(send_msg2))).encode())
        data = self.conn.recv(100).decode()
        self.conn.close()
        self.soc.close()
        #self.rec_port += 1
        tmp = data.split(" ")
        self.other_parallel0 = GF256(int(tmp[0]))
        self.other_parallel1 = GF256(int(tmp[1]))

    def send_num_treble(self,number1,number2,number3, target_ip, target_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        rec_data = s.recv(100).decode()
        tmp = rec_data.split(" ")
        self.rec_data_parallel0 = GF256(int(tmp[0]))
        self.rec_data_parallel1 = GF256(int(tmp[1]))
        self.rec_data_parallel2 = GF256(int(tmp[2]))
        s.send(str(str(int(number1))+" "+str(int(number2))+" "+str(int(number3))).encode())
        s.close()

    def prep_rec_treble(self,send_msg1,send_msg2,send_msg3):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.rec_port))
        s.listen(1)
        self.conn, self.addr = s.accept()
        self.soc=s
        self.conn.send(str(str(int(send_msg1))+" "+str(int(send_msg2))+" "+str(int(send_msg3))).encode())
        data = self.conn.recv(100).decode()
        self.conn.close()
        self.soc.close()
        #self.rec_port += 1
        tmp = data.split(" ")
        self.other_parallel0 = GF256(int(tmp[0]))
        self.other_parallel1 = GF256(int(tmp[1]))
        self.other_parallel2 = GF256(int(tmp[2]))


class ComputePlayer4p_method1(Player):
    read_bits_cnt_0 = 0
    read_bits_cnt_1 = 0
    read_bits_cnt_2 = 0
    read_bits_cnt_3 = 0
    def __init__(self,ip='localhost', rec_port=5000):
        super().__init__(ip,rec_port)
        self.x = 0
        self.x3 = 0
        self.x9 = 0
        self.x11 = 0
        self.x27 = 0
        self.x81 = 0
        self.x243 = 0
        self.x254 = 0
        self.rand = 0
        self.mult_send0 = 0
        self.mult_send1 = 0
        self.mult_send2 = 0
        self.mult_send3 = 0
        self.mult_recv0 = 0
        self.mult_recv1 = 0
        self.mult_recv2 = 0
        self.mult_recv3 = 0
        self.tobemul1 = 0
        self.tobemul2 = 0
        self.tobemul3 = 0
        self.res_mul = 0
        self.mult_send0_1 = 0
        self.mult_send1_1 = 0
        self.mult_send2_1 = 0
        self.mult_send3_1 = 0
        self.mult_recv0_1 = 0
        self.mult_recv1_1 = 0
        self.mult_recv2_1 = 0
        self.mult_recv3_1 = 0
        self.tobe1 = 0
        self.tobe2 = 0
        self.tobe3 = 0
        self.res_mul1 = 0

        self.open = 0

        self.mem = 0

    def set_input(self,input):
        self.input = input

    def set_key(self,key):
        self.key = key

    def read_prepared_bits(self,no):
        with open(f"./prepared/four_party/party{no}.txt", 'r') as f:
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip().split(" ")
            self.prepared_bits = tmp

    def get_prepared_bits(self):
        if self.no == 0:
            res = GF256(self.prepared_bits[ComputePlayer4p_method1.read_bits_cnt_0])
            ComputePlayer4p_method1.read_bits_cnt_0 +=1
            return res
        if self.no == 1:
            res = GF256(self.prepared_bits[ComputePlayer4p_method1.read_bits_cnt_1])
            ComputePlayer4p_method1.read_bits_cnt_1 +=1
            return res
        if self.no == 2:
            res = GF256(self.prepared_bits[ComputePlayer4p_method1.read_bits_cnt_2])
            ComputePlayer4p_method1.read_bits_cnt_2 +=1
            return res
        if self.no == 3:
            res = GF256(self.prepared_bits[ComputePlayer4p_method1.read_bits_cnt_3])
            ComputePlayer4p_method1.read_bits_cnt_3 +=1
            return res

    def set_x(self,x):
        self.x = x

    def gen_rand(self):
        self.rand = GF256(random.randint(1,255))

    def set_mult(self,a,b):
        self.tobemul1 = a
        self.tobemul2 = b

    def set_mult2(self,a,b,c):
        self.tobemul1 = a
        self.tobemul2 = b
        self.tobemul3 = c

    def set_mult_parallel(self,a,b):
        self.tobe1 = a
        self.tobe2 = b

    def set_mult2_parallel(self,a,b,c):
        self.tobe1 = a
        self.tobe2 = b
        self.tobe3 = c

    def send_num_parallel(self,number1,number2, target_ip, target_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        rec_data = s.recv(100).decode()
        self.rec_data_parallel0 = GF256(int(rec_data.split(" ")[0]))
        self.rec_data_parallel1 = GF256(int(rec_data.split(" ")[1]))
        s.send(str(str(int(number1))+" "+str(int(number2))).encode())
        s.close()

    def prep_rec_parallel(self,send_msg1,send_msg2):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.rec_port))
        s.listen(1)
        self.conn, self.addr = s.accept()
        self.soc=s
        self.conn.send(str(str(int(send_msg1))+" "+str(int(send_msg2))).encode())
        data = self.conn.recv(100).decode()
        self.conn.close()
        self.soc.close()
        #self.rec_port += 1
        self.other_parallel0 = GF256(int(data.split(" ")[0]))
        self.other_parallel1 = GF256(int(data.split(" ")[1]))


class ComputePlayer4p_method2(Player):
    read_bits_cnt_0 = 0
    read_bits_cnt_1 = 0
    read_bits_cnt_2 = 0
    read_bits_cnt_3 = 0
    read_shares_cnt_0 = 0
    read_shares_cnt_1 = 0
    read_shares_cnt_2 = 0
    read_shares_cnt_3 = 0
    def __init__(self,ip='localhost', rec_port=5000):
        super().__init__(ip,rec_port)
        self.x = 0
        self.x2 = 0
        self.x4 = 0
        self.x8 = 0
        self.x16 = 0
        self.x32 = 0
        self.x64 = 0
        self.x128 = 0
        self.x254 = 0
        self.x11 = 0
        self.x112 = 0
        self.rand = 0
        self.mult_send0 = 0
        self.mult_send1 = 0
        self.mult_send2 = 0
        self.mult_send3 = 0
        self.mult_recv0 = 0
        self.mult_recv1 = 0
        self.mult_recv2 = 0
        self.mult_recv3 = 0
        self.tobemul1 = 0
        self.tobemul2 = 0
        self.tobemul3 = 0
        self.res_mul = 0
        self.mult_send0_1 = 0
        self.mult_send1_1 = 0
        self.mult_send2_1 = 0
        self.mult_send3_1 = 0
        self.mult_recv0_1 = 0
        self.mult_recv1_1 = 0
        self.mult_recv2_1 = 0
        self.mult_recv3_1 = 0
        self.tobe1 = 0
        self.tobe2 = 0
        self.tobe3 = 0
        self.res_mul1 = 0

        self.open = 0

        self.mem = 0

    def set_input(self,input):
        self.input = input

    def set_key(self,key):
        self.key = key

    def read_prepared_bits(self,no):
        with open(f"./prepared/four_party/party{no}.txt", 'r') as f:
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip().split(" ")
            self.prepared_bits = tmp

    def get_prepared_bits(self):
        if self.no == 0:
            res = GF256(self.prepared_bits[ComputePlayer4p_method2.read_bits_cnt_0])
            ComputePlayer4p_method2.read_bits_cnt_0 +=1
            return res
        if self.no == 1:
            res = GF256(self.prepared_bits[ComputePlayer4p_method2.read_bits_cnt_1])
            ComputePlayer4p_method2.read_bits_cnt_1 +=1
            return res
        if self.no == 2:
            res = GF256(self.prepared_bits[ComputePlayer4p_method2.read_bits_cnt_2])
            ComputePlayer4p_method2.read_bits_cnt_2 +=1
            return res
        if self.no == 3:
            res = GF256(self.prepared_bits[ComputePlayer4p_method2.read_bits_cnt_3])
            ComputePlayer4p_method2.read_bits_cnt_3 +=1
            return res

    def read_prepared_shares(self,no):
        with open(f"./prepared_random/four_party/party{no}.txt", 'r') as f:
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip().split(" ")
            self.prepared_shares = tmp

    def get_prepared_shares(self):
        if self.no == 0:
            res = GF256(self.prepared_shares[ComputePlayer4p_method2.read_shares_cnt_0])
            ComputePlayer4p_method2.read_shares_cnt_0 += 1
            return res
        if self.no == 1:
            res = GF256(self.prepared_shares[ComputePlayer4p_method2.read_shares_cnt_1])
            ComputePlayer4p_method2.read_shares_cnt_1 += 1
            return res
        if self.no == 2:
            res = GF256(self.prepared_shares[ComputePlayer4p_method2.read_shares_cnt_2])
            ComputePlayer4p_method2.read_shares_cnt_2 += 1
            return res
        if self.no == 3:
            res = GF256(self.prepared_shares[ComputePlayer4p_method2.read_shares_cnt_3])
            ComputePlayer4p_method2.read_shares_cnt_3 += 1
            return res



    def set_x(self,x):
        self.x = x

    def gen_rand(self):
        self.rand = GF256(random.randint(1,255))

    def set_mult(self,a,b):
        self.tobemul1 = a
        self.tobemul2 = b

    def set_mult2(self,a,b,c):
        self.tobemul1 = a
        self.tobemul2 = b
        self.tobemul3 = c

    def set_mult_parallel(self,a,b):
        self.tobe1 = a
        self.tobe2 = b

    def set_mult2_parallel(self,a,b,c):
        self.tobe1 = a
        self.tobe2 = b
        self.tobe3 = c

    def send_num_parallel(self,number1,number2, target_ip, target_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        rec_data = s.recv(100).decode()
        self.rec_data_parallel0 = GF256(int(rec_data.split(" ")[0]))
        self.rec_data_parallel1 = GF256(int(rec_data.split(" ")[1]))
        s.send(str(str(int(number1))+" "+str(int(number2))).encode())
        s.close()

    def prep_rec_parallel(self,send_msg1,send_msg2):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.rec_port))
        s.listen(1)
        self.conn, self.addr = s.accept()
        self.soc=s
        self.conn.send(str(str(int(send_msg1))+" "+str(int(send_msg2))).encode())
        data = self.conn.recv(100).decode()
        self.conn.close()
        self.soc.close()
        #self.rec_port += 1
        self.other_parallel0 = GF256(int(data.split(" ")[0]))
        self.other_parallel1 = GF256(int(data.split(" ")[1]))


class ComputePlayer4p_method3(Player):
    read_bits_cnt_0 = 0
    read_bits_cnt_1 = 0
    read_bits_cnt_2 = 0
    read_bits_cnt_3 = 0
    read_shares_cnt_0 = 0
    read_shares_cnt_1 = 0
    read_shares_cnt_2 = 0
    read_shares_cnt_3 = 0
    def __init__(self,ip='localhost', rec_port=5000):
        super().__init__(ip,rec_port)
        self.x = 0
        self.x3 = 0
        self.x4 = 0
        self.x8 = 0
        self.x9 = 0
        self.x11 = 0
        self.x19 = 0
        self.x27 = 0
        self.x29 = 0
        self.x61 = 0
        self.x81 = 0
        self.x243 = 0
        self.x127 = 0
        self.x191 = 0
        self.x223 = 0
        self.x239 = 0
        self.x247 = 0
        self.x251 = 0
        self.x253 = 0
        self.x254 = 0
        self.rand = 0
        self.mult_send0 = [0,0,0,0,0,0,0,0]
        self.mult_send1 = [0,0,0,0,0,0,0,0]
        self.mult_send2 = [0,0,0,0,0,0,0,0]
        self.mult_send3 = [0,0,0,0,0,0,0,0]
        self.mult_recv0 = [0,0,0,0,0,0,0,0]
        self.mult_recv1 = [0,0,0,0,0,0,0,0]
        self.mult_recv2 = [0,0,0,0,0,0,0,0]
        self.mult_recv3 = [0,0,0,0,0,0,0,0]
        self.tobemul1 = [0,0,0,0,0,0,0,0]
        self.tobemul2 = [0,0,0,0,0,0,0,0]
        self.tobemul3 = [0,0,0,0,0,0,0,0]
        self.res_mul = [0,0,0,0,0,0,0,0]

        self.open = 0

        self.mem = 0

    def set_input(self,input):
        self.input = input

    def set_key(self,key):
        self.key = key

    def read_prepared_bits(self,no):
        with open(f"./prepared/four_party/party{no}.txt", 'r') as f:
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip().split(" ")
            self.prepared_bits = tmp

    def get_prepared_bits(self):
        if self.no == 0:
            res = GF256(self.prepared_bits[ComputePlayer4p_method3.read_bits_cnt_0])
            ComputePlayer4p_method3.read_bits_cnt_0 +=1
            return res
        if self.no == 1:
            res = GF256(self.prepared_bits[ComputePlayer4p_method3.read_bits_cnt_1])
            ComputePlayer4p_method3.read_bits_cnt_1 +=1
            return res
        if self.no == 2:
            res = GF256(self.prepared_bits[ComputePlayer4p_method3.read_bits_cnt_2])
            ComputePlayer4p_method3.read_bits_cnt_2 +=1
            return res
        if self.no == 3:
            res = GF256(self.prepared_bits[ComputePlayer4p_method3.read_bits_cnt_3])
            ComputePlayer4p_method3.read_bits_cnt_3 +=1
            return res

    def read_prepared_shares(self,no):
        with open(f"./prepared_random/four_party/party{no}.txt", 'r') as f:
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip().split(" ")
            self.prepared_shares = tmp

    def get_prepared_shares(self):
        if self.no == 0:
            res = GF256(self.prepared_shares[ComputePlayer4p_method3.read_shares_cnt_0])
            ComputePlayer4p_method3.read_shares_cnt_0 += 1
            return res
        if self.no == 1:
            res = GF256(self.prepared_shares[ComputePlayer4p_method3.read_shares_cnt_1])
            ComputePlayer4p_method3.read_shares_cnt_1 += 1
            return res
        if self.no == 2:
            res = GF256(self.prepared_shares[ComputePlayer4p_method3.read_shares_cnt_2])
            ComputePlayer4p_method3.read_shares_cnt_2 += 1
            return res
        if self.no == 3:
            res = GF256(self.prepared_shares[ComputePlayer4p_method3.read_shares_cnt_3])
            ComputePlayer4p_method3.read_shares_cnt_3 += 1
            return res



    def set_x(self,x):
        self.x = x

    def gen_rand(self):
        self.rand = GF256(random.randint(1,255))

    def set_mult(self,a,b):
        self.tobemul1[0] = a
        self.tobemul2[0] = b

    def set_mult2(self,a,b,c):
        self.tobemul1[0] = a
        self.tobemul2[0] = b
        self.tobemul3[0] = c

    def set_mult_parallel(self,a,b):
        for i in range(len(a)):
            self.tobemul1[i] = a[i]
            self.tobemul2[i] = b[i]

    def set_mult2_parallel(self,a,b,c):
        for i in range(len(a)):
            self.tobemul1[i] = a[i]
            self.tobemul2[i] = b[i]
            self.tobemul3[i] = c[i]

    def send_num_parallel(self, numbers, target_ip, target_port): #numbers should be a list and its elements' type are GF256
        send_msg = list_to_string(numbers)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        rec_data = s.recv(100).decode()
        self.rec_data = string_to_list(rec_data)
        s.send(send_msg.encode())
        s.close()

    def prep_rec_parallel(self,send_msg):              #send_msg should be a list and its elements' type are GF256
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.rec_port))
        s.listen(1)
        self.conn, self.addr = s.accept()
        self.soc=s
        s_msg = list_to_string(send_msg)
        self.conn.send(s_msg.encode())
        data = self.conn.recv(100).decode()
        self.conn.close()
        self.soc.close()
        #self.rec_port += 1
        self.other = string_to_list(data)



class ComputePlayer4p_method4(Player):
    read_bits_cnt_0 = 0
    read_bits_cnt_1 = 0
    read_bits_cnt_2 = 0
    read_bits_cnt_3 = 0
    read_shares_cnt_0 = 0
    read_shares_cnt_1 = 0
    read_shares_cnt_2 = 0
    read_shares_cnt_3 = 0
    def __init__(self,ip='localhost', rec_port=5000):
        super().__init__(ip,rec_port)
        self.x = 0
        self.x2 = 0
        self.x4 = 0
        self.x8 = 0
        self.x16 = 0
        self.x32 = 0
        self.x64 = 0
        self.x128 = 0
        self.x254 = 0
        self.x7 = 0
        self.x11 = 0
        self.x28 = 0
        self.x56 = 0
        self.x88 = 0
        self.x224 = 0
        self.x127 = 0
        self.x191 = 0
        self.x223 = 0
        self.x239 = 0
        self.x247 = 0
        self.x251 = 0
        self.x253 = 0
        self.x254 = 0
        self.rand = 0
        self.mult_send0 = [0,0,0,0,0,0,0,0]
        self.mult_send1 = [0,0,0,0,0,0,0,0]
        self.mult_send2 = [0,0,0,0,0,0,0,0]
        self.mult_send3 = [0,0,0,0,0,0,0,0]
        self.mult_recv0 = [0,0,0,0,0,0,0,0]
        self.mult_recv1 = [0,0,0,0,0,0,0,0]
        self.mult_recv2 = [0,0,0,0,0,0,0,0]
        self.mult_recv3 = [0,0,0,0,0,0,0,0]
        self.tobemul1 = [0,0,0,0,0,0,0,0]
        self.tobemul2 = [0,0,0,0,0,0,0,0]
        self.tobemul3 = [0,0,0,0,0,0,0,0]
        self.res_mul = [0,0,0,0,0,0,0,0]

        self.open = 0

        self.mem = 0

    def set_input(self,input):
        self.input = input

    def set_key(self,key):
        self.key = key

    def read_prepared_bits(self,no):
        with open(f"./prepared/four_party/party{no}.txt", 'r') as f:
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip().split(" ")
            self.prepared_bits = tmp

    def get_prepared_bits(self):
        if self.no == 0:
            res = GF256(self.prepared_bits[ComputePlayer4p_method4.read_bits_cnt_0])
            ComputePlayer4p_method4.read_bits_cnt_0 +=1
            return res
        if self.no == 1:
            res = GF256(self.prepared_bits[ComputePlayer4p_method4.read_bits_cnt_1])
            ComputePlayer4p_method4.read_bits_cnt_1 +=1
            return res
        if self.no == 2:
            res = GF256(self.prepared_bits[ComputePlayer4p_method4.read_bits_cnt_2])
            ComputePlayer4p_method4.read_bits_cnt_2 +=1
            return res
        if self.no == 3:
            res = GF256(self.prepared_bits[ComputePlayer4p_method4.read_bits_cnt_3])
            ComputePlayer4p_method4.read_bits_cnt_3 +=1
            return res

    def read_prepared_shares(self,no):
        with open(f"./prepared_random/four_party/party{no}.txt", 'r') as f:
            tmp = f.readlines()
            for i in range(len(tmp)):
                tmp[i] = tmp[i].strip().split(" ")
            self.prepared_shares = tmp

    def get_prepared_shares(self):
        if self.no == 0:
            res = GF256(self.prepared_shares[ComputePlayer4p_method4.read_shares_cnt_0])
            ComputePlayer4p_method4.read_shares_cnt_0 += 1
            return res
        if self.no == 1:
            res = GF256(self.prepared_shares[ComputePlayer4p_method4.read_shares_cnt_1])
            ComputePlayer4p_method4.read_shares_cnt_1 += 1
            return res
        if self.no == 2:
            res = GF256(self.prepared_shares[ComputePlayer4p_method4.read_shares_cnt_2])
            ComputePlayer4p_method4.read_shares_cnt_2 += 1
            return res
        if self.no == 3:
            res = GF256(self.prepared_shares[ComputePlayer4p_method4.read_shares_cnt_3])
            ComputePlayer4p_method4.read_shares_cnt_3 += 1
            return res



    def set_x(self,x):
        self.x = x

    def gen_rand(self):
        self.rand = GF256(random.randint(1,255))

    def set_mult(self,a,b):
        self.tobemul1[0] = a
        self.tobemul2[0] = b

    def set_mult2(self,a,b,c):
        self.tobemul1[0] = a
        self.tobemul2[0] = b
        self.tobemul3[0] = c

    def set_mult_parallel(self,a,b):
        for i in range(len(a)):
            self.tobemul1[i] = a[i]
            self.tobemul2[i] = b[i]

    def set_mult2_parallel(self,a,b,c):
        for i in range(len(a)):
            self.tobemul1[i] = a[i]
            self.tobemul2[i] = b[i]
            self.tobemul3[i] = c[i]

    def send_num_parallel(self, numbers, target_ip, target_port): #numbers should be a list and its elements' type are GF256
        send_msg = list_to_string(numbers)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        rec_data = s.recv(100).decode()
        self.rec_data = string_to_list(rec_data)
        s.send(send_msg.encode())
        s.close()

    def prep_rec_parallel(self,send_msg):              #send_msg should be a list and its elements' type are GF256
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", self.rec_port))
        s.listen(1)
        self.conn, self.addr = s.accept()
        self.soc=s
        s_msg = list_to_string(send_msg)
        self.conn.send(s_msg.encode())
        data = self.conn.recv(100).decode()
        self.conn.close()
        self.soc.close()
        #self.rec_port += 1
        self.other = string_to_list(data)




def multi_broadcast_3p(players):
    global broadcast_time
    #t0 = datetime.datetime.now()
    t0 = time.time()
    t1 = Thread(target=players[0].prep_rec, args=(players[0].mult_send1, ))
    t2 = Thread(target=players[1].send_num, args=(players[1].mult_send0, players[0].ip, players[0].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[0].mult_recv1 = players[0].other
    players[1].mult_recv0 = players[1].rec_data

    t1 = Thread(target=players[0].prep_rec, args=(players[0].mult_send2, ))
    t2 = Thread(target=players[2].send_num, args=(players[2].mult_send0, players[0].ip, players[0].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[0].mult_recv2 = players[0].other
    players[2].mult_recv0 = players[2].rec_data

    t1 = Thread(target=players[1].prep_rec, args=(players[1].mult_send2, ))
    t2 = Thread(target=players[2].send_num, args=(players[2].mult_send1, players[1].ip, players[1].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[1].mult_recv2 = players[1].other
    players[2].mult_recv1 = players[2].rec_data

    #t1 = datetime.datetime.now()
    t1 = time.time()

    for i in range(3):
        setattr(players[i], f"mult_recv{i}",getattr(players[i], f"mult_send{i}"))
    broadcast_time += t1-t0
    #print(broadcast_time)


def multi_3p(players,cofflambda,alpha):
    for i in range(len(players)):
        tmp = players[i].tobemul1*players[i].tobemul2
        players[i].gen_rand()
        players[i].mult_send0 = cofflambda[i]*tmp+players[i].rand*alpha[0]
        players[i].mult_send1 = cofflambda[i]*tmp+players[i].rand*alpha[1]
        players[i].mult_send2 = cofflambda[i]*tmp+players[i].rand*alpha[2]

    multi_broadcast_3p(players)
    for i in range(len(players)):
        players[i].res_mul = players[i].mult_recv0+players[i].mult_recv1+players[i].mult_recv2


def multi_broadcast_3p_parallel(players):
    global broadcast_time
    #t0 = datetime.datetime.now()
    t0 = time.time()
    t1 = Thread(target=players[0].prep_rec_parallel, args=(players[0].mult_send1, players[0].mult_send1_1,))
    t2 = Thread(target=players[1].send_num_parallel,
                args=(players[1].mult_send0, players[1].mult_send0_1, players[0].ip, players[0].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[0].mult_recv1 = players[0].other_parallel0
    players[0].mult_recv1_1 = players[0].other_parallel1
    players[1].mult_recv0 = players[1].rec_data_parallel0
    players[1].mult_recv0_1 = players[1].rec_data_parallel1

    t1 = Thread(target=players[0].prep_rec_parallel, args=(players[0].mult_send2, players[0].mult_send2_1,))
    t2 = Thread(target=players[2].send_num_parallel,
                args=(players[2].mult_send0, players[2].mult_send0_1, players[0].ip, players[0].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[0].mult_recv2 = players[0].other_parallel0
    players[0].mult_recv2_1 = players[0].other_parallel1
    players[2].mult_recv0 = players[2].rec_data_parallel0
    players[2].mult_recv0_1 = players[2].rec_data_parallel1

    t1 = Thread(target=players[1].prep_rec_parallel, args=(players[1].mult_send2, players[1].mult_send2_1,))
    t2 = Thread(target=players[2].send_num_parallel,
                args=(players[2].mult_send1, players[2].mult_send1_1, players[1].ip, players[1].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[1].mult_recv2 = players[1].other_parallel0
    players[1].mult_recv2_1 = players[1].other_parallel1
    players[2].mult_recv1 = players[2].rec_data_parallel0
    players[2].mult_recv1_1 = players[2].rec_data_parallel1

    #t1 = datetime.datetime.now()
    t1 = time.time()
    broadcast_time+=t1-t0

    for i in range(3):
        setattr(players[i], f"mult_recv{i}", getattr(players[i], f"mult_send{i}"))
        setattr(players[i], f"mult_recv{i}_1", getattr(players[i], f"mult_send{i}_1"))


def multi_3p_parallel(players,cofflambda,alpha):
    for i in range(len(players)):
        tmp1 = players[i].tobemul1*players[i].tobemul2
        tmp2 = players[i].tobe1*players[i].tobe2
        players[i].gen_rand()
        players[i].mult_send0 = cofflambda[i]*tmp1+players[i].rand*alpha[0]
        players[i].mult_send1 = cofflambda[i]*tmp1+players[i].rand*alpha[1]
        players[i].mult_send2 = cofflambda[i]*tmp1+players[i].rand*alpha[2]
        players[i].gen_rand()
        players[i].mult_send0_1 = cofflambda[i]*tmp2+players[i].rand*alpha[0]
        players[i].mult_send1_1 = cofflambda[i]*tmp2+players[i].rand*alpha[1]
        players[i].mult_send2_1 = cofflambda[i]*tmp2+players[i].rand*alpha[2]
    multi_broadcast_3p_parallel(players)
    for i in range(len(players)):
        players[i].res_mul = players[i].mult_recv0 + players[i].mult_recv1 + players[i].mult_recv2
        players[i].res_mul1 = players[i].mult_recv0_1 + players[i].mult_recv1_1 + players[i].mult_recv2_1


def multi_broadcast_3p_treble(players):
    global broadcast_time
    #t0 = datetime.datetime.now()
    t0 = time.time()
    t1 = Thread(target=players[0].prep_rec_treble, args=(players[0].mult_send1, players[0].mult_send1_1, players[0].mult_send1_2 ))
    t2 = Thread(target=players[1].send_num_treble,
                args=(players[1].mult_send0, players[1].mult_send0_1, players[1].mult_send0_2, players[0].ip, players[0].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[0].mult_recv1 = players[0].other_parallel0
    players[0].mult_recv1_1 = players[0].other_parallel1
    players[0].mult_recv1_2 = players[0].other_parallel2
    players[1].mult_recv0 = players[1].rec_data_parallel0
    players[1].mult_recv0_1 = players[1].rec_data_parallel1
    players[1].mult_recv0_2 = players[1].rec_data_parallel2



    t1 = Thread(target=players[0].prep_rec_treble, args=(players[0].mult_send2, players[0].mult_send2_1, players[0].mult_send2_2 ))
    t2 = Thread(target=players[2].send_num_treble,
                args=(players[2].mult_send0, players[2].mult_send0_1, players[2].mult_send0_2, players[0].ip, players[0].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[0].mult_recv2 = players[0].other_parallel0
    players[0].mult_recv2_1 = players[0].other_parallel1
    players[0].mult_recv2_2 = players[0].other_parallel2
    players[2].mult_recv0 = players[2].rec_data_parallel0
    players[2].mult_recv0_1 = players[2].rec_data_parallel1
    players[2].mult_recv0_2 = players[2].rec_data_parallel2

    t1 = Thread(target=players[1].prep_rec_treble, args=(players[1].mult_send2, players[1].mult_send2_1, players[1].mult_send2_2 ))
    t2 = Thread(target=players[2].send_num_treble,
                args=(players[2].mult_send1, players[2].mult_send1_1, players[2].mult_send1_2, players[1].ip, players[1].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[1].mult_recv2 = players[1].other_parallel0
    players[1].mult_recv2_1 = players[1].other_parallel1
    players[1].mult_recv2_2 = players[1].other_parallel2
    players[2].mult_recv1 = players[2].rec_data_parallel0
    players[2].mult_recv1_1 = players[2].rec_data_parallel1
    players[2].mult_recv1_2 = players[2].rec_data_parallel2

    #t1 = datetime.datetime.now()
    t1 = time.time()

    for i in range(3):
        setattr(players[i], f"mult_recv{i}", getattr(players[i], f"mult_send{i}"))
        setattr(players[i], f"mult_recv{i}_1", getattr(players[i], f"mult_send{i}_1"))
        setattr(players[i], f"mult_recv{i}_2", getattr(players[i], f"mult_send{i}_2"))
    broadcast_time += t1-t0


def multi_3p_treble(players,cofflambda,alpha):
    for i in range(len(players)):
        tmp1 = players[i].tobemul1*players[i].tobemul2
        tmp2 = players[i].tobe1*players[i].tobe2
        tmp3 = players[i].tob1*players[i].tob2
        players[i].gen_rand()
        players[i].mult_send0 = cofflambda[i]*tmp1+players[i].rand*alpha[0]
        players[i].mult_send1 = cofflambda[i]*tmp1+players[i].rand*alpha[1]
        players[i].mult_send2 = cofflambda[i]*tmp1+players[i].rand*alpha[2]
        players[i].gen_rand()
        players[i].mult_send0_1 = cofflambda[i]*tmp2+players[i].rand*alpha[0]
        players[i].mult_send1_1 = cofflambda[i]*tmp2+players[i].rand*alpha[1]
        players[i].mult_send2_1 = cofflambda[i]*tmp2+players[i].rand*alpha[2]
        players[i].gen_rand()
        players[i].mult_send0_2 = cofflambda[i]*tmp3+players[i].rand*alpha[0]
        players[i].mult_send1_2 = cofflambda[i]*tmp3+players[i].rand*alpha[1]
        players[i].mult_send2_2 = cofflambda[i]*tmp3+players[i].rand*alpha[2]
    multi_broadcast_3p_treble(players)
    for i in range(len(players)):
        players[i].res_mul = players[i].mult_recv0 + players[i].mult_recv1 + players[i].mult_recv2
        players[i].res_mul1 = players[i].mult_recv0_1 + players[i].mult_recv1_1 + players[i].mult_recv2_1
        players[i].res_mul2 = players[i].mult_recv0_2 + players[i].mult_recv1_2 + players[i].mult_recv2_2


def multi2_broadcast_4p(players):
    global broadcast_time
    #t0 = datetime.datetime.now()
    t0 = time.time()
    t1 = Thread(target=players[0].prep_rec, args=(players[0].mult_send1, ))
    t2 = Thread(target=players[1].send_num, args=(players[1].mult_send0, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[2].prep_rec, args=(players[2].mult_send3, ))
    t4 = Thread(target=players[3].send_num, args=(players[3].mult_send2, players[2].ip, players[2].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv1 = players[0].other
    players[1].mult_recv0 = players[1].rec_data
    players[2].mult_recv3 = players[2].other
    players[3].mult_recv2 = players[3].rec_data

    t1 = Thread(target=players[0].prep_rec, args=(players[0].mult_send2, ))
    t2 = Thread(target=players[2].send_num, args=(players[2].mult_send0, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[1].prep_rec, args=(players[1].mult_send3, ))
    t4 = Thread(target=players[3].send_num, args=(players[3].mult_send1, players[1].ip, players[1].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv2 = players[0].other
    players[2].mult_recv0 = players[2].rec_data
    players[1].mult_recv3 = players[1].other
    players[3].mult_recv1 = players[3].rec_data

    t1 = Thread(target=players[0].prep_rec, args=(players[0].mult_send3, ))
    t2 = Thread(target=players[3].send_num, args=(players[3].mult_send0, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[1].prep_rec, args=(players[1].mult_send2, ))
    t4 = Thread(target=players[2].send_num, args=(players[2].mult_send1, players[1].ip, players[1].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv3 = players[0].other
    players[3].mult_recv0 = players[3].rec_data
    players[1].mult_recv2 = players[1].other
    players[2].mult_recv1 = players[2].rec_data

    #t1 = datetime.datetime.now()
    t1 = time.time()

    for i in range(4):
        setattr(players[i], f"mult_recv{i}",getattr(players[i], f"mult_send{i}"))
    broadcast_time += t1-t0
    #print(broadcast_time)


def multi_broadcast_4p(players):
    global broadcast_time
    #t0 = datetime.datetime.now()
    t0 = time.time()
    t1 = Thread(target=players[0].prep_rec, args=(players[0].mult_send1, ))
    t2 = Thread(target=players[1].send_num, args=(players[1].mult_send0, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[3].oneway_rec, args=())
    t4 = Thread(target=players[2].oneway_send, args=(players[2].mult_send3, players[3].ip, players[3].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv1 = players[0].other
    players[1].mult_recv0 = players[1].rec_data
    players[3].mult_recv2 = players[3].oneway_other

    t1 = Thread(target=players[0].prep_rec, args=(players[0].mult_send2, ))
    t2 = Thread(target=players[2].send_num, args=(players[2].mult_send0, players[0].ip, players[0].rec_port))
    t4 = Thread(target=players[1].oneway_send, args=(players[1].mult_send3, players[3].ip, players[3].rec_port))
    t3 = Thread(target=players[3].oneway_rec, args=())
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv2 = players[0].other
    players[2].mult_recv0 = players[2].rec_data
    players[3].mult_recv1 = players[3].oneway_other

    t1 = Thread(target=players[1].prep_rec, args=(players[1].mult_send2, ))
    t2 = Thread(target=players[2].send_num, args=(players[2].mult_send1, players[1].ip, players[1].rec_port))
    t4 = Thread(target=players[0].oneway_send, args=(players[0].mult_send3, players[3].ip, players[3].rec_port))
    t3 = Thread(target=players[3].oneway_rec, args=())
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[1].mult_recv2 = players[1].other
    players[2].mult_recv1 = players[2].rec_data
    players[3].mult_recv0 = players[3].oneway_other

    #t1 = datetime.datetime.now()
    t1 = time.time()

    for i in range(3):
        setattr(players[i], f"mult_recv{i}", getattr(players[i], f"mult_send{i}"))
    broadcast_time += t1-t0
    #print(broadcast_time)


def multi2_4p(players,cofflambda,alpha):
    for i in range(len(players)):
        tmp = players[i].tobemul1*players[i].tobemul2*players[i].tobemul3
        players[i].gen_rand()
        players[i].mult_send0 = cofflambda[i]*tmp+players[i].rand*alpha[0]
        players[i].mult_send1 = cofflambda[i]*tmp+players[i].rand*alpha[1]
        players[i].mult_send2 = cofflambda[i]*tmp+players[i].rand*alpha[2]
        players[i].mult_send3 = cofflambda[i]*tmp+players[i].rand*alpha[3]

    multi2_broadcast_4p(players)
    for i in range(len(players)):
        players[i].res_mul = players[i].mult_recv0+players[i].mult_recv1+players[i].mult_recv2+players[i].mult_recv3


def multi_4p(players,cofflambda,alpha):
    #这里的lambda和multi2_4p的lambda不一样，前者是3方对应的lambda,后者是4方对应的lambda
    for i in range(3):
        tmp = players[i].tobemul1*players[i].tobemul2
        players[i].gen_rand()
        players[i].mult_send0 = cofflambda[i]*tmp+players[i].rand*alpha[0]
        players[i].mult_send1 = cofflambda[i]*tmp+players[i].rand*alpha[1]
        players[i].mult_send2 = cofflambda[i]*tmp+players[i].rand*alpha[2]
        players[i].mult_send3 = cofflambda[i]*tmp+players[i].rand*alpha[3]

    multi_broadcast_4p(players)
    for i in range(4):
        players[i].res_mul = players[i].mult_recv0+players[i].mult_recv1+players[i].mult_recv2


def multi2_broadcast_4p_parallel(players):
    global broadcast_time
    #t0 = datetime.datetime.now()
    t0 = time.time()
    t1 = Thread(target=players[0].prep_rec_parallel, args=(players[0].mult_send1, players[0].mult_send1_1,))
    t2 = Thread(target=players[1].send_num_parallel,
                args=(players[1].mult_send0, players[1].mult_send0_1, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[2].prep_rec_parallel, args=(players[2].mult_send3, players[2].mult_send3_1,))
    t4 = Thread(target=players[3].send_num_parallel,
                args=(players[3].mult_send2, players[3].mult_send2_1, players[2].ip, players[2].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv1 = players[0].other_parallel0
    players[0].mult_recv1_1 = players[0].other_parallel1
    players[1].mult_recv0 = players[1].rec_data_parallel0
    players[1].mult_recv0_1 = players[1].rec_data_parallel1
    players[2].mult_recv3 = players[2].other_parallel0
    players[2].mult_recv3_1 = players[2].other_parallel1
    players[3].mult_recv2 = players[3].rec_data_parallel0
    players[3].mult_recv2_1 = players[3].rec_data_parallel1

    t1 = Thread(target=players[0].prep_rec_parallel, args=(players[0].mult_send2, players[0].mult_send2_1,))
    t2 = Thread(target=players[2].send_num_parallel,
                args=(players[2].mult_send0, players[2].mult_send0_1, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[1].prep_rec_parallel, args=(players[1].mult_send3, players[1].mult_send3_1,))
    t4 = Thread(target=players[3].send_num_parallel,
                args=(players[3].mult_send1, players[3].mult_send1_1, players[1].ip, players[1].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv2 = players[0].other_parallel0
    players[0].mult_recv2_1 = players[0].other_parallel1
    players[2].mult_recv0 = players[2].rec_data_parallel0
    players[2].mult_recv0_1 = players[2].rec_data_parallel1
    players[1].mult_recv3 = players[1].other_parallel0
    players[1].mult_recv3_1 = players[1].other_parallel1
    players[3].mult_recv1 = players[3].rec_data_parallel0
    players[3].mult_recv1_1 = players[3].rec_data_parallel1

    t1 = Thread(target=players[1].prep_rec_parallel, args=(players[1].mult_send2, players[1].mult_send2_1,))
    t2 = Thread(target=players[2].send_num_parallel,
                args=(players[2].mult_send1, players[2].mult_send1_1, players[1].ip, players[1].rec_port))
    t3 = Thread(target=players[0].prep_rec_parallel, args=(players[0].mult_send3, players[0].mult_send3_1,))
    t4 = Thread(target=players[3].send_num_parallel,
                args=(players[3].mult_send0, players[3].mult_send0_1, players[0].ip, players[0].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[1].mult_recv2 = players[1].other_parallel0
    players[1].mult_recv2_1 = players[1].other_parallel1
    players[2].mult_recv1 = players[2].rec_data_parallel0
    players[2].mult_recv1_1 = players[2].rec_data_parallel1
    players[0].mult_recv3 = players[0].other_parallel0
    players[0].mult_recv3_1 = players[0].other_parallel1
    players[3].mult_recv0 = players[3].rec_data_parallel0
    players[3].mult_recv0_1 = players[3].rec_data_parallel1

    #t1 = datetime.datetime.now()
    t1 = time.time()
    broadcast_time+=t1-t0

    for i in range(4):
        setattr(players[i], f"mult_recv{i}", getattr(players[i], f"mult_send{i}"))
        setattr(players[i], f"mult_recv{i}_1", getattr(players[i], f"mult_send{i}_1"))


def multi2_4p_parallel(players,cofflambda,alpha):
    for i in range(len(players)):
        tmp1 = players[i].tobemul1*players[i].tobemul2*players[i].tobemul3
        tmp2 = players[i].tobe1*players[i].tobe2*players[i].tobe3
        players[i].gen_rand()
        players[i].mult_send0 = cofflambda[i] * tmp1 + players[i].rand * alpha[0]
        players[i].mult_send1 = cofflambda[i] * tmp1 + players[i].rand * alpha[1]
        players[i].mult_send2 = cofflambda[i] * tmp1 + players[i].rand * alpha[2]
        players[i].mult_send3 = cofflambda[i] * tmp1 + players[i].rand * alpha[3]
        players[i].gen_rand()
        players[i].mult_send0_1 = cofflambda[i] * tmp2 + players[i].rand * alpha[0]
        players[i].mult_send1_1 = cofflambda[i] * tmp2 + players[i].rand * alpha[1]
        players[i].mult_send2_1 = cofflambda[i] * tmp2 + players[i].rand * alpha[2]
        players[i].mult_send3_1 = cofflambda[i] * tmp2 + players[i].rand * alpha[3]
    multi2_broadcast_4p_parallel(players)
    for i in range(len(players)):
        players[i].res_mul = players[i].mult_recv0 + players[i].mult_recv1 + players[i].mult_recv2 + players[i].mult_recv3
        players[i].res_mul1 = players[i].mult_recv0_1 + players[i].mult_recv1_1 + players[i].mult_recv2_1 + players[i].mult_recv3_1


def multi2_broadcast_4p_parallel_multi(players):
    global broadcast_time
    #t0 = datetime.datetime.now()
    t0 = time.time()
    t1 = Thread(target=players[0].prep_rec_parallel, args=(players[0].mult_send1,))
    t2 = Thread(target=players[1].send_num_parallel, args=(players[1].mult_send0, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[2].prep_rec_parallel, args=(players[2].mult_send3,))
    t4 = Thread(target=players[3].send_num_parallel, args=(players[3].mult_send2, players[2].ip, players[2].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv1 = players[0].other
    players[1].mult_recv0 = players[1].rec_data
    players[2].mult_recv3 = players[2].other
    players[3].mult_recv2 = players[3].rec_data


    t1 = Thread(target=players[0].prep_rec_parallel, args=(players[0].mult_send2,))
    t2 = Thread(target=players[2].send_num_parallel, args=(players[2].mult_send0, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[1].prep_rec_parallel, args=(players[1].mult_send3,))
    t4 = Thread(target=players[3].send_num_parallel, args=(players[3].mult_send1, players[1].ip, players[1].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv2 = players[0].other
    players[2].mult_recv0 = players[2].rec_data
    players[1].mult_recv3 = players[1].other
    players[3].mult_recv1 = players[3].rec_data


    t1 = Thread(target=players[0].prep_rec_parallel, args=(players[0].mult_send3,))
    t2 = Thread(target=players[3].send_num_parallel, args=(players[3].mult_send0, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[1].prep_rec_parallel, args=(players[1].mult_send2,))
    t4 = Thread(target=players[2].send_num_parallel, args=(players[2].mult_send1, players[1].ip, players[1].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv3 = players[0].other
    players[3].mult_recv0 = players[3].rec_data
    players[1].mult_recv2 = players[1].other
    players[2].mult_recv1 = players[2].rec_data


    #t1 = datetime.datetime.now()
    t1 = time.time()
    broadcast_time+=t1-t0

    for i in range(4):
        setattr(players[i], f"mult_recv{i}", getattr(players[i], f"mult_send{i}"))


def multi_broadcast_4p_parallel_multi(players):
    global broadcast_time
    t0 = time.time()
    t1 = Thread(target=players[0].prep_rec_parallel, args=(players[0].mult_send1,))
    t2 = Thread(target=players[1].send_num_parallel, args=(players[1].mult_send0, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[2].prep_rec_parallel, args=(players[2].mult_send3,))
    t4 = Thread(target=players[3].send_num_parallel, args=(players[3].mult_send2, players[2].ip, players[2].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv1 = players[0].other
    players[1].mult_recv0 = players[1].rec_data
    players[3].mult_recv2 = players[3].rec_data


    t1 = Thread(target=players[0].prep_rec_parallel, args=(players[0].mult_send2,))
    t2 = Thread(target=players[2].send_num_parallel, args=(players[2].mult_send0, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[1].prep_rec_parallel, args=(players[1].mult_send3,))
    t4 = Thread(target=players[3].send_num_parallel, args=(players[3].mult_send1, players[1].ip, players[1].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[0].mult_recv2 = players[0].other
    players[2].mult_recv0 = players[2].rec_data
    players[3].mult_recv1 = players[3].rec_data


    t1 = Thread(target=players[0].prep_rec_parallel, args=(players[0].mult_send3,))
    t2 = Thread(target=players[3].send_num_parallel, args=(players[3].mult_send0, players[0].ip, players[0].rec_port))
    t3 = Thread(target=players[1].prep_rec_parallel, args=(players[1].mult_send2,))
    t4 = Thread(target=players[2].send_num_parallel, args=(players[2].mult_send1, players[1].ip, players[1].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[3].mult_recv0 = players[3].rec_data
    players[1].mult_recv2 = players[1].other
    players[2].mult_recv1 = players[2].rec_data


    t1 = time.time()
    broadcast_time+=t1-t0

    for i in range(3):
        setattr(players[i], f"mult_recv{i}", getattr(players[i], f"mult_send{i}"))



def multi2_4p_parallel_multi(players,cofflambda,alpha,pnum):
    tmp = [0 for i in range(pnum)]
    for i in range(len(players)):
        for j in range(pnum):
            tmp[j] = players[i].tobemul1[j]*players[i].tobemul2[j]*players[i].tobemul3[j]
        for j in range(pnum):
            players[i].gen_rand()
            players[i].mult_send0[j] = cofflambda[i] * tmp[j] + players[i].rand * alpha[0]
            players[i].mult_send1[j] = cofflambda[i] * tmp[j] + players[i].rand * alpha[1]
            players[i].mult_send2[j] = cofflambda[i] * tmp[j] + players[i].rand * alpha[2]
            players[i].mult_send3[j] = cofflambda[i] * tmp[j] + players[i].rand * alpha[3]
    multi2_broadcast_4p_parallel_multi(players)
    for i in range(len(players)):
        for j in range(pnum):
            players[i].res_mul[j] = players[i].mult_recv0[j]+players[i].mult_recv1[j]+players[i].mult_recv2[j]+players[i].mult_recv3[j]


def multi_4p_parallel_multi(players,cofflambda,cofflambda3,alpha,onum,dnum):
    #can deal with a series of multiplication(both once-multi and double-mutli) in parallel
    tmp = [0 for i in range(dnum+onum)]
    for i in range(len(players)):
        for j in range(dnum):
            tmp[j] = players[i].tobemul1[j]*players[i].tobemul2[j]*players[i].tobemul3[j]
        for j in range(dnum):
            players[i].gen_rand()
            players[i].mult_send0[j] = cofflambda[i] * tmp[j] + players[i].rand * alpha[0]
            players[i].mult_send1[j] = cofflambda[i] * tmp[j] + players[i].rand * alpha[1]
            players[i].mult_send2[j] = cofflambda[i] * tmp[j] + players[i].rand * alpha[2]
            players[i].mult_send3[j] = cofflambda[i] * tmp[j] + players[i].rand * alpha[3]
    multi2_broadcast_4p_parallel_multi(players)
    for i in range(len(players)):
        for j in range(dnum):
            players[i].res_mul[j] = players[i].mult_recv0[j]+players[i].mult_recv1[j]+players[i].mult_recv2[j]+players[i].mult_recv3[j]

    for i in range(3):
        for j in range(dnum,dnum+onum):
            tmp[j] = players[i].tobemul1[j]*players[i].tobemul2[j]
        for j in range(dnum,dnum+onum):
            players[i].gen_rand()
            players[i].mult_send0[j] = cofflambda3[i] * tmp[j] + players[i].rand * alpha[0]
            players[i].mult_send1[j] = cofflambda3[i] * tmp[j] + players[i].rand * alpha[1]
            players[i].mult_send2[j] = cofflambda3[i] * tmp[j] + players[i].rand * alpha[2]
            players[i].mult_send3[j] = cofflambda3[i] * tmp[j] + players[i].rand * alpha[3]
    multi_broadcast_4p_parallel_multi(players)
    for i in range(len(players)):
        for j in range(dnum,dnum+onum):
            players[i].res_mul[j] = players[i].mult_recv0[j]+players[i].mult_recv1[j]+players[i].mult_recv2[j]



def x_inverse(players,cofflambda,alpha):
    for i in range(len(players)):
        players[i].set_mult(players[i].x,players[i].x)
    multi_3p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x2 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult(players[i].x2,players[i].x2)
    multi_3p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x4 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult(players[i].x4,players[i].x4)
    multi_3p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x8 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult(players[i].x,players[i].x8)
    multi_3p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x9 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult(players[i].x9,players[i].x9)
    multi_3p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x18 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult(players[i].x18,players[i].x18)
        players[i].set_mult_parallel(players[i].x18,players[i].x)
    multi_3p_parallel(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x36 = players[i].res_mul
        players[i].x19 = players[i].res_mul1

    for i in range(len(players)):
        players[i].set_mult(players[i].x36,players[i].x36)
        players[i].set_mult_parallel(players[i].x36,players[i].x19)
    multi_3p_parallel(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x72 = players[i].res_mul
        players[i].x55 = players[i].res_mul1

    for i in range(len(players)):
        players[i].set_mult(players[i].x72,players[i].x55)
    multi_3p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x127 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult(players[i].x127,players[i].x127)
    multi_3p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x254 = players[i].res_mul


def x_inverse_method2(players,cofflambda,alpha):
    for i in range(len(players)):
        players[i].set_mult(players[i].x,players[i].x)
    multi_3p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x2 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult(players[i].x2,players[i].x2)
        players[i].set_mult_parallel(players[i].x,players[i].x2)
    multi_3p_parallel(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x4 = players[i].res_mul
        players[i].x3 = players[i].res_mul1

    for i in range(len(players)):
        players[i].set_mult(players[i].x4,players[i].x4)
        players[i].set_mult_parallel(players[i].x3,players[i].x4)
    multi_3p_parallel(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x8 = players[i].res_mul
        players[i].x7 = players[i].res_mul1

    for i in range(len(players)):
        players[i].set_mult(players[i].x8,players[i].x8)
        players[i].set_mult_parallel(players[i].x7,players[i].x8)
    multi_3p_parallel(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x16 = players[i].res_mul
        players[i].x15 = players[i].res_mul1

    for i in range(len(players)):
        players[i].set_mult(players[i].x16,players[i].x16)
        players[i].set_mult_parallel(players[i].x15,players[i].x16)
    multi_3p_parallel(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x32 = players[i].res_mul
        players[i].x31 = players[i].res_mul1

    for i in range(len(players)):
        players[i].set_mult(players[i].x32,players[i].x32)
        players[i].set_mult_parallel(players[i].x31,players[i].x32)
    multi_3p_parallel(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x64 = players[i].res_mul
        players[i].x63 = players[i].res_mul1

    for i in range(len(players)):
        players[i].set_mult(players[i].x63,players[i].x64)
    multi_3p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x127 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult(players[i].x127,players[i].x127)
    multi_3p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x254 = players[i].res_mul


def x_inverse_method3(players,cofflambda,alpha):
    prepare = []
    for i in range(len(players)):
        prepare.append(players[i].get_prepared_shares())
        players[i].open = players[i].x+prepare[i][0]
    open_val(players,alpha)
    for i in range(3):
        for j in range(1,8):
            players[i].mem = players[i].mem*players[i].mem
            setattr(players[i], f"x{2**j}", players[i].mem + prepare[i][j])

    for i in range(len(players)):
        players[i].set_mult(players[i].x2,players[i].x4)
        players[i].set_mult_parallel(players[i].x8,players[i].x16)
        players[i].set_mult_treble(players[i].x32,players[i].x64)
    multi_3p_treble(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x6 = players[i].res_mul
        players[i].x24 = players[i].res_mul1
        players[i].x96 = players[i].res_mul2

    for i in range(len(players)):
        players[i].set_mult(players[i].x6,players[i].x24)
        players[i].set_mult_parallel(players[i].x96,players[i].x128)
    multi_3p_parallel(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x30 = players[i].res_mul
        players[i].x224 = players[i].res_mul1

    for i in range(len(players)):
        players[i].set_mult(players[i].x30,players[i].x224)
    multi_3p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x254 = players[i].res_mul


def x_inverse4p_method1(players,cofflambda,cofflambda3,alpha):
    for i in range(len(players)):
        players[i].set_mult2(players[i].x,players[i].x,players[i].x)
    multi2_4p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x3 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult2(players[i].x3,players[i].x3,players[i].x3)
    multi2_4p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x9 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult2(players[i].x9,players[i].x9,players[i].x9)
        players[i].set_mult2_parallel(players[i].x,players[i].x,players[i].x9)
    multi2_4p_parallel(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x27 = players[i].res_mul
        players[i].x11 = players[i].res_mul1

    for i in range(len(players)):
        players[i].set_mult2(players[i].x27,players[i].x27,players[i].x27)
    multi2_4p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x81 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult2(players[i].x81,players[i].x81,players[i].x81)
    multi2_4p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x243 = players[i].res_mul

    for i in range(len(players)):
        players[i].set_mult(players[i].x243,players[i].x11)
    multi_4p(players,cofflambda3,alpha)
    for i in range(len(players)):
        players[i].x254 = players[i].res_mul


def x_inverse4p_method2(players,cofflambda,alpha):
    prepare = []
    for i in range(len(players)):
        prepare.append(players[i].get_prepared_shares())
        players[i].open = players[i].x+prepare[i][0]
    open_val_4p(players,alpha)
    for i in range(4):
        for j in range(1,8):
            players[i].mem = players[i].mem*players[i].mem
            setattr(players[i], f"x{2**j}", players[i].mem + prepare[i][j])

    for i in range(len(players)):
        players[i].set_mult2(players[i].x2,players[i].x4,players[i].x8)
        players[i].set_mult2_parallel(players[i].x16,players[i].x32,players[i].x64)
    multi2_4p_parallel(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x14 = players[i].res_mul
        players[i].x112 = players[i].res_mul1

    for i in range(len(players)):
        players[i].set_mult2(players[i].x128,players[i].x112,players[i].x14)
    multi2_4p(players,cofflambda,alpha)
    for i in range(len(players)):
        players[i].x254 = players[i].res_mul


def open_val(players,alpha):
    global broadcast_time
    #t0 = datetime.datetime.now()
    t0 = time.time()
    t1 = Thread(target=players[0].prep_rec, args=(players[0].open,))
    t2 = Thread(target=players[1].send_num, args=(players[1].open, players[0].ip, players[0].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[0].mem = reconstruct(alpha, players[0].open, players[0].other)
    players[1].mem = reconstruct(alpha,players[1].rec_data, players[1].open)
    t1 = Thread(target = players[2].oneway_rec, args=())
    t2 = Thread(target=players[1].oneway_send, args=(players[1].mem, players[2].ip, players[2].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[2].mem = players[2].oneway_other
    t1 = Thread(target = players[2].oneway_rec, args=())
    t2 = Thread(target=players[0].oneway_send, args=(players[0].mem, players[2].ip, players[2].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    #t1 = datetime.datetime.now()
    t1 = time.time()
    broadcast_time+=t1-t0

def open_val_4p(players,alpha):
    global broadcast_time
    t0 = time.time()
    t1 = Thread(target=players[0].prep_rec, args=(players[0].open,))
    t2 = Thread(target=players[1].send_num, args=(players[1].open, players[0].ip, players[0].rec_port))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    players[0].mem = reconstruct(alpha, players[0].open, players[0].other)
    players[1].mem = reconstruct(alpha, players[1].rec_data, players[1].open)
    t1 = Thread(target=players[3].oneway_rec, args=())
    t2 = Thread(target=players[1].oneway_send, args=(players[1].mem, players[3].ip, players[3].rec_port))
    t3 = Thread(target=players[2].oneway_rec, args=())
    t4 = Thread(target=players[0].oneway_send, args=(players[0].mem, players[2].ip, players[2].rec_port))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    players[2].mem = players[2].oneway_other
    players[3].mem = players[3].oneway_other
    t1 = time.time()
    broadcast_time+=t1-t0


def affine_linear_function(players,alpha):
    prepare = []
    for i in range(len(players)):
        prepare.append(players[i].get_prepared_bits())
        players[i].open = players[i].x254+prepare[i][0]
    open_val(players,alpha)
    for i in range(len(players)):
        players[i].mem = '{:0>8b}'.format(int(players[i].mem))
        vec = GF256([[GF256(players[i].mem[7])+GF256(prepare[i][1])],[GF256(players[i].mem[6])+GF256(prepare[i][2])],
               [GF256(players[i].mem[5])+GF256(prepare[i][3])],[GF256(players[i].mem[4])+GF256(prepare[i][4])],
               [GF256(players[i].mem[3])+GF256(prepare[i][5])],[GF256(players[i].mem[2])+GF256(prepare[i][6])],
               [GF256(players[i].mem[1])+GF256(prepare[i][7])],[GF256(players[i].mem[0])+GF256(prepare[i][8])]])
        cons = GF256([[1,0,0,0,1,1,1,1],
                     [1,1,0,0,0,1,1,1],
                     [1,1,1,0,0,0,1,1],
                     [1,1,1,1,0,0,0,1],
                     [1,1,1,1,1,0,0,0],
                     [0,1,1,1,1,1,0,0],
                     [0,0,1,1,1,1,1,0],
                     [0,0,0,1,1,1,1,1]])
        vec = cons@vec+GF256([[1],[1],[0],[0],[0],[1],[1],[0]])
        players[i].mem = GF256(vec[0][0]*GF256(1)+vec[1][0]*GF256(2)+vec[2][0]*GF256(4)+vec[3][0]*GF256(8)+ \
                               vec[4][0]*GF256(16)+vec[5][0]*GF256(32)+vec[6][0]*GF256(64)+vec[7][0]*GF256(128))


def affine_linear_function_4p(players,alpha):
    prepare = []
    for i in range(len(players)):
        prepare.append(players[i].get_prepared_bits())
        players[i].open = players[i].x254+prepare[i][0]
    open_val_4p(players,alpha)
    for i in range(len(players)):
        players[i].mem = '{:0>8b}'.format(int(players[i].mem))
        vec = GF256([[GF256(players[i].mem[7])+GF256(prepare[i][1])],[GF256(players[i].mem[6])+GF256(prepare[i][2])],
               [GF256(players[i].mem[5])+GF256(prepare[i][3])],[GF256(players[i].mem[4])+GF256(prepare[i][4])],
               [GF256(players[i].mem[3])+GF256(prepare[i][5])],[GF256(players[i].mem[2])+GF256(prepare[i][6])],
               [GF256(players[i].mem[1])+GF256(prepare[i][7])],[GF256(players[i].mem[0])+GF256(prepare[i][8])]])
        cons = GF256([[1,0,0,0,1,1,1,1],
                     [1,1,0,0,0,1,1,1],
                     [1,1,1,0,0,0,1,1],
                     [1,1,1,1,0,0,0,1],
                     [1,1,1,1,1,0,0,0],
                     [0,1,1,1,1,1,0,0],
                     [0,0,1,1,1,1,1,0],
                     [0,0,0,1,1,1,1,1]])
        vec = cons@vec+GF256([[1],[1],[0],[0],[0],[1],[1],[0]])
        players[i].mem = GF256(vec[0][0]*GF256(1)+vec[1][0]*GF256(2)+vec[2][0]*GF256(4)+vec[3][0]*GF256(8)+ \
                               vec[4][0]*GF256(16)+vec[5][0]*GF256(32)+vec[6][0]*GF256(64)+vec[7][0]*GF256(128))


def subbyte_4p_method1(players,coff,coff3,alpha):
    for i in range(len(players)):
        players[i].tobemul1[0] = players[i].x
        players[i].tobemul2[0] = players[i].x
        players[i].tobemul3[0] = players[i].x
    multi2_4p_parallel_multi(players,coff,alpha,1)
    for i in range(len(players)):
        players[i].x3 = players[i].res_mul[0]

    for i in range(len(players)):
        players[i].tobemul1[0] = players[i].x3
        players[i].tobemul1[1] = players[i].x
        players[i].tobemul2[0] = players[i].x3
        players[i].tobemul2[1] = players[i].x3
        players[i].tobemul3[0] = players[i].x3
    multi_4p_parallel_multi(players,coff,coff3,alpha,1,1)
    for i in range(len(players)):
        players[i].x9 = players[i].res_mul[0]
        players[i].x4 = players[i].res_mul[1]

    for i in range(len(players)):
        players[i].tobemul1[0] = players[i].x9
        players[i].tobemul1[1] = players[i].x9
        players[i].tobemul1[2] = players[i].x9
        players[i].tobemul1[3] = players[i].x4
        players[i].tobemul2[0] = players[i].x9
        players[i].tobemul2[1] = players[i].x
        players[i].tobemul2[2] = players[i].x9
        players[i].tobemul2[3] = players[i].x4
        players[i].tobemul3[0] = players[i].x9
        players[i].tobemul3[1] = players[i].x
        players[i].tobemul3[2] = players[i].x
    multi_4p_parallel_multi(players,coff,coff3,alpha,1,3)
    for i in range(len(players)):
        players[i].x27 = players[i].res_mul[0]
        players[i].x11 = players[i].res_mul[1]
        players[i].x19 = players[i].res_mul[2]
        players[i].x8 = players[i].res_mul[3]

    for i in range(len(players)):
        players[i].tobemul1[0] = players[i].x27
        players[i].tobemul1[1] = players[i].x27
        players[i].tobemul2[0] = players[i].x27
        players[i].tobemul2[1] = players[i].x
        players[i].tobemul3[0] = players[i].x27
        players[i].tobemul3[1] = players[i].x
    multi2_4p_parallel_multi(players,coff,alpha,2)
    for i in range(len(players)):
        players[i].x81 = players[i].res_mul[0]
        players[i].x29 = players[i].res_mul[1]

    for i in range(len(players)):
        players[i].tobemul1[0] = players[i].x81
        players[i].tobemul1[1] = players[i].x29
        players[i].tobemul2[0] = players[i].x81
        players[i].tobemul2[1] = players[i].x29
        players[i].tobemul3[0] = players[i].x81
        players[i].tobemul3[1] = players[i].x3
    multi2_4p_parallel_multi(players, coff, alpha, 2)
    for i in range(len(players)):
        players[i].x243 = players[i].res_mul[0]
        players[i].x61 = players[i].res_mul[1]

    for i in range(len(players)):
        players[i].tobemul1[0] = players[i].x81
        players[i].tobemul1[1] = players[i].x81
        players[i].tobemul1[2] = players[i].x81
        players[i].tobemul1[3] = players[i].x243
        players[i].tobemul1[4] = players[i].x243
        players[i].tobemul1[5] = players[i].x243
        players[i].tobemul1[6] = players[i].x243
        players[i].tobemul1[7] = players[i].x243
        players[i].tobemul2[0] = players[i].x27
        players[i].tobemul2[1] = players[i].x81
        players[i].tobemul2[2] = players[i].x81
        players[i].tobemul2[3] = players[i].x243
        players[i].tobemul2[4] = players[i].x3
        players[i].tobemul2[5] = players[i].x4
        players[i].tobemul2[6] = players[i].x9
        players[i].tobemul2[7] = players[i].x11
        players[i].tobemul3[0] = players[i].x19
        players[i].tobemul3[1] = players[i].x29
        players[i].tobemul3[2] = players[i].x61
        players[i].tobemul3[3] = players[i].x8
        players[i].tobemul3[4] = players[i].x
        players[i].tobemul3[5] = players[i].x4
        players[i].tobemul3[6] = players[i].x
    multi_4p_parallel_multi(players,coff,coff3,alpha,1,7)
    for i in range(len(players)):
        players[i].x127 = players[i].res_mul[0]
        players[i].x191 = players[i].res_mul[1]
        players[i].x223 = players[i].res_mul[2]
        players[i].x239 = players[i].res_mul[3]
        players[i].x247 = players[i].res_mul[4]
        players[i].x251 = players[i].res_mul[5]
        players[i].x253 = players[i].res_mul[6]
        players[i].x254 = players[i].res_mul[7]
    for i in range(len(players)):
        players[i].mem = GF256(0x63) + GF256(0x8F)*players[i].x127 + GF256(0xB5)*players[i].x191 + GF256(0x01)*players[i].x223 \
                         + GF256(0xF4)*players[i].x239 + GF256(0x25)*players[i].x247 + GF256(0xF9)*players[i].x251 + GF256(0x09)*players[i].x253 + GF256(0x05)*players[i].x254



def subbyte_4p_method2(players,cofflambda,alpha):
    prepare = []
    for i in range(len(players)):
        prepare.append(players[i].get_prepared_shares())
        players[i].open = players[i].x+prepare[i][0]
    open_val_4p(players,alpha)
    for i in range(4):
        for j in range(1,8):
            players[i].mem = players[i].mem*players[i].mem
            setattr(players[i], f"x{2**j}", players[i].mem + prepare[i][j])
    for i in range(len(players)):
        players[i].tobemul1[0] = players[i].x
        players[i].tobemul1[1] = players[i].x
        players[i].tobemul1[2] = players[i].x4
        players[i].tobemul1[3] = players[i].x8
        players[i].tobemul1[4] = players[i].x8
        players[i].tobemul1[5] = players[i].x32
        players[i].tobemul2[0] = players[i].x2
        players[i].tobemul2[1] = players[i].x2
        players[i].tobemul2[2] = players[i].x8
        players[i].tobemul2[3] = players[i].x16
        players[i].tobemul2[4] = players[i].x16
        players[i].tobemul2[5] = players[i].x64
        players[i].tobemul3[0] = players[i].x4
        players[i].tobemul3[1] = players[i].x8
        players[i].tobemul3[2] = players[i].x16
        players[i].tobemul3[3] = players[i].x32
        players[i].tobemul3[4] = players[i].x64
        players[i].tobemul3[5] = players[i].x128
    multi2_4p_parallel_multi(players,cofflambda,alpha,6)
    for i in range(len(players)):
        players[i].x7 = players[i].res_mul[0]
        players[i].x11 = players[i].res_mul[1]
        players[i].x28 = players[i].res_mul[2]
        players[i].x56 = players[i].res_mul[3]
        players[i].x88 = players[i].res_mul[4]
        players[i].x224 = players[i].res_mul[5]
    for i in range(len(players)):
        players[i].tobemul1[0] = players[i].x7
        players[i].tobemul1[1] = players[i].x7
        players[i].tobemul1[2] = players[i].x7
        players[i].tobemul1[3] = players[i].x7
        players[i].tobemul1[4] = players[i].x7
        players[i].tobemul1[5] = players[i].x11
        players[i].tobemul1[6] = players[i].x
        players[i].tobemul1[7] = players[i].x2
        players[i].tobemul2[0] = players[i].x56
        players[i].tobemul2[1] = players[i].x56
        players[i].tobemul2[2] = players[i].x88
        players[i].tobemul2[3] = players[i].x8
        players[i].tobemul2[4] = players[i].x16
        players[i].tobemul2[5] = players[i].x16
        players[i].tobemul2[6] = players[i].x28
        players[i].tobemul2[7] = players[i].x28
        players[i].tobemul3[0] = players[i].x64
        players[i].tobemul3[1] = players[i].x128
        players[i].tobemul3[2] = players[i].x128
        players[i].tobemul3[3] = players[i].x224
        players[i].tobemul3[4] = players[i].x224
        players[i].tobemul3[5] = players[i].x224
        players[i].tobemul3[6] = players[i].x224
        players[i].tobemul3[7] = players[i].x224
    multi2_4p_parallel_multi(players, cofflambda, alpha, 8)
    for i in range(len(players)):
        players[i].x127 = players[i].res_mul[0]
        players[i].x191 = players[i].res_mul[1]
        players[i].x223 = players[i].res_mul[2]
        players[i].x239 = players[i].res_mul[3]
        players[i].x247 = players[i].res_mul[4]
        players[i].x251 = players[i].res_mul[5]
        players[i].x253 = players[i].res_mul[6]
        players[i].x254 = players[i].res_mul[7]
    for i in range(len(players)):
        players[i].mem = GF256(0x63) + GF256(0x8F)*players[i].x127 + GF256(0xB5)*players[i].x191 + GF256(0x01)*players[i].x223 \
                         + GF256(0xF4)*players[i].x239 + GF256(0x25)*players[i].x247 + GF256(0xF9)*players[i].x251 + GF256(0x09)*players[i].x253 + GF256(0x05)*players[i].x254


def SubByte_2(players,coff,coff3,alpha):
    for i in range(4):
        for j in range(4):
            for k in range(len(players)):
                players[k].set_x(players[k].input[i,j])
            subbyte_4p_method2(players, coff, alpha)
            #subbyte_4p_method1(players, coff, coff3, alpha)
            for k in range(len(players)):
                players[k].input[i, j] = players[k].mem



def S_box(players,coff,coff3,alpha):
    #x_inverse4p_method1(players, coff, coff3, alpha)
    #x_inverse4p_method2(players, coff, alpha)
    #x_inverse(players,coff,alpha)
    #x_inverse_method2(players,coff,alpha)
    x_inverse_method3(players,coff,alpha)
    #affine_linear_function(players,alpha)
    affine_linear_function(players, alpha)

def SubByte(players,coff,coff3,alpha):
    for i in range(4):
        for j in range(4):
            for k in range(len(players)):
                players[k].set_x(players[k].input[i,j])
            S_box(players,coff,coff3,alpha)
            for k in range(len(players)):
                players[k].input[i,j] = players[k].mem

def ShiftRows(players):
    for i in range(len(players)):
        for j in range(1,4):
            players[i].input[j] = np.roll(players[i].input[j],j)


def MixColumns(players):
    for i in range(len(players)):
        players[i].input = GF256([[0x02,0x03,0x01,0x01],
                                  [0x01,0x02,0x03,0x01],
                                  [0x01,0x01,0x02,0x03],
                                  [0x03,0x01,0x01,0x02]])@players[i].input


def KeyExpansion(players,roundconst,coff,coff3,alpha):
    for i in range(len(players)):
        players[i].set_x(players[i].key[1,3])
    S_box(players,coff,coff3,alpha)
    for i in range(len(players)):
        players[i].key[0,0] += players[i].mem+roundconst

    for i in range(len(players)):
        players[i].set_x(players[i].key[2,3])
    S_box(players,coff,coff3,alpha)
    for i in range(len(players)):
        players[i].key[1,0] += players[i].mem

    for i in range(len(players)):
        players[i].set_x(players[i].key[3,3])
    S_box(players,coff,coff3,alpha)
    for i in range(len(players)):
        players[i].key[2,0] += players[i].mem

    for i in range(len(players)):
        players[i].set_x(players[i].key[0,3])
    S_box(players,coff,coff3,alpha)
    for i in range(len(players)):
        players[i].key[3,0] += players[i].mem

    for i in range(len(players)):
        for j in range(1,4):
            for k in range(4):
                players[i].key[k,j] += players[i].key[k,j-1]


def KeyExpansion_2(players,roundconst,coff,coff3,alpha):
    for i in range(len(players)):
        players[i].set_x(players[i].key[1,3])
    subbyte_4p_method2(players, coff, alpha)
    #subbyte_4p_method1(players, coff, coff3, alpha)
    for i in range(len(players)):
        players[i].key[0,0] += players[i].mem+roundconst

    for i in range(len(players)):
        players[i].set_x(players[i].key[2,3])
    subbyte_4p_method2(players, coff, alpha)
    #subbyte_4p_method1(players, coff, coff3, alpha)
    for i in range(len(players)):
        players[i].key[1,0] += players[i].mem

    for i in range(len(players)):
        players[i].set_x(players[i].key[3,3])
    subbyte_4p_method2(players, coff, alpha)
    #subbyte_4p_method1(players, coff, coff3, alpha)
    for i in range(len(players)):
        players[i].key[2,0] += players[i].mem

    for i in range(len(players)):
        players[i].set_x(players[i].key[0,3])
    subbyte_4p_method2(players, coff, alpha)
    #subbyte_4p_method1(players, coff, coff3, alpha)
    for i in range(len(players)):
        players[i].key[3,0] += players[i].mem

    for i in range(len(players)):
        for j in range(1,4):
            for k in range(4):
                players[i].key[k,j] += players[i].key[k,j-1]



def AddRoundKey(players,):
    for i in range(len(players)):
        players[i].input = players[i].input+players[i].key


def subbyte_poly(x):
    res = GF256(0x63) + GF256(0x8F)*(GF256(x)**127) + GF256(0xB5)*(GF256(x)**191) + GF256(0x01)*(GF256(x)**223) \
        + GF256(0xF4)*(GF256(x)**239) + GF256(0x25)*(GF256(x)**247) + GF256(0xF9)*(GF256(x)**251) + GF256(0x09)*(GF256(x)**253) + GF256(0x05)*(GF256(x)**254)

    return res


def aes_encode(players,coff,coff3,alpha,roundconst):
    #for 3p, only use coff, for 4p, coff for 4, coff3 for 3
    AddRoundKey(players)
    for i in range(9):
        SubByte(players,coff,coff3,alpha)
        ShiftRows(players)
        MixColumns(players)
        KeyExpansion(players, roundconst[i], coff, coff3, alpha)
    SubByte(players, coff, coff3, alpha)
    ShiftRows(players)
    KeyExpansion(players, roundconst[i], coff, coff3, alpha)
    AddRoundKey(players)


def aes_encode_2(players,coff,coff3,alpha,roundconst):
    AddRoundKey(players)
    for i in range(9):
        SubByte_2(players, coff, coff3, alpha)
        ShiftRows(players)
        MixColumns(players)
        KeyExpansion_2(players,roundconst[i],coff,coff3,alpha)
    SubByte_2(players, coff, coff3, alpha)
    ShiftRows(players)
    KeyExpansion_2(players,roundconst[9],coff,coff3,alpha)
    AddRoundKey(players)




if __name__ == "__main__":
    inputs = GF256([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]])
    share_inputs = []
    for i in range(3):
        share_inputs.append(GF256([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]))
    keys = GF256([[16,15,14,13],[12,11,10,9],[8,7,6,5],[4,3,2,1]])
    share_keys = []
    for i in range(3):
        share_keys.append(GF256([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]))
    for i in range(4):
        for j in range(4):
            tmp = shamir_secret_sharing256(inputs[i,j],alpha_3p,3).getval()
            for k in range(3):
                share_inputs[k][i,j] = tmp[k]
    for i in range(4):
        for j in range(4):
            tmp = shamir_secret_sharing256(keys[i,j],alpha_3p,3).getval()
            for k in range(3):
                share_keys[k][i,j] = tmp[k]
    players = []
    coff = shamir_secret_sharing256(GF256(1),alpha_3p,3).getlambda()
    coff3 = shamir_secret_sharing256(GF256(1),alpha_3p,3).getlambda()
    for i in range(3):
        players.append(ComputePlayer3p_method3("localhost",4589+i))
    for i in range(len(players)):
        players[i].set_input(share_inputs[i])
        players[i].set_key(share_keys[i])
    for i in range(len(players)):
        players[i].read_prepared_bits(i)
        players[i].read_prepared_shares(i)
    roundconst = GF256([1,2,4,8,16,32,64,128,27,54])
    #broadcast_time = datetime.datetime.now()
    #broadcast_time = time.time()
    original_time = time.time()
    aes_encode(players,coff,coff3,alpha_3p,roundconst)
    print(broadcast_time)
    #t0 = datetime.datetime.now()
    t0 = time.time()
    print(t0-original_time)


