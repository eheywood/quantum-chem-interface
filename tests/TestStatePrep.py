import unittest
import cirq
import sys
sys.path.append('../')
from model.simulations import state_preparation
from model.Circuit import Circuit
from model.QVM_cirq import QVM_cirq

from qiskit.primitives import Sampler

class TestStatePrepCirq(unittest.TestCase):

    def test_1_qubit(self):
        amps = [1,0]
        qubits = cirq.LineQubit.range(1)
        state_prep = cirq.Circuit(state_preparation.state_prep(amps,qubits,'cirq'),cirq.measure(*qubits, key='meas'))

        result = cirq.Simulator().run(state_prep, repetitions=1000)

        self.assertEqual(result.histogram(key='meas'), {0:1000})

    def test_2_qubit_1(self):
        amps = [0,0,1,0]
        qubits = cirq.LineQubit.range(2)
        state_prep = cirq.Circuit(state_preparation.state_prep(amps,qubits,'cirq'),cirq.measure(*qubits, key='measure_all'))
        
        result = cirq.Simulator().run(state_prep, repetitions=1000)
        print(result.histogram(key='measure_all'))

        self.assertEqual(result.histogram(key='measure_all'), {2:1000})

    def test_2_qubit_2(self):
        amps = [0.5,0,0,0.5]
        qubits = cirq.LineQubit.range(2)
        state_prep = cirq.Circuit(state_preparation.state_prep(amps,qubits,'cirq'),cirq.measure(*qubits, key='measure_all'))
        
        result = cirq.Simulator().run(state_prep, repetitions=1000)

        histogram = result.histogram(key='measure_all')
        histogram[0] = round(histogram[0],-2)
        histogram[3]= round(histogram[3],-2)

        self.assertEqual(histogram, {0:500,3:500})
    
    def test_3_qubit_1(self):
        amps = [0,0.5,0.5,0,0,0,0,0]
        qubits = cirq.LineQubit.range(3)
        state_prep = cirq.Circuit(state_preparation.state_prep(amps,qubits,'cirq'),cirq.measure(*qubits, key='measure_all'))
        
        result = cirq.Simulator().run(state_prep, repetitions=1000)

        histogram = result.histogram(key='measure_all')
        histogram[1] = round(histogram[1],-2)
        histogram[2]= round(histogram[2],-2)

        self.assertEqual(histogram, {1:500,2:500})
    
    def test_3_qubit_2(self):
        amps = [0,0.25,0.25,0.5,0,0,0,0]
        qubits = cirq.LineQubit.range(3)
        state_prep = cirq.Circuit(state_preparation.state_prep(amps,qubits,'cirq'),cirq.measure(*qubits, key='measure_all'))
        
        result = cirq.Simulator().run(state_prep, repetitions=1000)

        histogram = result.histogram(key='measure_all')

        self.assertAlmostEqual(histogram[1], 250, places=-2)
        self.assertAlmostEqual(histogram[2], 250, places=-2)
        self.assertAlmostEqual(histogram[3], 500, places=-2)

class TestStatePrepQiskit(unittest.TestCase):

    def test_1_qubit(self):
        amps = [1,0]
        qubits = cirq.LineQubit.range(1)
        state_prep = cirq.Circuit(state_preparation.state_prep(amps,qubits,'qiskit'),cirq.measure(*qubits, key='meas'))

        state_prep_circuit = Circuit('state_prep_test_1_1','weber')
        state_prep_circuit.set_cirq_circuit(state_prep)

        job = Sampler().run(state_prep_circuit.get_qiskit_circuit())
        result = job.result()

        self.assertEqual(result.quasi_dists[0], {0:1})
    

    def test_2_qubit_1(self):
        amps = [1,0,0,0]
        qubits = cirq.LineQubit.range(2)
        state_prep = cirq.Circuit(state_preparation.state_prep(amps,qubits,'qiskit'),cirq.measure(*qubits, key='meas'))

        state_prep_circuit = Circuit('state_prep_test_2_1','weber')
        state_prep_circuit.set_cirq_circuit(state_prep)

        job = Sampler().run(state_prep_circuit.get_qiskit_circuit())
        result = job.result()

        self.assertEqual(result.quasi_dists[0], {0:1})
    
    def test_2_qubit_2(self):
        amps = [0.5,0,0,0.5]

        qubits = cirq.LineQubit.range(2)
        state_prep = cirq.Circuit(state_preparation.state_prep(amps,qubits,'qiskit'),cirq.measure(*qubits, key='meas'))

        state_prep_circuit = Circuit('state_prep_test_2_2','weber')
        state_prep_circuit.set_cirq_circuit(state_prep)

        job = Sampler().run(state_prep_circuit.get_qiskit_circuit())
        histogram = job.result().quasi_dists[0]

        self.assertAlmostEqual(histogram[0], 0.5, places=2)
        self.assertAlmostEqual(histogram[3], 0.5, places=2)

    def test_3_qubit_1(self):
        amps = [0,0.5,0.5,0,0,0,0,0]
        qubits = cirq.LineQubit.range(3)
        state_prep = cirq.Circuit(state_preparation.state_prep(amps,qubits,'qiskit'),cirq.measure(*qubits, key='measure_all'))

        state_prep_circuit = Circuit('state_prep_test_3_1','weber')
        state_prep_circuit.set_cirq_circuit(state_prep)

        job = Sampler().run(state_prep_circuit.get_qiskit_circuit())
        histogram = job.result().quasi_dists[0]

        self.assertAlmostEqual(histogram[1], 0.5, places=2)
        self.assertAlmostEqual(histogram[2], 0.5, places=2)
    
    def test_3_qubit_2(self):
        amps = [0,0.25,0.25,0.5,0,0,0,0]
        qubits = cirq.LineQubit.range(3)
        state_prep = cirq.Circuit(state_preparation.state_prep(amps,qubits,'qiskit'),cirq.measure(*qubits, key='measure_all'))

        state_prep_circuit = Circuit('state_prep_test_3_2','weber')
        state_prep_circuit.set_cirq_circuit(state_prep)

        job = Sampler().run(state_prep_circuit.get_qiskit_circuit())
        histogram = job.result().quasi_dists[0]
        print(histogram)

        self.assertAlmostEqual(histogram[1], 0.25, places=2)
        self.assertAlmostEqual(histogram[2], 0.25, places=2)
        self.assertAlmostEqual(histogram[3], 0.5, places=2)
        









