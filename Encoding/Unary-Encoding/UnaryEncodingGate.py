from qiskit import QuantumRegister
from qiskit.circuit import Gate
from qiskit.extensions.standard.x import CnotGate, XGate
from qiskit.extensions.standard.ry import CryGate
from Preprocessing.Classical_boolean_tests import is_stochastic_vector
from Visualization.Gate_visualization_tools import format_angle
from AbstractGates.qiwiGate import qiwiGate
import numpy as np


        
def unary_encoding_angles(distribution): #ADD THE POSSIBILITY TO HAVE AN ODD N
    distribution = np.array(distribution)
    n = len(distribution)
    if is_stochastic_vector(distribution) == True and n % 2 == 0:        
        angles = []        
        for i in range(n - 1):
            i = i + 1
            if i < n / 2:
                angles.append(2 * np.arctan2(np.sqrt(np.sum(distribution[0:i])), np.sqrt(distribution[i])))   
            elif i == n / 2 :
                middle = int(n / 2)
                angles.append(2 * np.arctan2(np.sqrt(1 - np.sum(distribution[middle:n])), np.sqrt(np.sum(distribution[middle:n]))))
            else : 
                angles.append(2 * np.arctan2(np.sqrt(np.sum(distribution[i:n])), np.sqrt(distribution[i - 1])))
        return angles
    else :
        raise NameError("The input vector is not a probability distribution or its dimension is not a multiple of 2.")


class PartialSwapGate(Gate):
    """Partial Swap (PS) gate. """
    
    def __init__(self, angle):
        self.angle = angle
        super().__init__(name=f"PartialSwap(" + format_angle(angle, 10**(-3), 10) + ")", num_qubits=2, params=[])
    
    def _define(self):
        definition = []
        q = QuantumRegister(2)
        rule = [
                (CnotGate(), [q[1], q[0]], []),
                (CryGate(-self.angle), [q[0], q[1]], []),
                (CnotGate(), [q[1], q[0]], [])
                ]
        for inst in rule:
            definition.append(inst)
        self.definition = definition
        

class UnaryEncodingGate(qiwiGate):
    """Unary Encoding gate. """
    
    def __init__(self, distribution, least_significant_bit_first=True):
        self.num_qubits = len(distribution)
        self.least_significant_bit_first = least_significant_bit_first
        self.distribution = distribution
        super().__init__(name=f"Unary Encoding", num_qubits=len(distribution), params=[], least_significant_bit_first = least_significant_bit_first)
    
    def _define(self):
            definition = []
            distribution_qubits = QuantumRegister(self.num_qubits)
            theta = unary_encoding_angles(self.distribution)
            middle = int(self.num_qubits / 2)
            if self.least_significant_bit_first:
                distribution_qubits = distribution_qubits[::-1]
            definition.append((XGate(), [distribution_qubits[middle]], []))
            definition.append((PartialSwapGate(theta[middle - 1]), [distribution_qubits[middle - 1], distribution_qubits[middle]], []))
            for step in range(middle - 1):
                step = step + 1
                definition.append((PartialSwapGate(theta[middle - 1 - step]), [distribution_qubits[middle - 1 - step], distribution_qubits[middle - step]], []))
                definition.append((PartialSwapGate(-theta[middle - 1 + step]), [distribution_qubits[middle - 1 + step], distribution_qubits[middle + step]], []))
            if self.least_significant_bit_first:
                distribution_qubits = distribution_qubits[::-1]
            self.definition = definition