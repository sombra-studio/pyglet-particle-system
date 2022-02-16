from dataclasses import dataclass
from numpy import ndarray


@dataclass
class State:
    """
    A physical state that defines a particle.

    Attributes:
        pos(ndarray): The position in space
        v(ndarray): Velocity at the current state
        m(float): Mass of the particle at the current state
    """
    pos: ndarray
    v: ndarray
    m: float
