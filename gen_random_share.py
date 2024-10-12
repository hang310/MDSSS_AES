import galois
from utils import shamir_secret_sharing256
import random
import numpy as np
from utils import reconstruct

GF256 = galois.GF(2**8, irreducible_poly=galois.Poly.Degrees([8,4,3,1,0]))

alpha_3p = GF256([2,3,4])
alpha_4p = GF256([2,3,4,5])

def gen_random_share_3p():
    with open("./prepared_random/three_party/party0.txt", 'w') as f_0, open("./prepared_random/three_party/party1.txt", 'w') as f_1, open("./prepared_random/three_party/party2.txt", 'w') as f_2, open("./prepared_random/three_party/openval.txt", 'w') as f_open:
        for k in range(25000):
            rand_val = random.randint(1,255)
            rand_val = GF256(rand_val)
            randwrite = []
            randwrite.append(rand_val)
            f_open.write(str(int(rand_val)) + '\n')
            for i in range(7):
                randwrite.append(randwrite[i]*randwrite[i])
            for i in range(7):
                share = shamir_secret_sharing256(randwrite[i],alpha_3p,3).getval()
                f_0.write(str(int(share[0]))+' ')
                f_1.write(str(int(share[1]))+' ')
                f_2.write(str(int(share[2]))+' ')
            share = shamir_secret_sharing256(randwrite[7],alpha_3p,3).getval()
            f_0.write(str(int(share[0])) + '\n')
            f_1.write(str(int(share[1])) + '\n')
            f_2.write(str(int(share[2])) + '\n')


def gen_random_share_4p():
    with open("./prepared_random/four_party/party0.txt", 'w') as f_0, open("./prepared_random/four_party/party1.txt", 'w') as f_1, open("./prepared_random/four_party/party2.txt", 'w') as f_2, open("./prepared_random/four_party/party3.txt", 'w') as f_3, open("./prepared_random/four_party/openval.txt", 'w') as f_open:
        for k in range(25000):
            rand_val = random.randint(1,255)
            rand_val = GF256(rand_val)
            randwrite = []
            randwrite.append(rand_val)
            f_open.write(str(int(rand_val)) + '\n')
            for i in range(7):
                randwrite.append(randwrite[i]*randwrite[i])
            for i in range(7):
                share = shamir_secret_sharing256(randwrite[i],alpha_4p,4).getval()
                f_0.write(str(int(share[0]))+' ')
                f_1.write(str(int(share[1]))+' ')
                f_2.write(str(int(share[2]))+' ')
                f_3.write(str(int(share[3]))+' ')
            share = shamir_secret_sharing256(randwrite[7],alpha_4p,4).getval()
            f_0.write(str(int(share[0])) + '\n')
            f_1.write(str(int(share[1])) + '\n')
            f_2.write(str(int(share[2])) + '\n')
            f_3.write(str(int(share[3])) + '\n')



if __name__ == "__main__":
    gen_random_share_3p()








