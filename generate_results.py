from model.simulations.ParticleInBoxSim import build_circuit
from model.Circuit import Circuit
from model.QVM_cirq import QVM_cirq
from model.QVM_qiskit import QVM_qiskit
from model.IBM_Q_interface import IBM_Q
import yaml
import matplotlib.pyplot as plt
import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

# TODO: re reun results for correct results

def main():

    L_arr = [4,8,16]
    energy_lvl = 1
    time_step_size = 0.1
    num_iters_arr = [1,5,10]
    noisy = "noise"
    backend = 'cirq'

    config_file = open('config.yaml','r')
    config = yaml.safe_load(config_file)
    
    virtualMachine = QVM_cirq(config=config['cirq-qvm'])

    for L in L_arr:
        for num_iters in num_iters_arr:

            particle_circuit, initial_state_circuit  = build_circuit(L,energy_lvl,time_step_size,num_iters,'cirq-QVM')

            circuit_name = backend + "_particle_L" + str(L) + "_e" + str(energy_lvl) + "_i" + str(num_iters)
            particleCircuit = Circuit(circuit_name)
            particleCircuit.set_cirq_circuit(particle_circuit)

            initial_name = backend +  "_initial_L" + str(L) + "_e" + str(energy_lvl) + noisy
            Circuit_initial = Circuit(initial_name)
            Circuit_initial.set_cirq_circuit(initial_state_circuit)
            

            result1 = virtualMachine.run_circuit(particleCircuit,False)
            print(result1)

            result2 = virtualMachine.run_circuit(Circuit_initial,False)
            print(result2)

            num_measures = int(np.log2(L) + 1)

            for i in range(2 ** num_measures):
                    bin_num = bin(i)[2:]

                    while len(bin_num) != len(bin((2 ** num_measures) -1)[2:]):
                        bin_num = '0' + bin_num
                    
                    count = result1.get(bin_num)
                    if count == None:
                        result1.update({i:0})
                    else:
                        result1.pop(bin_num,None)
                        result1.update({i:count})
                    
                    initial_count = result2.get(bin_num)
                    if initial_count == None:
                        result2.update({i:0})
                    else:
                        result2.pop(bin_num,None)
                        result2.update({i:initial_count})
                        
            print(result1)
            print(result2)
            fig,ax = plt.subplots()
            ax.bar(result1.keys(),result1.values())
            ax.set_xlabel("State")
            ax.set_ylabel("Counts")
            plt.savefig("./results/results_cirq_noise/" + circuit_name)

            fig1,ax1 = plt.subplots()
            ax1.bar(result2.keys(),result2.values())
            ax1.set_xlabel("State")
            ax1.set_ylabel("Counts")
            plt.savefig("./results/results_cirq_noise/" + initial_name)



def submit_IBMQ_job():

    L = 32
    energy_lvl = 1
    time_step_size = 0.1
    num_iters = 1
    #noisy = "noise"
    backend = 'IBMQ'

    config_file = open('config.yaml','r')
    config = yaml.safe_load(config_file)

    token_str = "fc5d547283354d8a12af2179141f8ea4089cdca5fac9ad1cc89eacc03acab823664cdcc31b436a4f7c98a2f7aa11ae341989a55acf6a60d64e4439a4a89ad092"
    qm = IBM_Q(token=token_str)
    
    particle_circuit, initial_state_circuit  = build_circuit(L,energy_lvl,time_step_size,num_iters,'qiskit-QVM')

    circuit_name = backend + "_particle_L" + str(L) + "_e" + str(energy_lvl) + "_i" + str(num_iters)
    particleCircuit = Circuit(circuit_name)
    particleCircuit.set_cirq_circuit(particle_circuit)

    initial_name = backend +  "_initial_L" + str(L) + "_e" + str(energy_lvl)
    Circuit_initial = Circuit(initial_name)
    Circuit_initial.set_cirq_circuit(initial_state_circuit)


    result1 = qm.verify_via_sim(particleCircuit)
    print(result1)

    num_measures = int(np.log2(L) + 1)

    for i in range(2 ** num_measures):
            bin_num = bin(i)[2:]

            while len(bin_num) != len(bin((2 ** num_measures) -1)[2:]):
                bin_num = '0' + bin_num
            
            count = result1.get(bin_num)
            if count == None:
                result1.update({i:0})
            else:
                result1.pop(bin_num,None)
                result1.update({i:count})
            

    print(result1)

    fig,ax = plt.subplots()
    ax.bar(result1.keys(),result1.values())
    ax.set_xlabel("State")
    ax.set_ylabel("Counts")
    plt.savefig("./results/results_IBM_Q/" + circuit_name)

    job_id = qm.submit_job(particleCircuit)
    print(job_id)
    status = qm.check_job_status(job_id)
    print(status)


if __name__ == '__main__':
	#main()
 
    #submit_IBMQ_job()
 
    #config_file = open('config.yaml','r')
    #config = yaml.safe_load(config_file)

    token_str = "fc5d547283354d8a12af2179141f8ea4089cdca5fac9ad1cc89eacc03acab823664cdcc31b436a4f7c98a2f7aa11ae341989a55acf6a60d64e4439a4a89ad092"

    qm = IBM_Q(token=token_str)
    job_id = 'crftgha7fdh0008f92t0'

    #service = QiskitRuntimeService(channel='ibm_quantum',instance='ibm-q/open/main',token=token_str)
    
    #job = service.job('crft3w7qzd5000885sh0')
    status = qm.check_job_status(job_id)
    complete, result1 = qm.get_results_from_job(job_id)
    print(result1)

    num_measures = int(np.log2(32) + 1)

    for i in range(2 ** num_measures):
            bin_num = bin(i)[2:]

            while len(bin_num) != len(bin((2 ** num_measures) -1)[2:]):
                bin_num = '0' + bin_num
            
            count = result1.get(bin_num)
            if count == None:
                result1.update({i:0})
            else:
                result1.pop(bin_num,None)
                result1.update({i:count})
            

    print(result1)

    circuit_name = 'IBMQ_particle_L32_e1_i10'
    fig,ax = plt.subplots()
    ax.bar(result1.keys(),result1.values())
    ax.set_xlabel("State")
    ax.set_ylabel("Counts")
    plt.savefig("./results/results_IBM_Q/" + circuit_name)

