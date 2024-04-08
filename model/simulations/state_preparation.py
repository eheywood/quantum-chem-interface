import numpy as np
import cirq

def calc_angle(s,j,amps):
    
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

def state_prep(amps,qubits) -> cirq.Moment:
    ## amps must be in order from 000, 001, ... 110, 111
    ## take in prop distrib- add up to 1
    ## must normalise by applying np.sqrt on all

    n = len(qubits)

    ## Normalise amps
    if np.sum(amps) != 1:
        raise Exception("Probability distribution must add to 1")

    amps = np.sqrt(amps)
    print(amps)

    moment = []
    for s in range(n):
        j = 1
        for j in range(int(2**(n-s)),0,-1):
            # no control qubit:
            beta = calc_angle(s,j,amps)
            if beta.isnan():
                beta = 0
            if s == 1:
                moment.append(cirq.Moment(cirq.Ry(rads=beta).on(qubits[s])))
            else:
                control_order = list(bin(2**(n-s) - j + 1))[2:]
                moment.append(cirq.Moment(cirq.Ry(rads=beta).on(qubits[s]).controlled_by(qubits[1])))
            j += 1

    return moment
                


if __name__ == '__main__':
    qubits = cirq.LineQubit.range(2)
    a = [0,0.5,0.5,0]
    moment = state_prep(a,qubits)
    print(cirq.Circuit(moment).to_text_diagram())