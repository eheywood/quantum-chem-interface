import abc
import Circuit

class QVM(abc.ABC):

    @abc.abstractmethod
    def run_circuit(self,circuit:Circuit,optimised:bool) -> dict:
        pass

    @abc.abstractmethod
    def construct_default_QVM(self):
        pass
    
    @abc.abstractmethod
    def update_config(self,config:dict):
        pass
    

