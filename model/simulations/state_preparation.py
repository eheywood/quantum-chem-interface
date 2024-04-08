import numpy as np
import cirq

def calculate_angles(a):
    
    n = np.log2(len(a))
    angles = np.zeros((n,2**(n-1)))
    
    K = np.linspace(1,n,n,dtype=int)

    for k in K:
        print("k: ", k)
        stop = int(2 ** (n-k))
        J = np.linspace(1,stop,stop,dtype=int)
        for j in J:
            print("j: ", j)
            numerator = 0
            for l in range(int(2 ** (k-1))):
                index = int(((2*j)-1)*(2**(k-1))+l) -1
                numerator += (a[index] ** 2)

            denominator = 0
            for l in range(int(2 ** k)):
                index = int((j-1)*(2**k)+l) - 1
                denominator += (a[index] ** 2)

            frac = np.sqrt(numerator) / np.sqrt(denominator)

            print(2 * np.arcsin(frac))
            angles[k-1][j-1] = 2 * np.arcsin(frac)
            
    return angles

def state_prep(amps) -> cirq.Moment:
    ## amps must be in order from 000, 001, ... 110, 111

    angles = calculate_angles(a)