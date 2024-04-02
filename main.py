from model.Circuit import Circuit
from model.QVM_cirq import QVM
import yaml

def main():
    print("test")

    test_circuit = Circuit('test','weber')

    file = open("model/simulations/qasm.txt", 'r')

    test_circuit.qiskit_load_from_qasm(file.read())

    config_file = open('config.yaml','r')
    config = yaml.safe_load(config_file)
    virtualMachine = QVM(config=config['cirq-qvm'])
    result = virtualMachine.run_circuit(test_circuit,False)
    print(result)
    
if __name__ == '__main__':
	main()