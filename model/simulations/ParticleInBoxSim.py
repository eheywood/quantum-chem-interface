## This python script will generate a quantum circuit (in cirq) that simulates the particle in a box problem depending on a few factors:

## Time steps T and time step size  (not sure if i need this bc it might be time independent)

## V(x) model of potential energy, In our case v simple , is 0 within the box, infinity everywhere else.

## L = the length of the space/box

## N = the number of times to split the space up into a grid.Turns it into a discrete quantized problem. 

## Number of quibits is dependent on number of times the space is split up. n = log2(N)

import cirq
import cirq_google
import qsimcirq
import numpy as np 

# TODO: def build_circuit(L:float,N=8:int,wave:str):
    #n_quibits = math,log2(N)

    ## 1) interpret waveFunc
    ## 2) quantise grid space L into N 
    ## 3) n qubits = log2(N)
    
    ## for each time step:
        ## for each position?

    ## 4) Apply hadamarad to all qubits to put it into superposiiton
    ## 5) QFT all quibits
    ## 6) Apply a diagonal phase shift to the quibits (controlled Z gate?). Depends on the computational basis.....? This simulates the kinetic energy operator
    ## 7) Inverse QFT
    ## 8) Apply phase shift depending on potential energy... R gate??

    ## 9) apply hadamarad gates again? measure 'in the computational basis'

    ## Should result in prob\bilities - for each position??

    #return cirq.Circuit()


# TODO: def interpret_wavefunc():  Takes the wavefunction and returns the initial states of the qubits that is required.

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

# TODO: def phaseShift -> for momentum operator as well as 


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
    



