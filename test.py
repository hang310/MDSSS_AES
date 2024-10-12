#from utils import *
import utils as u
#from utils import broadcast_time, aes_encode, GF256, shamir_secret_sharing256, ComputePlayer3p_method3
import datetime, time
import galois

GF256 = galois.GF(2**8, irreducible_poly=galois.Poly.Degrees([8,4,3,1,0]))

alpha_3p = GF256([2,3,4])
alpha_4p = GF256([2,3,4,5])


if __name__=="__main__":
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
            tmp = u.shamir_secret_sharing256(inputs[i,j],alpha_4p,3).getval()
            for k in range(3):
                share_inputs[k][i,j] = tmp[k]
    for i in range(4):
        for j in range(4):
            tmp = u.shamir_secret_sharing256(keys[i,j],alpha_4p,3).getval()
            for k in range(3):
                share_keys[k][i,j] = tmp[k]
    players = []
    coff = u.shamir_secret_sharing256(GF256(1),alpha_4p,4).getlambda()
    coff3 = u.shamir_secret_sharing256(GF256(1), alpha_3p, 3).getlambda()
    for i in range(3):
        players.append(u.ComputePlayer3p_method3("localhost",5090+11*i))
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
    for i in range(1):
        u.aes_encode(players,coff3,coff3,alpha_3p,roundconst)
    print(u.broadcast_time)
    #t0 = datetime.datetime.now()
    t0 = time.time()
    print(t0-original_time)

    # test for 4p
    # inputs = GF256([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]])
    # share_inputs = []
    # for i in range(4):
    #     share_inputs.append(GF256([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]))
    # keys = GF256([[16,15,14,13],[12,11,10,9],[8,7,6,5],[4,3,2,1]])
    # share_keys = []
    # for i in range(4):
    #     share_keys.append(GF256([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]))
    # for i in range(4):
    #     for j in range(4):
    #         tmp = u.shamir_secret_sharing256(inputs[i,j],alpha_4p,4).getval()
    #         for k in range(4):
    #             share_inputs[k][i,j] = tmp[k]
    # for i in range(4):
    #     for j in range(4):
    #         tmp = u.shamir_secret_sharing256(keys[i,j],alpha_4p,4).getval()
    #         for k in range(4):
    #             share_keys[k][i,j] = tmp[k]
    # players = []
    # coff = u.shamir_secret_sharing256(GF256(1),alpha_4p,4).getlambda()
    # coff3 = u.shamir_secret_sharing256(GF256(1), alpha_3p, 3).getlambda()
    # for i in range(4):
    #     players.append(u.ComputePlayer4p_method2("localhost",5090+11*i))
    # for i in range(len(players)):
    #     players[i].set_input(share_inputs[i])
    #     players[i].set_key(share_keys[i])
    # for i in range(len(players)):
    #     players[i].read_prepared_bits(i)
    #     players[i].read_prepared_shares(i)
    # roundconst = GF256([1,2,4,8,16,32,64,128,27,54])
    # #broadcast_time = datetime.datetime.now()
    # #broadcast_time = time.time()
    # original_time = time.time()
    # for i in range(100):
    #     u.aes_encode(players,coff,coff3,alpha_4p,roundconst)
    # print(u.broadcast_time)
    # #t0 = datetime.datetime.now()
    # t0 = time.time()
    # print(t0-original_time)