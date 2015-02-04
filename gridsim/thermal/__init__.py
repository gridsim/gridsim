"""
The thermal simulation module offers a very abstract thermal simulation. The
simulation is based on the thermal capacity of a thermal process (envelope)
and the energy flows between those processes via thermal couplings that result
as consequence of the temperature differences between the thermal processes and
the thermal conductivity of the couplings between them.

*Example*:

.. literalinclude:: ../../demo/thermal.py
    :linenos:

* On line 11 we create a new simulation.
* On lines 22 to 35 we create a very simple thermal process with one room and
  the outside temperature from a data file.
* On line 38 we create a plot recorder and on line 39 we record all temperatures
  using the plot recorder.
* On line 44 & 45 we initialize the simulation and start the simulation for the
  month avril with a resolution of 1 hour.
* On linea 51 to 53 we save the data in several formats.

The figure looks like this one:

.. figure:: ../../demo/output/thermal-example.png
            :align: center

Here is the class diagram of the thermal package:

.. figure:: ./figures/model-thermal.png
    :align: center
    :scale: 100 %

"""

from gridsim.simulation import Simulator
from .simulation import ThermalSimulator

Simulator.register_simulation_module(ThermalSimulator)
