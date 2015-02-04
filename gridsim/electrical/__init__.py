"""
.. moduleauthor:: Gilbert Maitre <gilbert.maitre@hevs.ch>

The :mod:`gridsim.electrical` module implements the electrical part of the
gridsim simulator. It basically manages Consuming-Producing-Storing (CPS)
Elements, which consume (positive sign) and/or produce (negative sign) a
certain amount of energy (``delta_energy``) at each simulation step.

CPS elements may be attach to buses of an electrical power network, which is
also made of branches as connections between buses.

*Example*:

.. literalinclude:: ../../demo/loadflow.py
    :linenos:

shows a pure electrical example made of a reference 5-bus network
(see e.g. Xi-Fan Wang, Yonghua Song, Malcolm Irving, Modern power systems
analysis), to the non-slack buses of which are attached 4 CPS elements :
1 with constant power, production, 3 with random gaussian distributed power
consumption.

Here is the class diagram of the electrical package:

.. figure:: ./figures/model-electrical.png
    :align: center
    :scale: 100 %

"""
from gridsim.simulation import Simulator
from .simulation import ElectricalSimulator

Simulator.register_simulation_module(ElectricalSimulator)