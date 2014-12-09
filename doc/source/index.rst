.. _intro-ref:

#####################
The Gridsim simulator
#####################

.. figure:: ./figures/logo.png
            :align: center

****************
Table of Content
****************

This documentation is separated into four parts:

.. toctree::
    :numbered:
    :titlesonly:

    overview.rst
    documentation.rst
    core.rst
    tools.rst
    unit.rst
    io.rst
    copyright.rst

*********************
Context and objective
*********************
The energy world is quite complex: energy is moved, stored and transformed using
a heterogeneous and vastly distributed infrastructure. The move towards a
cleaner and more sustainable energy system, which is favoured by people, has
major implications on the energy system. Large controllable plants will be
replaced by small distributed units featuring most of the time a stochastic
behaviour. To accommodate these changes, the energy system as a whole must
become more flexible.
Many processes like building heating or cooling feature some level of
flexibility. This flexibility potential is mostly unused today. To make the
energy system more flexible, some of its elements must be orchestrated so they
interact harmoniously. This is the role of a control strategy.

Before real deployment, the effect of control strategies applied to energy
system/flexible elements should be assessed by simulation. The Gridsim simulator
has been designed for that purpose.


********************************
Why using the Gridsim simulator?
********************************
Many powerful energy simulators do exist either as open source or licensed
software...
So why a new simulation framework?

Gridsim has two distinctive features:

* Gridsim  can model the complex interactions between energy carriers. It is not
  limited to a single energy carrier like electricity or heat.
* Gridsim should be seen as an open toolbox to quickly design the simulator
  adapted to specific needs.

Hence Gridsim expected users are researchers and developers in energy systems
who need to simulate complex, multi-carrier energy systems with their control
strategies.

The Gridsim simulator benefits of the power of the Python programming language.
A clear object oriented design makes the simulator scalable: the number of types
and instances can be increased while keeping a manageable program structure.
New element(s) types are typically designed by specialising existing elements.

*************
Main features
*************
The main features of the Gridsim simulator are listed below:

* The simulator allows to define the topology of an energy system (electrical
  grid, generation, consumption and storage elements, elements transforming
  energy from a form to another form) as well as dynamic environment parameters
  (for example, temperature or solar radiation over time at a given point).
* An energy system is simulated over a given time period (simulation period,
  typically one year) with a given unit time step (typically one second).
* Any energy system parameter can be recorded over the simulation period.

Each element has its own independent behaviour. At each unit time step, the
Gridsim core module addresses each element twice:

* Upon the first call, the element updates its internal state. To do this it has
  a logic defined by its type. It can request the public state of other
  elements.
* Upon the second call, the element updates its public state with its internal
  state.

This two step process guarantees that elements access the system in a steady
state.

For questions, bug reports, patches and new elements/modules,
contact gridsim@hevs.ch.

