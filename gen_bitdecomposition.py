import galois
from utils import shamir_secret_sharing256
import random
import numpy as np

GF256 = galois.GF(2**8, irreducible_poly=galois.Poly.Degrees([8,4,3,1,0]))

alpha_3p = GF256([2,3,4])
alpha_4p = GF256([2,3,4,5])

def gen_bit_decomposition_3p():
    with open("./prepared/three_party/opened_value.txt", 'w') as f_open, open("./prepared/three_party/party0.txt", 'w') as f_0, open("./prepared/three_party/party1.txt", 'w') as f_1, open("./prepared/three_party/party2.txt", 'w') as f_2:
        for k in range(25000):
            randbit = []
            for i in range(8):
                randbit.append(random.randint(0,1))
            open_val = GF256(randbit[0]*1+randbit[1]*2+randbit[2]*4+randbit[3]*8+randbit[4]*16
                                   +randbit[5]*32+randbit[6]*64+randbit[7]*128)
            f_open.write(str(int(open_val))+ " " + str(randbit)+'\n')
            shares = []
            open_val_share = shamir_secret_sharing256(open_val,alpha_3p,3).getval()
            for i in range(8):
                shares.append(shamir_secret_sharing256(GF256(randbit[i]),alpha_3p,3).getval())
            f_0.write(str(int(open_val_share[0]))+" "+str(int(shares[0][0]))+" "+str(int(shares[1][0]))+" "
                      +str(int(shares[2][0]))+" "+str(int(shares[3][0]))+" "+str(int(shares[4][0]))+" "
                      +str(int(shares[5][0]))+" "+str(int(shares[6][0]))+" "+str(int(shares[7][0]))+'\n')
            f_1.write(str(int(open_val_share[1]))+" "+str(int(shares[0][1]))+" "+str(int(shares[1][1]))+" "
                      +str(int(shares[2][1]))+" "+str(int(shares[3][1]))+" "+str(int(shares[4][1]))+" "
                      +str(int(shares[5][1]))+" "+str(int(shares[6][1]))+" "+str(int(shares[7][1]))+'\n')
            f_2.write(str(int(open_val_share[2]))+" "+str(int(shares[0][2]))+" "+str(int(shares[1][2]))+" "
                      +str(int(shares[2][2]))+" "+str(int(shares[3][2]))+" "+str(int(shares[4][2]))+" "
                      +str(int(shares[5][2]))+" "+str(int(shares[6][2]))+" "+str(int(shares[7][2]))+'\n')

def gen_bit_decomposition_4p():
    with open("./prepared/four_party/opened_value.txt", 'w') as f_open, open("./prepared/four_party/party0.txt", 'w') as f_0, open("./prepared/four_party/party1.txt", 'w') as f_1, open("./prepared/four_party/party2.txt", 'w') as f_2, open("./prepared/four_party/party3.txt", 'w') as f_3:
        for k in range(25000):
            randbit = []
            for i in range(8):
                randbit.append(random.randint(0,1))
            open_val = GF256(randbit[0]*1+randbit[1]*2+randbit[2]*4+randbit[3]*8+randbit[4]*16
                                   +randbit[5]*32+randbit[6]*64+randbit[7]*128)
            f_open.write(str(int(open_val))+ " " + str(randbit)+'\n')
            shares = []
            open_val_share = shamir_secret_sharing256(open_val,alpha_4p,4).getval()
            for i in range(8):
                shares.append(shamir_secret_sharing256(GF256(randbit[i]),alpha_4p,4).getval())
            f_0.write(str(int(open_val_share[0]))+" "+str(int(shares[0][0]))+" "+str(int(shares[1][0]))+" "
                      +str(int(shares[2][0]))+" "+str(int(shares[3][0]))+" "+str(int(shares[4][0]))+" "
                      +str(int(shares[5][0]))+" "+str(int(shares[6][0]))+" "+str(int(shares[7][0]))+'\n')
            f_1.write(str(int(open_val_share[1]))+" "+str(int(shares[0][1]))+" "+str(int(shares[1][1]))+" "
                      +str(int(shares[2][1]))+" "+str(int(shares[3][1]))+" "+str(int(shares[4][1]))+" "
                      +str(int(shares[5][1]))+" "+str(int(shares[6][1]))+" "+str(int(shares[7][1]))+'\n')
            f_2.write(str(int(open_val_share[2]))+" "+str(int(shares[0][2]))+" "+str(int(shares[1][2]))+" "
                      +str(int(shares[2][2]))+" "+str(int(shares[3][2]))+" "+str(int(shares[4][2]))+" "
                      +str(int(shares[5][2]))+" "+str(int(shares[6][2]))+" "+str(int(shares[7][2]))+'\n')
            f_3.write(str(int(open_val_share[3]))+" "+str(int(shares[0][3]))+" "+str(int(shares[1][3]))+" "
                      +str(int(shares[2][3]))+" "+str(int(shares[3][3]))+" "+str(int(shares[4][3]))+" "
                      +str(int(shares[5][3]))+" "+str(int(shares[6][3]))+" "+str(int(shares[7][3]))+'\n')


if __name__ == "__main__":
    gen_bit_decomposition_4p()




















'''
def reconstruct(alpha, i1, i2):
    A = GF256([[1, alpha[0]], [1, alpha[1]]])
    B = np.linalg.inv(A)
    C = GF256([[i1], [i2]])
    D = B @ C
    return D[0, 0]


randbit = []
for i in range(8):
    randbit.append(random.randint(0,1))
print(randbit)
shares = []
for i in range(8):
    shares.append(shamir_secret_sharing256(GF256(randbit[i]),alpha,4))

val = GF256(randbit[0]*1+randbit[1]*2+randbit[2]*4+randbit[3]*8+randbit[4]*16+randbit[5]*32+randbit[6]*64+randbit[7]*128)
print(val)
#val_share = shamir_secret_sharing256(val,4)

shares_val = []
for i in range(8):
    shares_val.append(shares[i].getval())

affine_linear_matrix = GF256([[1,0,0,0,1,1,1,1],
                              [1,1,0,0,0,1,1,1],
                              [1,1,1,0,0,0,1,1],
                              [1,1,1,1,0,0,0,1],
                              [1,1,1,1,1,0,0,0],
                              [0,1,1,1,1,1,0,0],
                              [0,0,1,1,1,1,1,0],
                              [0,0,0,1,1,1,1,1]])

share_val = affine_linear_matrix@GF256(shares_val)
orig_val = affine_linear_matrix@GF256([[randbit[0]],[randbit[1]],[randbit[2]],[randbit[3]],[randbit[4]],[randbit[5]],
                                       [randbit[6]],[randbit[7]]])

res_val = []
for j in range(4):
    res_val.append(GF256(shares_val[0][j]*GF256(1)+shares_val[1][j]*GF256(2)+shares_val[2][j]*GF256(4)+shares_val[3][j]*GF256(8)+
                           shares_val[4][j]*GF256(16)+shares_val[5][j]*GF256(32)+shares_val[6][j]*GF256(64)+shares_val[7][j]*GF256(128)))


tmp = reconstruct(alpha,res_val[0],res_val[1])

#print(orig_val)
#val = GF256(orig_val[0][0]*GF256(1)+orig_val[1][0]*GF256(2)+orig_val[2][0]*GF256(4)+orig_val[3][0]*GF256(8)
#            +orig_val[4][0]*GF256(16)+orig_val[5][0]*GF256(32)+orig_val[6][0]*GF256(64)+orig_val[7][0]*GF256(128))


print(tmp)
#print(val)
'''
















