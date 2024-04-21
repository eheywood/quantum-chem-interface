## This python script will generate a quantum circuit (in cirq) that simulates the particle in a box problem depending on a few factors:

## Time steps T and time step size  (not sure if i need this bc it might be time independent)

## V(x) model of potential energy, In our case v simple , is 0 within the box, infinity everywhere else.

## L = the length of the space/box

## N = the number of times to split the space up into a grid.Turns it into a discrete quantized problem. 

## Number of quibits is dependent on number of times the space is split up. n = log2(N)

import cirq
import cirq.circuits
import cirq.sim
import cirq_google
import numpy as np 
from scipy.stats import norm
import math
from model.simulations.state_preparation import state_prep

def build_circuit(L:int, energy_lvl, time_step, num_of_iters,backend):
    
    moments = []

    # 1) generate waveFunc. Transform into an array representation of normalized probabilities.
    wave_func = p_in_box_wavefunc(energy_lvl,L)

    # 2) quantize grid space 2L into N. As assume box is from 0-L and > L is outside box. This is where we apply a 'penalty' on the potential energy, for being outside the box.

    N = int(2*L)

    # 3) n qubits = log2(N). Plus 1 bc of ancilliary
    n_qubits = int(np.log2(N)) + 1 
    qubits = cirq.LineQubit.range(n_qubits)

    box_amps = np.zeros((N))
    box_amps[0:L] = wave_func
    print(box_amps)

    #box_amps = [0,0.5,0.5,0,0,0,0,0]
    #state_prepared_moment = state_prep(box_amps,qubits)
    state_prepared_moment = state_prep(box_amps,qubits[1:],backend)

    initial_state_circuit = cirq.Circuit(state_prepared_moment,cirq.measure(*qubits[1:],key='meas'))
    
    moments.append(state_prepared_moment)
    # for each time step:
    for i in range(num_of_iters):

        # 4) Apply phase shift depending on highest order bit 
        #potential_moment = cirq.Moment(cirq.DiagonalGate(potential_energy_shifts).on(qubits[-1]))
        #potential_energy_shifts = [1000,1000] #multiply by time step means nothing here.
        
        potential_moment = cirq.Moment(cirq.rz(1.99*np.pi).on(qubits[len(qubits)-1]))
        moments.append(potential_moment)


        # 5) QFT all quibits
        qft_moment = QFT(qubits)
        #moments.append(qft_moment)
        moments.append(cirq.qft(*qubits[1:],without_reverse=True))

        # 6) Apply a diagonal phase shift to the quibits (controlled Z gate?). Depends on the computational basis.....? This simulates the kinetic energy operator
    
        # assume m = 0.5, h_bar = 0
        #momentum_moment = cirq.Moment(cirq.DiagonalGate(momentum_shifts).on(*qubits))
        #moments.append(momentum_moment)
        moments.append(build_momentum_moment(qubits,time_step))

        # 7) Inverse QFT
        inv_qft_moment = inv_QFT(qubits)
        #moments.append(inv_qft_moment)
        moments.append(cirq.qft(*qubits[1:],inverse=True,without_reverse=True))



    # Should result in a matrix of probabilities, all adding to 1 and representing different positions within the box.
    moments.append(cirq.measure(*qubits[1:],key='meas'))
    final_circuit = cirq.Circuit(moments)

    print(final_circuit.to_text_diagram())

    return final_circuit, initial_state_circuit

def build_momentum_moment(qubits,phi):
    """ Builds the cirq.Moment for the momentum operator.

    :param qubits: The list of qubits to apply it to
    :type qubits: list
    :param phi: The paramater to rotate the phase by
    :type phi: float
    :return: The moment containing the operator.    
    :rtype: cirq.Moment
    """

    moment = []
    n = len(qubits)

    mini_moment = []
    for j in range(n-1):
        mini_moment.append(cirq.rz(phi/(2**(j+n-4))).on(qubits[n -1 - j]))
    moment.append(cirq.Moment(mini_moment))

    phases = [phi * (2**(4-i-j)) for i in range(1,n) for j in range(i+1,n)]
    print("phases:", phases)

    count = 0
    for i in range(n-1,0,-1):
        for j in range(i-1,0,-1):
            ops = []
            ops.append(cirq.Moment(cirq.CNOT(qubits[j],qubits[0])))
            ops.append(cirq.Moment(cirq.CNOT(qubits[i],qubits[0])))
            ops.append(cirq.Moment(cirq.rz(phases[count]).on(qubits[0])))
            ops.append(cirq.Moment(cirq.CNOT(qubits[i],qubits[0])))
            ops.append(cirq.Moment(cirq.CNOT(qubits[j],qubits[0])))
            moment.append(ops)
            count += 1

    print(cirq.Circuit(moment).to_text_diagram())
    return moment


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

def p_in_box_wavefunc(energy_lvl,L):

    wave_func = np.zeros((L))
    for x in range(L):
        wave_func[x] = np.sqrt(2 / L) * np.sin((energy_lvl * np.pi * x)/L)

    return wave_func / sum(wave_func)


def QFT(qubits):
    moment = []
    for q in range(len(qubits)):
        moment.append(cirq.Moment(cirq.H(qubits[q])))
        count = 2
        for i in range(q+1,len(qubits)):
            rk = R_k(count)
            count +=1
            moment.append(cirq.Moment(cirq.ControlledGate(rk).on(qubits[i],qubits[q])))
    
    moment.append(reverse_qubit_order(qubits))

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

    moment.append(reverse_qubit_order(qubits))

    return moment

def reverse_qubit_order(qubits:list) -> cirq.Moment:
    """ Reverses the bit ordering.

    :param qubits: The qubits to apply this operation to.
    :type qubits: list
    :return: The moment of this operation
    :rtype: cirq.Moment
    """

    moment = []

    forward = 0
    backwards = len(qubits)-1

    while forward < backwards:
        moment.append(cirq.Moment(cirq.SWAP(qubits[forward],qubits[backwards])))
        forward += 1
        backwards -= 1
    
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
        super(R_k_inv, self)
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
    time_step = 0.1

    #circuit = build_circuit(4,1,0.1,1)

    qubits = cirq.LineQubit.range(5)
    qft_mom = QFT(qubits)
    inv_QFT_mom = inv_QFT(qubits)
    circuit = cirq.Circuit(qft_mom,inv_QFT_mom)
    print(circuit.to_text_diagram())

    print(p_in_box_wavefunc(1,8))


