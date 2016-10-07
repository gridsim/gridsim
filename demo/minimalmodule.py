from gridsim.unit import units
from gridsim.core import AbstractSimulationModule, AbstractSimulationElement
from gridsim.simulation import Simulator


# A very simple simulation element of the minimal simulation module example:
# tracks only the time.
class MinimalSimulationElement(AbstractSimulationElement):
    def __init__(self, friendly_name):
        # It is important to call the base class constructor with the
        # friendly name!
        super(MinimalSimulationElement, self).__init__(friendly_name)

        # Initialize all attributes within the __init__ method. Python standard
        # rules apply.
        self.val = None
        self._val = None

    # Called by the simulation module to reset this element.
    def reset(self):
        self.val = 0.
        self._val = 0.

    # Calculates the next state of the element. Note that we do not make the new
    # state public. This will be done in the update() method.
    def calculate(self, time, delta_time):
        self._val += delta_time

    # When all elements have been calculated the simulation is calling this
    # method on all elements in order to put their internal state outside.
    def update(self, time, delta_time):
        self.val = self._val


# A simulation module has to derive from AbstractSimulationModule and has to
# implement all methods.
class MinimalGridsimModuleAbstract(AbstractSimulationModule):

    # It is important that the module has an __init__() method without
    # parameters, as the modules were instantiated by the core simulator using
    # constructors without parameters.
    def __init__(self):
        # Prepare list of all contained elements. Here we have just one type
        # of elements.
        self.elements = []
        super(MinimalGridsimModuleAbstract, self).__init__()

    # This is a custom method of our minimal simulation module.
    def say_hello(self):
        print 'Hello'

    # Each module has to offer its own methods to add elements to the control
    # of the module.
    def add(self, element):
        # To avoid errors from library users we
        if not isinstance(element, MinimalSimulationElement):
            raise TypeError
        element.id = len(self.elements)
        self.elements.append(element)
        return element

    def attribute_name(self):
        return 'minimal'

    def reset(self):
        print 'reset'
        for element in self.elements:
            element.reset()

    def calculate(self, time, delta_time):
        print 'calculate, time=' + str(time) + ', delta_time=' + str(delta_time)
        for element in self.elements:
            element.calculate(time, delta_time)

    def update(self, time, delta_time):
        print 'update, time=' + str(time) + ', delta_time=' + str(delta_time)
        for element in self.elements:
            element.update(time, delta_time)

Simulator.register_simulation_module(MinimalGridsimModuleAbstract)

sim = Simulator()
sim.minimal.say_hello()
el = sim.minimal.add(MinimalSimulationElement('test'))
sim.reset()
sim.run(1*units.seconds, 250*units.milliseconds)

