import sys
sys.path.append('./model/simulations')
from model.Circuit import Circuit
from model.QVM_cirq import QVM
import ParticleInBoxSim
import state_preparation
import cirq
import matplotlib.pyplot as plt
import numpy as np

import model.simulations.ParticleInBoxSim


def main():
    print("test")

    #test_circuit = Circuit('test','weber')

    
    #file = open("simulations/qasm.txt", 'r')

    #test_circuit.qiskit_load_from_qasm(file.read())


    particle_circuit, initial_state_circuit  = ParticleInBoxSim.build_circuit(8,1,0.1,10)

    #circuit = cirq.Circuit(state_preparation.state_prep([0,0.5,0.5,0,0,0,0,0],qubits),cirq.measure(qubits))
    #print(circuit)

    #print(cirq.contrib.quirk.circuit_to_quirk_url(particle_circuit,prefer_unknown_gate_to_failure=True))
    virtualMachine = QVM(processor='rainbow',noisy=False)

    result1 = virtualMachine.run_circuit(initial_state_circuit,1000,True)
    fig,ax = plt.subplots(nrows=1,ncols =2)
    _ = cirq.plot_state_histogram(result1, ax[0])

    result1 = virtualMachine.run_circuit(particle_circuit,1000,True)
    _ = cirq.plot_state_histogram(result1, ax[1])
    plt.show()

    # result_1 = cirq.Simulator().compute_amplitudes(initial_state_circuit,range(8))
    # for i in range(len(result_1)):
    #       result_1[i] = (result_1[i].real**2) + (result_1[i].imag**2)
    # print("INITIAL: ", (result_1))

    
    # result_2 = cirq.Simulator().compute_amplitudes(particle_circuit,range(8))
    # for i in range(len(result_2)):
    #       result_2[i] = (result_2[i].real**2) + (result_2[i].imag**2)
    # print("FINAL: ", (result_2))

    
if __name__ == '__main__':
	main()