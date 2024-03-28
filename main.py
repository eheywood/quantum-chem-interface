from model.Circuit import Circuit
from model.QVM_cirq import QVM
import view.arguments

def main():
    print("test")

    test_circuit = Circuit('test','weber')

    file = open("simulations/qasm.txt", 'r')

    test_circuit.qiskit_load_from_qasm(file.read())

    virtualMachine = QVM(processor='rainbow',noisy=False)
    result = virtualMachine.run_circuit(test_circuit,10,True)
    print(result)
    
if __name__ == '__main__':
	main()