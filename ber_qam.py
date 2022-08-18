import sys
import numpy as np
import math

default_precision = 0.5/100

def BER(M, gamma):
    L = np.sqrt(M)
    k = 2 * (L - 1) / (np.log2(M) * L)
    gamma = np.power(10, gamma / 10)
    arg = np.sqrt(3 * np.log2(M) * gamma / (2*M - 2))
    return k * math.erfc(arg)

def search_ber_qam(target: float, constellation_size: int, precision = default_precision):
    lb = 0
    rb = 100
    mb = lb + (rb - lb) / 2
    delta = 1
    n = 0;

    while(abs(delta) > precision):
        n += 1
        mb = lb + (rb - lb)/2
        B = BER(constellation_size, mb)
        delta = (target - B) / B if B != 0 else 1e6 # Avoid division by infinity
        delta = min(delta, 1e6)
        # print("[{}] T: {} C: {:1.2e} \t({}%) \t({:1.2f} {:1.2f} {:1.2f})".format(n, target, B, int(100*delta), lb, mb, rb))

        if(delta > 0):
            rb = mb
        else:
            lb = mb

    return mb

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"Usage:\n{sys.argv[0]} constellation_size target_ber_base target_ber_power [epsilon]")
        print(f"\ni.e:\n{sys.argv[0]} 16 10 -6 returns the required Eb/No to achieve BER < 10^-6 on a 16 QAM system")
        exit()

    M     = int( sys.argv[1] )
    base  = int( sys.argv[2] )
    power = int( sys.argv[3] )
    
    if( len(sys.argv) == 5 ):
        default_precision = float(sys.argv[4])
    
    assert( default_precision < 1.0 )
    assert( M > 1 )
    assert( pow(base, power) > 0 )
    target = pow(base, power)
    gamma = search_ber_qam(target, M)
    print("Found BER = {:1.2e} at Eb/No = {:.2f} dB".format(BER(M, gamma), gamma))
