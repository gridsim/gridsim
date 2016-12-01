"""
.. moduleauthor:: Dominique Gabioud <dominique.gabioud@hevs.ch>
.. moduleauthor:: Gillian Basso <gillian.basso@hevs.ch>
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

The :mod:`gridsim.cyberphysical` module implements the connection to real
devices for gridsim simulator.

Here is the class diagram of the cyber-physic package:

.. figure:: ./figures/model-cyberphysical.png
    :align: center
    :scale: 100 %

"""
from gridsim.simulation import Simulator
from .simulation import CyberPhysicalModule

Simulator.register_simulation_module(CyberPhysicalModule)
