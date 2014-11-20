Table of Contents
===

 1. Synopsis
 2. Latest Version
 3. Installation
 4. Documentation
 5. Bug Reporting
 6. Contributors
 7. Contacts
 8. License
 9. Copyright


1. Synopsis
===
Gridsim has two distinctive features:

 * Gridsim can model the complex interactions between energy carriers. It is
   not limited to a single energy carrier like electricity or heat.
 * Gridsim should be seen as an open toolbox to quickly design the simulator
 adapted to specific needs.

Hence Gridsim expected users are researchers and developers in energy systems
who need to simulated complex, multi-carrier energy systems with their control
strategies.

The Gridsim simulator benefits of the power of the Python programming language.
A clear object oriented design makes the simulator scalable: the number of types
and instances can be increased while keeping a manageable program structure. New
element(s) types are typically designed by specialising existing elements.


2. Latest Version
===
You can find the latest version of Gridsim on :
    http://

The current release of Gridsim is 0.1 and you can download it on pypi at :
    http://


3. Installation
===
Gridsim is a full python project thus as long as Python is installed on your
system you can install it by moving in the root folder (the folder this README
file should be) and run :
    python setup.py install
In some systems you need Administrator right to run this command.

/!\ Warning : Gridsim requires these packages to be used in full :

 * numpy
 * scipy
 * matplotlib
 * pint


4. Documentation
===
You can find the full documentation on :
    http://gridsim.hevs.ch
A documentation also is provided with this release in './doc' folder.


5. Bug Reporting
===
If you find any bugs, or if you want new features you can put your request on
github at the following address :
    http://


6. Contributors
===

The Gridsim Team is currently composed of :

 * Michael Clausen (clm@hevs.ch)
 * Dominique Gabioud (dominique.gabioud@hevs.ch)
 * Gilbert Maitre (gilbert.maitre@hevs.ch)
 * Gillian Basso (gillian.basso@hevs.ch)
 * Michael Sequeira Carvalho (michael.sequeira@hevs.ch)
 * Pierre Ferrez (pierre.ferrez@hevs.ch)
 * Pierre Roduit (pierre.roduit@hevs.ch)


7. Contacts
===
For questions, bug reports, patches and new elements / modules, contact :
gridsim@hevs.ch.


8. License
===
You should have received a copy of the GNU General Public License along with
this program.
If not, see <http://www.gnu.org/licenses/>.


9. Copyright
===
Copyright (C) 2011-2014 The Gridsim Team

This file is part of the Gridsim project.

the Gridsim project is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

the Gridsim project is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.
