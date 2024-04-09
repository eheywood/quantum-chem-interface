## This python script will generate a quantum circuit (in cirq) that simulates the particle in a box problem depending on a few factors:

## Time steps T and time step size  (not sure if i need this bc it might be time independent)

## V(x) model of potential energy, In our case v simple , is 0 within the box, infinity everywhere else.

## L = the length of the space/box

## N = the number of times to split the space up into a grid.Turns it into a discrete quantized problem. 

## Number of quibits is dependent on number of times the space is split up. n = log2(N)

import cirq
import cirq_google
import numpy as np 
from scipy.stats import norm
import math

def build_circuit(L:float,wave:str,N=8):
    n_qubits = np.log2(N)

    qubits = cirq.LineQubit.range(n_qubits)

    # 1) interpret waveFunc. Transform into an array representation of normalized probabilities.
    waveFunc = np.zeros((N))

    # 2) quantize grid space 2L into N. As assume box is from 0-L and > L is outside box. This is where we apply a 'penalty' on the potential energy, for being outside the box.
    # 3) n qubits = log2(N)
    
    # for each time step:?
        # for each position (eg |010> is position 2) need to make amplitude/value of it equivalent to the wavefunction 'value' at that point....

    # 4) QFT all quibits
    qft_moment = QFT(qubits)
    # 5) Apply a diagonal phase shift to the quibits (controlled Z gate?). Depends on the computational basis.....? This simulates the kinetic energy operator
    # 6) Inverse QFT
    inv_qft_moment = inv_QFT(qubits)
    # 7) Apply phase shift depending on potential energy... R gate??


    # Should result in a matrix of probabilities, all adding to 1 and representing different positions within the box.

#def interpret_wavefunc(wave,N):  
    #Takes the wavefunction and returns the initial states of the qubits that is required.
    
    #waveFunc = np.zeros((N))

    
def gaussian_wavefunc(mean,spread,N):
    """ Produces an array of values for a gaussian wavefunction

    :param mean: mean of the gaussian distrib.
    :type mean: float
    :param spread: the standard deviation of the gaussian wavefunction
    :type spread: float
    :param N: the number of points
    :type N: int
    :return: An array of amplitudes that will average to roughly one.
    :rtype: list
    """
    x = np.linspace(0,N-1, num=N)
    wave_func =norm.pdf(x,mean,spread)

    return wave_func

def rectangular_wavefunc(peak_mid,peak_length,N):
    """ Produces a rectangular wavefunction.

    :param peak_mid: The mid of the rectangular peak
    :type peak_mid: float
    :param peak_length: The length of the peak
    :type peak_length: int
    :param N: The number of positions in the wavefunction
    :type N: int
    :return: An array of the amplitudes for the wavefunction
    :rtype: list
    """
    peak_val = 1/peak_length
    print(peak_val)
    wave = np.zeros((N))

    if peak_length % 2 == 0:
        peak_mid == math.floor(peak_mid)
    
    print((peak_mid - (peak_length /2)))
    print((peak_mid + (peak_length /2)))

    for i in range(N):
        print(i)
        if i >= (peak_mid - (peak_length /2)) and i <= (peak_mid + (peak_length /2)):
            wave[i] = peak_val
    
    return wave

        

# TODO: def phaseShift -> for momentum operator as well as 

def QFT(qubits):
    moment = []
    for q in range(len(qubits)):
        moment.append(cirq.Moment(cirq.H(qubits[q])))
        count = 2
        for i in range(q+1,len(qubits)):
            rk = R_k(count)
            count +=1
            moment.append(cirq.Moment(cirq.ControlledGate(rk).on(qubits[i],qubits[q])))

    return moment

def inv_QFT(qubits):
    moment = []
    for q in range(len(qubits)-1,-1,-1):
        count = len(qubits) - q
        for i in range(len(qubits)-1,q,-1):
            print(count)
            rk = R_k_inv(count)
            count -=1
            moment.append(cirq.Moment(cirq.ControlledGate(rk).on(qubits[i],qubits[q])))
        print('H')
        moment.append(cirq.Moment(cirq.H(qubits[q])))
    return moment


## Custom gates to perform the unitary transform required for the QFT
class R_k(cirq.Gate):
    def __init__(self,k):
        super(R_k, self)
        self.k = k

    def _num_qubits_(self):
        return 1

    def _unitary_(self):
        return np.array([
            [1.0,  0],
            [0, (np.e **((2 * np.pi * 1.j)/2**self.k))]
        ])

    def _circuit_diagram_info_(self, args):
        return "R_" + str(self.k)
    

class R_k_inv(cirq.Gate):
    def __init__(self,k):
        super(R_k, self)
        self.k = k

    def _num_qubits_(self):
        return 1

    def _unitary_(self):
        return np.array([
            [1.0,  0],
            [0, -(np.e **((2 * np.pi * 1.j)/2**self.k))]
        ])

    def _circuit_diagram_info_(self, args):
        return "R_" + str(self.k) + "^+"
    
if __name__ == '__main__':
    qubits = cirq.LineQubit.range(3)
    #a = [0,0.5,0.5,0]
    #a = [0.2,0,0.5,0,0,0,0.2,0.1]
    #moment = state_prep(a,qubits)
    #print(cirq.Circuit(moment).to_text_diagram())

    N = 8
    mean = 3
    width = 5

    wave = rectangular_wavefunc(mean,width,N)
    print(wave)
    print(sum(wave))



