from gridsim.decorators import accepts, returns
from gridsim.core import AbstractSimulationModule

from .core import AbstractThermalElement, ThermalProcess, ThermalCoupling


class ThermalSimulator(AbstractSimulationModule):

    def __init__(self):
        """
        __init__(self)

        Gridsim main simulation class for thermal part. This module is
        automatically added to the :class:`.Simulator` when
        importing any class or module of :mod:`gridsim.thermal` package.

        To access this class from simulation, use :class:`.Simulator` as
        follow::

            # Create the simulation.
            sim = Simulator()
            thsim = sim.thermal

        """
        super(ThermalSimulator, self).__init__()

        self._processes = []
        self._processesDict = {}
        self._couplings = []
        self._couplingsDict = {}

    @accepts((1, int))
    @returns(ThermalProcess)
    def _process(self, process_id):
        return self._processes[process_id]

    @returns(str)
    def attribute_name(self):
        """
        attribute_name(self)

        Returns the name of this module.
        This name is used to access to this electrical simulator from the
        :class:`.Simulator`::

            # Create the simulation.
            sim = Simulator()
            thsim = sim.thermal

        :return: 'thermal'
        :rtype: str
        """
        return 'thermal'

    def all_elements(self):
        """
        all_elements(self)

        Returns a list of all :class:`.AbstractThermalElement`
        contained in the module.
        The core simulator will use these lists in order to be able
        to retrieve objects or list of objects by certain criteria using
        :func:`gridsim.simulation.Simulator.find`.

        :return: a list of all :class:`.AbstractThermalElement`
        :rtype: list
        """
        elements = []
        elements.extend(self._processes)
        elements.extend(self._couplings)
        return elements

    def reset(self):
        """
        reset(self)

        Calls :func:`gridsim.core.AbstractSimulationElement.reset` of
        each element in this thermal simulator, added by the
        :func:`ThermalSimulator.add`.
        """
        for process in self._processes:
            process.reset()
        for coupling in self._couplings:
            coupling.reset()

    @accepts(((1, 2), (int, float)))
    def calculate(self, time, delta_time):
        """
        calculate(self, time, delta_time)

        Calls :func:`gridsim.core.AbstractSimulationElement.calculate`
        of each :class:`.ThermalProcess` in this thermal
        simulator, added by the :func:`ThermalSimulator.add` then apply
        the :class:`.ThermalCoupling` to update the energy of each process.

        :param time: The actual simulation time.
        :type time: int or float in second

        :param delta_time: The time period for which the calculation
            has to be done.
        :type delta_time: int or float in second
        """

        for process in self._processes:
            process.calculate(time, delta_time)

        for coupling in self._couplings:
            coupling.calculate(time, delta_time)

    @accepts(((1, 2), (int, float)))
    def update(self, time, delta_time):
        """
        update(self, time, delta_time)

        Updates the data of each :class:`.AbstractThermalElement` in this
        electrical simulator added by the :func:`ThermalSimulator.add` and
        calculate the load flow with
        :class:`.AbstractElectricalLoadFlowCalculator`.

        :param time: The actual simulation time.
        :type time: int or float in second

        :param delta_time: The time period for which the calculation
            has to be done.
        :type delta_time: int or float in second
        """
        for process in self._processes:
            process.update(time, delta_time)
        for coupling in self._couplings:
            coupling.update(time, delta_time)

    @accepts((1, AbstractThermalElement))
    def add(self, element):
        """
        add(self, element)

        Adds the :class:`.ThermalProcess` or :class:`.ThermalCoupling` to the thermal simulation
        module.

        :param element: Element to add to the thermal simulator module.
        :type element: :class:`AbstractThermalElement`
        """
        if isinstance(element, ThermalProcess):
            if element.friendly_name in self._processesDict.keys():
                raise RuntimeError(
                    'Duplicate thermal process friendly name, must be unique.')
            element.id = len(self._processes)
            self._processes.append(element)
            self._processesDict[element.friendly_name] = element
            return element

        elif isinstance(element, ThermalCoupling):
            if element.friendly_name in self._couplingsDict.keys():
                raise RuntimeError(
                    'Duplicate thermal coupling friendly name, must be unique.')
            elif element.from_process is None:
                raise RuntimeError('Invalid from process.')
            elif element.to_process is None:
                raise RuntimeError('Invalid to process.')
            element.id = len(self._couplings)
            self._couplings.append(element)
            self._couplingsDict[element.friendly_name] = element
            return element
