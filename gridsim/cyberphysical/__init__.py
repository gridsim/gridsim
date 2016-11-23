"""
.. moduleauthor:: Gillian Basso <gillian.basso@hevs.ch>

The :mod:`gridsim.cyberphysic` module implements the connection to real
devices for gridsim simulator.

Here is the class diagram of the cyber-physic package:

.. figure:: ./figures/model-electrical.png
    :align: center
    :scale: 100 %

"""
from gridsim.simulation import Simulator
from .simulation import CyberPhysicalModule

Simulator.register_simulation_module(CyberPhysicalModule)
