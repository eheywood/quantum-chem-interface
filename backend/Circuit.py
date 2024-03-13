import cirq
from cirq.contrib.qasm_import import circuit_from_qasm, QasmException
import json
from qiskit import QuantumCircuit

class Circuit:

    qvm_hardware = None
    name = None
    __cirq_circuit = None
    __cirq_qubit_list = [] # List[cirq.Qubit]
    __qasm_circuit = None
    __qasm_circuit_string = None

    def __init__(self, name: str, QVM_hardware: str) -> None:
        """ Constructs the Circuit class

        :param name: Name of the circuit.
        :type name: str
        :param QVM_hardware: The name of the hardware teh QVM is simulating. If no QVM use a default of 'weber'
        :type QVM_hardware: str
        """
        
        self.qvm_hardware = QVM_hardware
        self.name = name
    
    ## SETTERS:
        
    def set_QVM_hardware(self, hardware: str):
        """ Sets the name of the hardware the QVM is simulating

        :param hardware: The name of the hardware being simulated
        :type hardware: str
        """
        self.qvm_hardware = hardware
    
    ## PRIVATE UPDATE CIRCUIT METHODS:
        
    def __update_cirq_circuit(self):
        """ Creates a Cirq circuit from the already existing qiskit circuit stored in the class
        """
        self.__cirq_circuit = circuit_from_qasm(self.__qasm_circuit_string)

    def __update_qasm_circuit(self):
        """ Creates a qasm circuit from the already existing cirq circuit stored in the class
        """

        # Not 100% support or finished from Cirq, use most basic quantum gates is possible, as the translating between these in Cirq and 
        # qasm is the most
        try:
            qasm_circuit = cirq.QasmOutput(self.__cirq_circuit,self.__cirq_qubit_list)
            qasm_filename = "../simulations/" + self.name + "_qasm.txt"
            qasm_circuit.save(qasm_filename)

            self.qasm_circuit = QuantumCircuit.from_qasm_file(qasm_filename)
        except QasmException: # TODO: better error handling?
            raise

    def __update_qubit_list(self):
        """ Updates the quibit list, is called if the circuit has been changed at any point.
        """

        self.__cirq_qubit_list = []
        for i in range(self.__cirq_circuit.all_qubits):
            self.__cirq_qubit_list.append(i)

    # TODO: def cirq_translate_circuit FOR 'device ready'


    ## LOADING CIRCUIT METHODS:
            
    def cirq_load_from_json(self, json_str: str):
        """ Loads a quantum circuit from a serialized cirq quantum circuit

        :param json_str: The string from the json file containing the circuit to be loaded
        :type json_str: str
        """

        self.cirq_circuit = cirq.read_json(json_text=json_str)


    def cirq_load_from_quirk_url(self, url: str):
        """ Loads a cirq circuit from a url that leads to a circuit in Quirk, a drag and drop online quantum circuit building tool

        :param url: The url leading to the desired Quirk circuit
        :type url: str
        """
        self.cirq_circuit = cirq.quirk_url_to_circuit(url)


    def qiskit_load_from_qasm(self, qasm_str: str):
        """ Loads in the quantum circuit from a file containing an Open QASM circuit

        :param qasm_str: The contents of the Open QASM circtuit
        :type qasm_str: str
        """

        self.__qasm_circuit_string = qasm_str
        self.__qasm_circuit = QuantumCircuit.from_qasm_str(qasm_str)


    ## GETTERS:
        
    def get_cirq_circuit(self) -> cirq.Circuit:
        """ Returns the quantum circuit 

        :return: The quantum circuit
        :rtype: cirq.Circuit
        """
        if self.__qasm_circuit != None and self.__cirq_circuit == None:
            self.__update_cirq_circuit()

        return self.__cirq_circuit

    def get_qasm_circuit(self):
        """ Return the quantum circuit. If null and the cirq version is not, updates the object to translate the cirq circuit to qasm

        :return: The quantum circuit
        :rtype: qiskit.QuantumCircuit
        """
        
        if self.__qasm_circuit == None and self.__cirq_circuit != None:
            self.__update_qasm_circuit()
        
        return self.qasm_circuit

    def get_circuit_str(self) -> str:
        """ Gets a displayable version of the circuit, ready to print

        :return: The circuit ready to be printed
        :rtype: str
        """

        if self.__cirq_circuit == None and self.__qasm_circuit_string != None:
            # translate qasm to cirq
            self.__update_cirq_circuit()
            self.__update_qubit_list()
        
        return self.cirq_circuit.to_text_diagram()



