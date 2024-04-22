from model.simulations.ParticleInBoxSim import build_circuit
from model.Circuit import Circuit
from model.QVM_cirq import QVM_cirq
from model.QVM_qiskit import QVM_qiskit
from model.IBM_Q_interface import IBM_Q
import yaml
import matplotlib.pyplot as plt
import matplotlib
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
    exactMachine = QVM_cirq()

    for L in L_arr:
        initial_state_dict = None
        x_labels = []
        iters = len(num_iters_arr)

        y_all_noise_labels = np.zeros((iters+1),dtype=object)
        y_diff_noise_labels = np.zeros((iters),dtype=object)

        y_all_labels = np.zeros((iters+1),dtype=object)
        y_diff_labels = np.zeros((iters),dtype=object)

        entire_amp_values = np.zeros((iters+1,L*2))
        diff_amp_values = np.zeros((iters,L*2))

        entire_amp_values_noisy = np.zeros((iters+1,L*2))
        diff_amp_values_noisy = np.zeros((iters,L*2))


        counter = 1
        for num_iters in num_iters_arr:                 
            particle_circuit, initial_state_circuit  = build_circuit(L,energy_lvl,time_step_size,num_iters,'cirq-QVM')

            ## Build Circuit
            circuit_name = backend + "_particle_L" + str(L) + "_e" + str(energy_lvl) + "_i" + str(num_iters)
            particleCircuit = Circuit(circuit_name)
            particleCircuit.set_cirq_circuit(particle_circuit)

            initial_name = backend +  "_initial_L" + str(L) + "_e" + str(energy_lvl)
            Circuit_initial = Circuit(initial_name)
            Circuit_initial.set_cirq_circuit(initial_state_circuit)
            

            noisy_result1 = virtualMachine.run_circuit(particleCircuit,False)

            noisy_result2 = virtualMachine.run_circuit(Circuit_initial,False)

            exact_result1 = exactMachine.run_circuit(particleCircuit,False)

            exact_result2 = exactMachine.run_circuit(Circuit_initial,False)

            num_measures = int(np.log2(L) + 1)

            for i in range(2 ** num_measures):
                    bin_num = bin(i)[2:]

                    while len(bin_num) != len(bin((2 ** num_measures) -1)[2:]):
                        bin_num = '0' + bin_num
                    
                    count = noisy_result1.get(bin_num)
                    if count == None:
                        noisy_result1.update({i:0})
                    else:
                        noisy_result1.pop(bin_num,None)
                        noisy_result1.update({i:count})
                    
                    initial_count = noisy_result2.get(bin_num)
                    if initial_count == None:
                        noisy_result2.update({i:0})
                    else:
                        noisy_result2.pop(bin_num,None)
                        noisy_result2.update({i:initial_count})

                    count = exact_result1.get(bin_num)
                    if count == None:
                        exact_result1.update({i:0})
                    else:
                        exact_result1.pop(bin_num,None)
                        exact_result1.update({i:count})
                    
                    initial_count = exact_result2.get(bin_num)
                    if initial_count == None:
                        exact_result2.update({i:0})
                    else:
                        exact_result2.pop(bin_num,None)
                        exact_result2.update({i:initial_count})

            noisy_result2 = dict(sorted(noisy_result2.items()))
            noisy_result1 = dict(sorted(noisy_result1.items()))
            exact_result2 = dict(sorted(exact_result2.items()))
            exact_result1 = dict(sorted(exact_result1.items()))

           
            print("noisy initial: " ,noisy_result2)     
            print("noisy: " ,noisy_result1)
            print("exact initial: ", exact_result2)
            print("exact: ", exact_result1)


            if num_iters == 1:
                initial_state_dict = exact_result2
                x_labels =list(initial_state_dict.keys())
                print(x_labels)
                entire_amp_values[0] = np.array(list(initial_state_dict.values())) / sum(list(initial_state_dict.values()))

                entire_amp_values_noisy[0] = np.array(list(initial_state_dict.values())) / sum(list(initial_state_dict.values()))

                y_all_labels[0] = "0"
                y_all_noise_labels[0] = "0"
            
            entire_amp_values[counter] = np.array(list(exact_result1.values())) / sum(list(exact_result1.values()))
            y_all_labels[counter] = str(num_iters)

            entire_amp_values_noisy[counter] = np.array(list(noisy_result1.values())) / sum(list(noisy_result1.values()))
            y_all_noise_labels[counter] = str(num_iters)

            diff_amp_values[(counter-1)] = entire_amp_values[counter] - entire_amp_values[0]
            y_diff_labels[(counter-1)] = str(num_iters)

            diff_amp_values_noisy[(counter-1)] = entire_amp_values_noisy[counter] - entire_amp_values_noisy[0]
            y_diff_noise_labels[(counter-1)] = str(num_iters)
            
            fig,ax = plt.subplots()
            ax.bar(noisy_result1.keys(),noisy_result1.values())
            ax.set_xlabel("State")
            ax.set_ylabel("Counts")
            plt.savefig("./results/results_cirq_noise/" + circuit_name)

            fig1,ax1 = plt.subplots()
            ax1.bar(noisy_result2.keys(),noisy_result2.values())
            ax1.set_xlabel("State")
            ax1.set_ylabel("Counts")
            plt.savefig("./results/results_cirq_noise/" + initial_name)

            fig,ax = plt.subplots()
            ax.bar(exact_result1.keys(),exact_result1.values())
            ax.set_xlabel("State")
            ax.set_ylabel("Counts")
            plt.savefig("./results/results_cirq_no_noise/" + circuit_name)

            fig1,ax1 = plt.subplots()
            ax1.bar(exact_result2.keys(),exact_result2.values())
            ax1.set_xlabel("State")
            ax1.set_ylabel("Counts")
            plt.savefig("./results/results_cirq_no_noise/" + initial_name)

            counter += 1

        fig,ax = plt.subplots(nrows=1,ncols=1)
        im = ax.imshow(entire_amp_values, cmap='Greens')
        ax.set_xticks(np.arange(len(x_labels)), labels = x_labels)
        ax.set_yticks(np.arange(len(y_all_labels)), labels = y_all_labels)
        cbar = ax.figure.colorbar(im, ax = ax,orientation='horizontal')
        cbar.set_label("Amplitude")
        ax.set_ylabel("Number of iterations")
        ax.set_xlabel("State")

        for i in range(len(x_labels)):
            for j in range(len(y_all_labels)):
                print(j,i,entire_amp_values[j,i])
                text = im.axes.text(i,j, round(entire_amp_values[j, i], 3),
                            ha = "center", va = "center", color = "w")

        plt.title("L:" + str(L) + " exact simulation amplitudes")
        file_name = "L" + str(L) + "_amplitudes_table"
        plt.savefig("./results/results_cirq_no_noise/" + file_name)

        fig,ax = plt.subplots(nrows=1,ncols=1)
        im = ax.imshow(entire_amp_values_noisy, cmap='Greens')
        ax.set_xticks(np.arange(len(x_labels)), labels = x_labels)
        ax.set_yticks(np.arange(len(y_all_noise_labels)), labels = y_all_noise_labels)
        cbar = ax.figure.colorbar(im, ax = ax,orientation='horizontal')
        cbar.set_label("Amplitude")
        ax.set_ylabel("Number of iterations")
        ax.set_xlabel("State")


        for i in range(len(x_labels)):
            for j in range(len(y_all_noise_labels)):
                print(j,i,entire_amp_values_noisy[j,i])
                text = im.axes.text(i,j, round(entire_amp_values_noisy[j, i], 3),
                            ha = "center", va = "center", color = "w")
                
        plt.title("L:" + str(L) + " noisy simulation amplitudes")
        file_name = "L" + str(L) + "_amplitudes_table"
        plt.savefig("./results/results_cirq_noise/" + file_name)


        fig,ax = plt.subplots(nrows=1,ncols=1)
        im2 = ax.imshow(diff_amp_values, cmap='RdBu')
        ax.set_xticks(np.arange(len(x_labels)), labels = x_labels)
        ax.set_yticks(np.arange(len(y_diff_labels)), labels = y_diff_labels)
        cbar = ax.figure.colorbar(im2, ax = ax,orientation='horizontal')
        cbar.set_label("Difference to expected amplitude")
        ax.set_ylabel("Number of iterations")
        ax.set_xlabel("State")


        for i in range(len(x_labels)):
            for j in range(len(y_diff_labels)):
                print(j,i,diff_amp_values[j,i])
                text = im2.axes.text(i, j, round(diff_amp_values[j, i], 3),
                            ha = "center", va = "center", color = "w")
        
        plt.title("L:" + str(L) + " exact simulation differences")
        file_name = "L" + str(L) + "_differences_table"
        plt.savefig("./results/results_cirq_no_noise/" + file_name)

        fig,ax = plt.subplots(nrows=1,ncols=1)
        im2 = ax.imshow(diff_amp_values_noisy, cmap='RdBu')
        ax.set_xticks(np.arange(len(x_labels)), labels = x_labels)
        ax.set_yticks(np.arange(len(y_diff_noise_labels)), labels = y_diff_noise_labels)
        cbar = ax.figure.colorbar(im2, ax = ax,orientation='horizontal')
        cbar.set_label("Difference to expected amplitude",)
        ax.set_ylabel("Number of iterations")
        ax.set_xlabel("State")


        for i in range(len(x_labels)):
            for j in range(len(y_diff_noise_labels)):
                print(j,i,diff_amp_values_noisy[j,i])
                text = im2.axes.text(i, j, round(diff_amp_values_noisy[j, i], 3),
                            ha = "center", va = "center", color = "w")
        plt.title("L:" + str(L) + " noisy simulation differences")
        file_name = "L" + str(L) + "_differences_table"
        plt.savefig("./results/results_cirq_noise/" + file_name)
        
        plt.show()

# plt.show()


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
    qm = IBM_Q(token=token_str, config=config)
    
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
	main()
 
    #submit_IBMQ_job()
 
    #config_file = open('config.yaml','r')
    #config = yaml.safe_load(config_file)

def IBM_Q_Get_results():
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

