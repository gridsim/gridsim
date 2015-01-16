"""
.. moduleauthor:: Gillian Basso (gillian.basso@hevs.ch)
.. codeauthor:: Michael Clausen (clm@hevs.ch)


"""
from gridsim.decorators import accepts
from gridsim.util import Air, Position
from gridsim.unit import units
from gridsim.core import AbstractSimulationElement


class AbstractThermalElement(AbstractSimulationElement):

    @accepts((1, str),
             (2, Position))
    def __init__(self, friendly_name, position=Position()):
        """
        __init__(self, friendly_name, position=Position())

        Base class of all :class:`.AbstractSimulationElement` that have to be in
        the :class:`.ThermalSimulator`

        :param friendly_name: User friendly name to give to the element.
        :type friendly_name: str

        :param position: The position of the thermal element.
            Defaults to [0,0,0].
        :type position: :class:`.Position`
        """
        super(AbstractThermalElement, self).__init__(friendly_name)

        self._position = position

    @property
    def position(self):
        """
        position(self)

        Returns the thermal simulation element's position.

        :returns: Position of the element.
        """
        return self._position


class ThermalProcess(AbstractThermalElement):

    @accepts((1, str),
             ((2, 3, 4), units.Quantity),
             (5, Position))
    def __init__(self, friendly_name,
                 thermal_capacity, initial_temperature, mass=1*units.kilogram,
                 position=Position()):
        """
        __init__(self, friendly_name, thermal_capacity, initial_temperature, mass=1*units.kilogram, position=Position()):

        The very basic element of a thermal simulation. A thermal process
        represents a closed thermal envelope like a room or a amount of
        matter which has an uniform thermal capacity and and stores an amount of
        thermal energy resulting in a temperature. Those thermal processes
        can be coupled by :class:`ThermalCoupling` elements.

        :param friendly_name: The name to give to the thermal process.
        :type friendly_name: str

        :param thermal_capacity: The thermal capacity of the process.
            See :class:`.Material`.
        :type thermal_capacity: heat_capacity, see :mod:`gridsim.unit`

        :param initial_temperature: The initial temperature of the process in
            degrees.
        :type initial_temperature: kelvin, see :mod:`gridsim.unit`

        :param mass: the mass of the element
        :type mass: mass, see :mod:`gridsim.unit`

        :param position: The position of the process.
        :type position: :class:`.Position`
        """
        super(ThermalProcess, self).__init__(friendly_name, position)
        self._initial_temperature = initial_temperature

        self._mass = mass

        self._internal_thermal_energy = initial_temperature * \
            thermal_capacity * mass

        self.thermal_capacity = thermal_capacity
        """
        The thermal capacity of the thermal process.
        """

        self.temperature = initial_temperature
        """
        The temperature of the process.
        """

        self.thermal_energy = self._internal_thermal_energy
        """
        The thermal energy stored inside the thermal process.
        """

    def add_energy(self, delta_energy):
        """
        add_energy(self, delta_energy)

        Adds a given amount of energy to the thermal process.

        :param delta_energy: The energy to add to the thermal process.
        :type delta_energy: joule, see :mod:`gridsim.unit`
        """
        self._internal_thermal_energy += delta_energy

    def reset(self):
        """
        reset(self)

        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.reset`.
        """
        self.temperature = self._initial_temperature

        self._internal_thermal_energy = \
            self._initial_temperature * self.thermal_capacity * self._mass

        self.thermal_energy = self._internal_thermal_energy

    def calculate(self, time, delta_time):
        """
        calculate(self, time, delta_time)

        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.calculate`.
        """
        pass

    def update(self, time, delta_time):
        """
        update(self, time, delta_time)

        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.update`.
        """
        self.thermal_energy = self._internal_thermal_energy
        self.temperature = self.thermal_energy / \
                           (self.thermal_capacity * self._mass)

    @staticmethod
    @accepts((0, str),
             (4, Position))
    def room(friendly_name,
             surface, height,
             initial_temperature=units(20, units.degC),
             position=Position()):
        """
        room(friendly_name, surface, height, initial_temperature=293.15*units.kelvin, position=Position()):

        Returns the thermal process of a room filled with air and the given
        surface, height and initial temperature.

        :param friendly_name: Friendly name to give to the returned object.
        :type friendly_name: str
        :param surface: The room's surface.
        :type surface: square_meter, see :mod:`gridsim.unit`
        :param height: The room's height.
        :type height: meter, see :mod:`gridsim.unit`
        :param initial_temperature: The initial temperature inside the room.
        :type initial_temperature: kelvin, see :mod:`gridsim.unit`
        :param position: The position of the process.
        :type position: :class:`.Position`
        :return: A new thermal process object representing the room or None on
            error.
        """
        return ThermalProcess(friendly_name,
                              Air().thermal_capacity,
                              initial_temperature,
                              surface * height * Air().weight,
                              position)

    @staticmethod
    def solid(friendly_name,
              specific_thermal_capacity, mass,
              initial_temperature=units(20, units.degC),
              position=Position()):
        """
        solid(friendly_name, specific_thermal_capacity, mass, initial_temperature=units(20, units.degC), position=Position()):

        Returns the thermal process of a solid body and the given mass, initial
        temperature.

        :param friendly_name: Friendly name to give to the returned object.
        :type friendly_name: str
        :param specific_thermal_capacity: The thermal capacity.
        :type specific_thermal_capacity: thermal_capacity, see :mod:`gridsim.unit`
        :param mass: The solid's mass.
        :type mass: mass, see :mod:`gridsim.unit`
        :param initial_temperature: The initial temperature of the solid.
        :type initial_temperature: temperature, see :mod:`gridsim.unit`
        :param position: The position of the solid.
        :type position: :class:`.Position`
        :return: A new thermal process object representing the solid or None
            on error.
        """
        return ThermalProcess(friendly_name, specific_thermal_capacity,
                              initial_temperature, mass, position)


class ThermalCoupling(AbstractThermalElement):

    @accepts((1, str),
             ((3, 4), ThermalProcess))
    def __init__(self, friendly_name, thermal_conductivity,
                 from_process,
                 to_process,
                 contact_area=1*units.metre*units.metre,
                 thickness=1*units.metre):
        """
        __init__(self, friendly_name, thermal_conductivity, from_process, to_process, contact_area=1*units.metre*units.metre, thickness=1*units.metre)

        A thermal coupling connects two thermal processes allowing them to
        exchange thermal energy.

        :param friendly_name: The friendly name to identify the element.
        :type friendly_name: str

        :param thermal_conductivity: The thermal conductivity of the thermal
            element.
        :type thermal_conductivity: thermal conductivity, see :mod:`gridsim.unit`

        :param from_process: The first process coupled
            process.
        :type from_process: :class:`ThermalProcess`

        :param to_process: The second process coupled
            process.
        :type to_process: :class:`ThermalProcess`
        """
        super(ThermalCoupling, self).__init__(friendly_name)

        self.from_process = from_process
        self.to_process = to_process

        self.thermal_conductivity = thermal_conductivity
        """
        The thermal conductivity of the coupling in W/K.
        """
        self._contact_area = contact_area
        """
        The size of the contact area between the two :class:`ThermalProcess`
        """
        self._thickness = thickness
        """
        The thickness of the material between the two :class:`ThermalProcess`
        """
        self._delta_energy = 0*units.joule
        """
        The energy variation
        """
        self.power = None
        """
        Thermal power that gets conducted by the thermal coupling.
        """

    @property
    def contact_area(self):
        return self._contact_area

    @property
    def thickness(self):
        return self._thickness

    def reset(self):
        """
        reset(self)

        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.reset`.
        """
        self._delta_energy = 0*units.joule

    def calculate(self, time, delta_time):
        """
        calculate(self, time, delta_time)

        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.calculate`.
        """
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
        self._delta_energy = \
            ((self.from_process.temperature - self.to_process.temperature) * \
            self.thermal_conductivity * \
            self.contact_area / self.thickness)*delta_time

        self.from_process.add_energy(-self._delta_energy)
        self.to_process.add_energy(self._delta_energy)

    def update(self, time, delta_time):
        """
        update(self, time, delta_time)

        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.update`.
        """
        self.power = self._delta_energy / delta_time
