import sys
sys.path.append('./model/simulations/')
from model.Circuit import Circuit
from model.simulations.ParticleInBoxSim import build_circuit
from model.QVM_cirq import QVM_cirq

import yaml

import cirq
import matplotlib.pyplot as plt
import numpy as np



def main():
    # print("test")

    #test_circuit = Circuit('test','weber')

    file = open("model/simulations/qasm.txt", 'r')

    test_circuit = Circuit("test",'weber')
    test_circuit.qiskit_load_from_qasm(file.read())

    config_file = open('config.yaml','r')
    config = yaml.safe_load(config_file)
    #virtualMachine = QVM_cirq(config=config['cirq-qvm'])
    #result = virtualMachine.run_circuit(test_circuit,False)
    
    #print(result)
    #virtualMachine = QVM_qiskit(config=config['qiskit-qvm'])
    #results = virtualMachine.run_circuit(test_circuit.get_qiskit_circuit())
    #print(results)
    
    #token = "fc5d547283354d8a12af2179141f8ea4089cdca5fac9ad1cc89eacc03acab823664cdcc31b436a4f7c98a2f7aa11ae341989a55acf6a60d64e4439a4a89ad092"
    #qm = IBM_Q(token)

    #result = qm.verify_via_sim(test_circuit.get_qiskit_circuit())
    #print(result)

    #job_id = qm.submit_job(test_circuit.get_qiskit_circuit())
    #print(job_id)
    #status = qm.check_job_status(job_id)
    #print(status)


    particle_circuit, initial_state_circuit  = build_circuit(8,1,0.1,1)

    virtualMachine = QVM_cirq(config=config['cirq-qvm'])

    result1 = virtualMachine.run_circuit(initial_state_circuit,True)
    fig,ax = plt.subplots(nrows=1,ncols =2)
    _ = cirq.plot_state_histogram(result1, ax[0])

    result1 = virtualMachine.run_circuit(particle_circuit,True)
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