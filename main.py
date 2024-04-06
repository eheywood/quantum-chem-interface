from model.Circuit import Circuit
from model.QVM_cirq import QVM_cirq
from model.QVM_qiskit import QVM_qiskit
from model.IBM_Q_interface import IBM_Q

import yaml

def main():
    # print("test")

    test_circuit = Circuit('test','weber')

    file = open("model/simulations/qasm.txt", 'r')

    test_circuit.qiskit_load_from_qasm(file.read())

    config_file = open('config.yaml','r')
    config = yaml.safe_load(config_file)
    #virtualMachine = QVM_cirq(config=config['cirq-qvm'])
    #result = virtualMachine.run_circuit(test_circuit,False)
    
    #print(result)
    #virtualMachine = QVM_qiskit(config=config['qiskit-qvm'])
    #results = virtualMachine.run_circuit(test_circuit.get_qiskit_circuit())
    #print(results)
    
    token = "fc5d547283354d8a12af2179141f8ea4089cdca5fac9ad1cc89eacc03acab823664cdcc31b436a4f7c98a2f7aa11ae341989a55acf6a60d64e4439a4a89ad092"
    qm = IBM_Q(token)

    result = qm.verify_via_sim(test_circuit.get_qiskit_circuit())
    print(result)

    #job_id = qm.submit_job(test_circuit.get_qiskit_circuit())
    #print(job_id)
    #status = qm.check_job_status(job_id)
    #print(status)
    
if __name__ == '__main__':
	main()