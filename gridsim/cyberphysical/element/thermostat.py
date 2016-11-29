from gridsim.unit import units

from gridsim.util import Position
from gridsim.controller import AbstractControllerElement


class Thermostat(AbstractControllerElement):
    def __init__(self, friendly_name, target_temperature, hysteresis,
                 thermal_process, subject, attribute,
                 on_value=True, off_value=False, position=Position()):
        """
        A thermostat controller. This class measures the temperature of a
        thermal process (typically a room) and controls ANY attribute of any
        AbstractSimulationElement depending the measured temperature, the given
        target_temperature and the hysteresis.

        :param: friendly_name: User friendly name to give to the element.
        :type friendly_name: str

        :param: target_temperature: The temperature to try to maintain inside
            the target ThermalProcess.
        :type: target_temperature: temperature see :mod:`gridsim.unit`

        :param: hysteresis: The +- hysteresis in order to avoid to fast on/off
            switching.
        :type: hysteresis: delta temperature see :mod:`gridsim.unit`

        :param: thermal_process: The reference to the thermal process to
            observe.
        :type: thermal_process: :class:`.ThermalProcess`

        :param: subject: Reference to the object of which is attribute has to be
            changed depending on the temperature.
        :type: object

        :param: attribute: The name of the attribute to control as string.
        :type: str

        :param: on_value: The value to set for the attribute in order to turn
            the device "on".
        :type: on_value: any

        :param: off_on_value: The value to set for the attribute in order to
            turn the device "off".
        :type: off_value: any

        :param position: The position of the thermal element.
            Defaults to [0,0,0].
        :type position: :class:`Position`
        """
        super(Thermostat, self).__init__(friendly_name, position)
        self.target_temperature = units.value(target_temperature, units.kelvin)
        """
        The temperature to try to retain inside the observer thermal process by
        conducting an electrothermal element.
        """

        self.hysteresis = units.value(hysteresis, units.kelvin)
        """
        The +- hysteresis applied to the temperature measure in order to avoid
        to fast on/off switching.
        """

        if not hasattr(thermal_process, 'temperature'):
            raise TypeError('thermal_process')
        self.thermal_process = thermal_process
        """
        The reference to the thermal process to observe and read the
        temperature from.
        """

        self.subject = subject
        """
        The reference to the element to control.
        """

        self.attribute = attribute
        """
        Name of the attribute to control.
        """

        self.on_value = on_value
        """
        Value to set in order to turn the element on.
        """

        self.off_value = off_value
        """
        Value to set in order to turn the element off.
        """

        self._output_value = off_value

    def setTargetTemperature(self, target_temperature):
        self.target_temperature = target_temperature

    def setHysteresis(self, hysteresis):
        self.hysteresis = hysteresis

    # AbstractSimulationElement implementation.
    def reset(self):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.reset`.
        """
        pass

    def calculate(self, time, delta_time):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.calculate`.
        """
        actual_temperature = self.thermal_process.temperature

        if actual_temperature < (self.target_temperature - self.hysteresis / 2.):
            self._output_value = self.on_value
        elif actual_temperature > (self.target_temperature + self.hysteresis / 2.):
            self._output_value = self.off_value

    def update(self, time, delta_time):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.update`.
        """
        setattr(self.subject, self.attribute, self._output_value)
