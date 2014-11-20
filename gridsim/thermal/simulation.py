from gridsim.decorators import accepts
from gridsim.core import AbstractSimulationModule

from .core import AbstractThermalElement, ThermalProcess, ThermalCoupling


class ThermalSimulator(AbstractSimulationModule):

    def __init__(self):
        """
        Simulation module for all thermal simulation aspects.
        """
        super(ThermalSimulator, self).__init__()

        self._processes = []
        self._processesDict = {}
        self._couplings = []
        self._couplingsDict = {}

    def _process(self, process_id):
        if isinstance(process_id, int):
            if len(self._processes) > process_id:
                return self._processes[process_id]
            else:
                raise IndexError('Invalid index.')
        else:
            raise TypeError

    # SimulationModule implementation.
    def attribute_name(self):
        """
        AbstractSimulationModule implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationModule.attribute_name`.
        """
        return 'thermal'

    def all_elements(self):
        """
        AbstractSimulationModule implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationModule.all_elements`.
        """
        elements = []
        elements.extend(self._processes)
        elements.extend(self._couplings)
        return elements

    def reset(self):
        """
        AbstractSimulationModule implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationModule.reset`.
        """
        for process in self._processes:
            process.reset()
        for coupling in self._couplings:
            coupling.reset()

    def calculate(self, time, delta_time):
        """
        AbstractSimulationModule implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationModule.calculate`.
        """

        for process in self._processes:
            process.calculate(time, delta_time)

        for coupling in self._couplings:
            process_a = self._process(coupling.from_process_id)
            process_b = self._process(coupling.to_process_id)
            if process_a is not None and process_b is not None:

                coupling._delta_energy = \
                    (process_a.temperature - process_b.temperature) * \
                    coupling.thermal_conductivity * \
                    coupling.contact_area / coupling.thickness

                process_a.add_energy(-coupling._delta_energy * delta_time)

                process_b.add_energy(coupling._delta_energy * delta_time)

                #
                # Q = C * T     Q: Thermal energy [J]
                #               C: Thermal conductivity [J/K]
                # dT = Rth * I  T: Temperature [K]
                #               dT: Temperature difference [K]
                # dQ = dt * I   Rth: Thermal resistance [K/W]
                #               I: Thermal flow [W]
                #               dQ: Change of thermal energy per time
                #                   interval [J]
                #               dt: Time interval [s]


    def update(self, time, delta_time):
        """
        AbstractSimulationModule implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationModule.update`.
        """
        for process in self._processes:
            process.update(time, delta_time)
        for coupling in self._couplings:
            coupling.update(time, delta_time)

    @accepts((1, AbstractThermalElement))
    def add(self, element):
        """
        Adds the thermal process or thermal coupling to the thermal simulation
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
            elif element.from_process_id > len(self._processes):
                raise RuntimeError('Invalid from process or from process ID.')
            elif element.to_process_id > len(self._processes):
                raise RuntimeError('Invalid to process or to process ID.')
            element.id = len(self._couplings)
            self._couplings.append(element)
            self._couplingsDict[element.friendly_name] = element
            return element
