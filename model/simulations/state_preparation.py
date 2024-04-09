import numpy as np
import cirq

### STATE PREPARATION for positive REAL values. Will not work with imaginary or negative values.

def calc_angle(s:int,j:int,amps:list) -> float:
    """ Calculates the angle to rotate, on a particular qubit and position.

    :param s: The qubit number, in reversing order. Eg if on q(0), input q(n)
    :type s: int
    :param j: The gate position for that qubit, again in reverse order. For example, if applying the first gate, input j as 2^(n-s) and decrease till 1.
    :type j: int
    :param amps: The desired amplitudes for the qubit states. 
    :type amps: list
    :return: The angle to rotate by.
    :rtype: float
    """
    
    numerator = 0
    #print("Calculating numerator...")
    for l in range(1, int(2 ** (s-1))+1):
        index = int(((2*j) - 1)*(2**(s-1)) + l) -1
        amp = np.abs(amps[index]) ** 2
        #print(l, ": ", amp)
        numerator += amp

    numerator = np.sqrt(numerator)
    #print("Numerator: ", numerator)
    
    denominator = 0
    #print("Calculating denom...")
    for l in range(1, int(2 ** s) +1):
        index = int((j - 1)*(2**s) + l) -1
        amp = np.abs(amps[index]) ** 2
        #print(l, ": ", amp)
        denominator += amp

    denominator = np.sqrt(denominator)
    #print("Denominator: ", denominator)
    return 2 * np.arcsin(numerator / denominator)

#def reverse_quibit_order(qubits) -> cirq.Moment:

def state_prep(amps:list,qubits:list) -> cirq.Moment:
    """_summary_

    :param amps: The probability distribution for qubit states. Must be in order from 000,001,...110,111.
    :type amps: list
    :param qubits: A list of the qubits to build the circuit with.
    :type qubits: list
    :raises Exception: Raised if the probability distribution does not add to 1.
    :return: The cirq.Moment that generates the correct state. Can be used at the beginning of a circuit.
    :rtype: cirq.Moment
    """
    ## amps must be in order from 000, 001, ... 110, 111
    ## take in prop distribution add up to 1
    ## must normalise by applying np.sqrt on all

    n = len(qubits)

    ## Ensure the probability distribution already addds to 1.
    if np.sum(amps) != 1:
        raise Exception("Probability distribution must add to 1")

    ## Square root all vals so the |amps|^2 adds to 1 as required for a quantum  machine.
    amps = np.sqrt(amps)
    print(amps)

    moment = []

    #Qubit index.
    q = 0

    for s in range(n,0,-1):

        ## For calculating the control values to put on qubits
        a = 1 

        for j in range(int(2**(n-s)),0,-1):

            #print("j: ", j)

            beta = calc_angle(s,j,amps)
            if np.isnan(beta):
                beta = 0

            if q == 0:
                #print("No controls")
                moment.append(cirq.Moment(cirq.Ry(rads=beta).on(qubits[q])))
            else:
                control_order = bin(2**(n-s) - a)[2:]
                int_control_order = [int(x) for x in control_order ]

                ## Ensuring that the control order is the correct length so the control conditions are correct.
                ## eg: 0 and 1 must become 00 and 01 if on qubit 3
                while len(int_control_order) != (2**(n-s-1)):
                    int_control_order = [0] + int_control_order

                #print("Controls: ", int_control_order)
                #print("Controlled by: ", qubits[:q])
                moment.append(cirq.Moment(cirq.Ry(rads=beta).on(qubits[q]).controlled_by(*qubits[:q],control_values=int_control_order)))
            a += 1
        q += 1

    return moment
                


if __name__ == '__main__':
    qubits = cirq.LineQubit.range(3)
    #a = [0,0.5,0.5,0]
    a = [0.2,0,0.5,0,0,0,0.2,0.1]
    moment = state_prep(a,qubits)
    print(cirq.Circuit(moment).to_text_diagram())
