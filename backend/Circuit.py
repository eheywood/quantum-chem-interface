import cirq
import json
from qiskit import QuantumCircuit

class Circuit:

    qvm_hardware = None
    name = None
    __cirq_circuit = None
    __cirq_qubit_map = None
    __qasm_circuit = None

    def __init__(self, name: str, QVM_hardware: str) -> None:
        """ Constructs the Circuit class

        :param name: Name of the circuit.
        :type name: str
        :param QVM_hardware: The name of the hardware teh QVM is simulating. If no QVM use a default of 'weber'
        :type QVM_hardware: str
        """

        
        self.qvm_hardware = QVM_hardware
        self.name = name
    
    def set_QVM_hardware(self, hardware: str):
        """ Sets the name of the hardware the QVM is simulating

        :param hardware: The name of the hardware being simulated
        :type hardware: str
        """
        self.qvm_hardware = hardware

    def __update_qasm_circuit(self):
        """ Creates a qasm circuit from the cirq circuit stored in the class
        """

        valid = True
        if valid:
            # TODO: add in checking validity as there is not 100% support between the two
            qasm_circuit = cirq.QasmOutput(self.cirq_circuit,self.cirq_qubit_map)
            qasm_filename = "../simulations/" + self.name + "_qasm.txt"
            qasm_circuit.save(qasm_filename)

            self.qasm_circuit = QuantumCircuit.from_qasm_file(qasm_filename)
        #else:
            #THROW SOME ERROR


    # TODO: def cirq_translate_circuit FOR 'device ready'

    # TODO: def cirq_load_from_json(file_str):

    def load_from_quirk_url(self, url: str):
        """ Loads a cirq circuit from a url that leads to a circuit in Quirk, a drag and drop online quantum circuit building tool

        :param url: The url leading to the desired Quirk circuit
        :type url: str
        """
        self.cirq_circuit = cirq.quirk_url_to_circuit(url)


    def get_cirq_circuit(self):
        """ Returns the quantum circuit 

        :return: The quantum circuit
        :rtype: cirq.Circuit
        """
        return self.cirq_circuit

    def get_qasm_circuit(self):
        """ Return the quantum circuit. If null and the cirq version is not, updates the object to translate the cirq circuit to qasm

        :return: The quantum circuit
        :rtype: qiskit.QuantumCircuit
        """
        
        if self.qasm_circuit == None and self.cirq_circuit != None:
            self.__update_qasm_circuit()
        
        # TODO: sort out error handling
        return self.qasm_circuit



