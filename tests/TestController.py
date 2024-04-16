import unittest
import cirq
import sys
sys.path.append('../')
from model.simulations import state_preparation
from model.Circuit import Circuit
from model.QVM_cirq import QVM_cirq

from qiskit.primitives import Sampler

class TestController(unittest.TestCase):
    
    def menu_test():
        print('test')