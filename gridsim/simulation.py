"""
.. moduleauthor:: Gillian Basso <gillian.basso@hevs.ch>

.. codeauthor:: Michael Clausen <clm@hevs.ch>


The :mod:`gridsim.simulation` module defines a simple way to access to the
simulator and offers interfaces of communication with users.

To create a new gridsim simulation you have to initialize a :class:`Simulator`
object. Then you will use the different simulation modules in order to define
the electrical and/or thermal topology and parametrize the data recorders and
controllers to form the complete simulation.

Once done, you should always start with a reset to ensure that all simulation
elements are in a defined state. Then you can either do a simple step using the
method :func:`Simulator.step()` or run a simulation until a given time with a
given step size using the method :func:`Simulator.run()`.

*Example*::

    from gridsim.unit import units
    from gridsim.simulation import Simulator

    # Create the main simulator object.
    sim = Simulator()

    # Build topology using the different simulation modules
    ...

    # Run the simulation from the
    sim.run(1*units.hours, 100*units.milliseconds)


As Gridsim is based on modules. You can get access to the
simulation modules by using special attributes of the core simulation object::

    sim = Simulation()
    sim.<module_name>

So if you import for example :mod:`gridsim.electrical`, you can get the
simulation module by typing::

    sim = Simulator()
    el = sim.electrical

..  note::
    Actually, the name of the module is the returned value of
    :func:`gridsim.core.AbstractSimulationModule.attribute_name`.
    Refer to the module you want to use to retrieve the module name.
"""
import types
from collections import namedtuple

from .decorators import accepts, returns
from .core import AbstractSimulationElement, AbstractSimulationModule
from .util import Position
from .unit import units


class Recorder(object):

    @accepts((1, str))
    def __init__(self, attribute_name):
        """
        __init__(self, attribute_name)

        Defines the interface an object has to implement in order to get
        notified between simulation steps with a reference to the observed
        object, the name of the attribute/property, the actual time and the
        actual value of the observed attribute/property.

        To add a recorder to the simulation, use :func:`Simulator.record`.

        :param attribute_name: The name of the attribute observed by this
            recorder.
        :type attribute_name: str
        """
        super(Recorder, self).__init__()

        self._attribute_name = attribute_name
        """
        The name of the attribute observed by this recorder
        """

    @property
    @returns(str)
    def attribute_name(self):
        """
        The name of the attribute observed by this recorder.
        """
        return self._attribute_name

    @accepts((1, list))
    def on_simulation_reset(self, subjects):
        """
        on_simulation_reset(self, subjects)

        This method is called by the simulation on order to inform the recorder
        that the simulation has been reset. The parameter ``subjects`` is a list
        of all subjects that are observer by the actual recorder. The method is
        called for each binding the recorder has with the simulation. This means
        that you do 3 calls to :func:`Simulator.record()`
        with the same recorder, this method is called 3 times.

        :param subjects: list of all observed objects.
        :type subjects: list or tuple of
            :class:`gridsim.core.AbstractSimulationElement`
        """
        raise NotImplementedError('Pure abstract method!')

    @accepts((1, units.Quantity))
    def on_simulation_step(self, time):
        """
        on_simulation_step(self, time)

        This method is called each time the simulation just completed a step.
        This method is optional and not required to re-implement a recorder.

        :param time: The actual simulation time.
        :type time: time, see :mod:`gridsim.unit`
        """
        raise NotImplementedError('Pure abstract method!')

    @accepts((1, AbstractSimulationElement),
             (2, units.Quantity))
    def on_observed_value(self, subject, time, value):
        """
        on_observed_value(self, subject, time, value)

        Called by the main simulation engine between each simulation step in
        order the recorder can save the time-value pair of one or multiple
        :class:`.AbstractSimulationElement` subclass(es).
        Any recorder is required to implement this method.

        :param subject: The object that will be observed by the recorder.
        :type subject: :class:`.AbstractSimulationElement`

        :param time: The actual time of the simulation.
        :type time: time, see :mod:`gridsim.unit`

        :param value: The actual value of the attribute/property of the subject.
        :type value: Depends attribute...
        """
        raise NotImplementedError(
            'Any instance of a class implementing Recorder has to implement '
            'this method.')


class Simulator(object):

    # List of all registered simulation modules. Note this are classes and we
    # need to instantiate them in __init__().
    _simulation_modules = []

    # Named tuple to be used in the recorder lamdba function.
    _RecorderContext = namedtuple('RecorderContext', 'value time delta_time')

    @staticmethod
    @accepts((1, types.ClassType))
    def register_simulation_module(module_class):
        """
        register_simulation_module(module_class)

        Registers a simulation module class within the main simulator class.
        Note that you register the class, the simulator automatically
        instantiates an object of the class in its own constructor every time an
        instance of the simulator is created.

        :param module_class: The class to register as a simulation module.
        :type module_class: :class:`gridsim.core.AbstractSimulationModule`
        """
        Simulator._simulation_modules.append(module_class)

    def __init__(self):
        """
        __init__(self)

        Gridsim main simulation class. Moves the simulation of all modules
        on in time and groups all simulation modules. The constructor creates
        automatically an instance of each registered simulation module. The fact
        to import a simulation module to the user's project registers the module
        automatically within the main simulation class. So only modules really
        used by the simulation are instantiated.
        """
        super(Simulator, self).__init__()

        # Create an instance for each simulation module.
        self._modules = {}
        for module_class in Simulator._simulation_modules:
            module = module_class()
            module.simulator = self
            self._modules[module.attribute_name()] = module

        # Prepare an array for all recorders.
        self._recorders = []
        self._recorderBindings = []

        # Initialize time to nothing.
        self.time = None

    @accepts((1, str))
    @returns(AbstractSimulationModule)
    def __getattr__(self, item):
        """
        __getattr__(self, item)

        If the main simulation object does not own an attribute with the given
        name <sim>.<name>, this method gets called. If there exists a simulation
        module with the given attribute name, we return the reference to that
        module. This enables the user to access very easily the different
        aspects of the simulation.

        :param item: The name of the attribute that does not exists per se which
            can be a potential simulation module.
        :type item: str
        
        :returns: :class:`AbstractSimulationModule` - The module corresponding to the
            item or None of no such module was found.
        """
        if item in self._modules.keys():
            return self._modules[item]
        else:
            raise AttributeError("The module "+str(item)+" is not loaded")

    @accepts(
        ((1, 3, 6), (str, type(None))),
        ((2, 4, 5), (int, type(None))),
        (7, (tuple, type(None))),
    )
    @returns(list)
    def find(self, module=None, uid=None, friendly_name=None,
             element_class=None, instance_of=None,
             has_attribute=None, close_to=None):
        """
        find(self, module=None, uid=None, friendly_name=None, element_class=None, instance_of=None, has_attribute=None, close_to=None)

        Finds all :class:`.AbstractSimulationElement` derived
        objects matching the given criteria by searching on either the given
        Gridsim simulation module or by searching the whole simulation of the
        module was not specified. Note that the method returns always a list of
        elements, even if only a single instance is found. All parameters are
        optional, if :func:`find()` will be called without any parameters,
        the list of all elements in the actual simulation will be returned.

        :param module: The module to search for elements.
        :type module: str
        
        :param uid: ID of the element. Note that these ID's are only unique for
            a given class inside a module, so you should never search just for
            an ID without specifying either the class or at least the module.
        :type uid: int
        
        :param friendly_name: The friendly name to search for.
        :type friendly_name: str
        
        :param element_class: The exact class the element has to be an instance 
            of. Superclasses are not considered.
        :type element_class: type
        
        :param instance_of: The object has to be an instance of the given class,
            whereas this can be the superclass of the object too.
        :type instance_of: type
        
        :param has_attribute: The object should have an attribute with the given
            name. This can be used in order to find all objects that have a 
            ``power`` attribute.
        :type has_attribute: str
        
        :param close_to: The object's position should be closer to the given one
            than the given radius. The parameters should be passed as tuple of 
            the position and the radius in meters [m]
        :type close_to: (Position, float)
        
        :return: List of :class:`.AbstractSimulationElement`
            matching the given criteria.

        *Example:*

        .. literalinclude:: ../../demo/find.py

        """
        elements = []

        # Get the complete list of elements from either specific or all modules.
        if module is not None:
            if module in self._modules.keys():
                elements = self._modules[module].all_elements()
            else:
                return elements
        else:
            for module in self._modules.values():
                elements.extend(module.all_elements())

        # Only AbstractSimulationElements will be considered!
        elements = filter(
            lambda element: isinstance(element, AbstractSimulationElement),
            elements)

        # Apply the different filters.
        if uid is not None:
            elements = filter(lambda element: element.id == uid, elements)

        if friendly_name is not None:
            elements = filter(
                lambda element: element.friendly_name == friendly_name,
                elements)

        if element_class is not None:
            elements = filter(
                lambda element: element.__class__ == element_class, elements)

        if instance_of is not None:
            elements = filter(lambda element: isinstance(element, instance_of),
                              elements)

        if has_attribute is not None:
            elements = filter(lambda element: hasattr(element, has_attribute),
                              elements)

        if close_to is not None and len(close_to) is 2:
            position, radius = close_to
            if isinstance(position, Position) and isinstance(radius,
                                                             (float, int)):
                elements = filter(lambda element: element.position.distance_to(
                    position) <= radius, elements)

        return elements

    @accepts((1, units.Quantity))
    @returns(type(None))
    def reset(self, initial_time=0*units.second):
        """
        reset(self, initial_time=0*units.second)

        Resets (re-initializes) the simulation.

        :param initial_time: The initial time from which the simulation starts.
            Defaults to ``0``.
        :type initial_time: time, see :mod:`gridsim.unit`
        """
        self.time = initial_time
        for module in self._modules.values():
            module.reset()

        for recorder_binding in self._recorderBindings:
            recorder_binding.reset()

    @accepts((1, units.Quantity))
    @returns(type(None))
    def _calculate(self, delta_time):
        for module in self._modules.values():
            module.calculate(self.time, delta_time)

    @accepts((1, units.Quantity))
    @returns(type(None))
    def _update(self, delta_time):

        for module in self._modules.values():
            module.update(self.time, delta_time)

        for recorder in self._recorders:
            recorder.on_simulation_step(self.time)

        for recorder_binding in self._recorderBindings:
            recorder_binding.update(self.time, delta_time)

    @accepts((1, units.Quantity))
    @returns(type(None))
    def step(self, delta_time):
        """
        step(self, delta_time)

        Executes a single simulation step on all modules.

        :param delta_time: The delta time for the single step.
        :type delta_time: time, see :mod:`gridsim.unit`
        """
        self._calculate(delta_time)
        self.time += delta_time
        self._update(delta_time)

    @accepts(((1, 2), units.Quantity))
    def run(self, run_time, delta_time):
        """
        run(self, run_time, delta_time)

        Runs the simulation for a given time.

        The run_time parameter defines the duration the simulation has to run.
        If a simulation was already run before, the additional duration is
        run in addition.

        :param run_time: Total run time.
        :type run_time: time, see :mod:`gridsim.unit`
        
        :param delta_time: Time interval for the simulation.
        :type delta_time: time, see :mod:`gridsim.unit`
        """
        if self.time is None:
            self.reset()

        end_time = self.time + run_time
        self._update(delta_time)
        while self.time < end_time:
            self.step(delta_time)

    # Internal class. Holds a recorder and the binding of the recorder to an
    # attribute of an object.
    class _RecorderBinding(object):

        def __init__(self, recorder, subjects, conversion):
            super(Simulator._RecorderBinding, self).__init__()

            # Save the recorder instance and the subject's attribute.
            self._recorder = recorder
            self._subjects = subjects
            self._conversion = conversion

        def reset(self):
            # Call the reset handler of the recorder.
            self._recorder.on_simulation_reset(
                [subject.friendly_name for subject in self._subjects])

        def update(self, time, delta_time):
            # This method is called by the simulation after each simulation step
            #   in order to update the recorder.
            for subject in self._subjects:

                value = getattr(subject, self._recorder.attribute_name)

                if self._conversion is not None:
                    value = self._conversion(
                    Simulator._RecorderContext(value, time, delta_time))

                self._recorder.on_observed_value(subject.friendly_name,
                                                 time, value)


    @accepts((1, Recorder),
             (2, (list, tuple, AbstractSimulationElement)),
             (3, (types.FunctionType, type(None))))
    @returns(Recorder)
    def record(self, recorder, subjects, conversion=None):
        """
        record(self, recorder, subjects, conversion=None)

        Adds a recorder to an attribute of an object. The recorder has to
        implement the :class:`Recorder` interface in order to
        receive the data of the given attribute after each simulation step.

        :param recorder: Reference to the recorder object. This object gets
            notified about the changes of the object's attribute at each
            simulation step.
        :type recorder: :class:`Recorder`
        
        :param subjects: The subjects of the recorder, in other words the 
            objects which is attributes has to be recorded.
        :type subjects: list or tuple of :class:`.AbstractSimulationElement`

        :param conversion: Lambda function to convert the actual value taken
            from the attribute before recording. The lambda function gets a
            single parameter ``context`` which is a named tuple with the following
            elements:
            
            **value**: The actual value just read from the simulation element's
            attribute.

            **time**: The actual simulation time.

            **delta_time**: The time step just simulated before updating the
            recorder. This can be handy in order to calculate for example the
            power of a delta-energy value.

        :type conversion: lambda context
        
        :returns: Reference to the recoder.
        """
        if isinstance(subjects, AbstractSimulationElement):
            subjects = (subjects,)

        self._recorderBindings.append(self._RecorderBinding(recorder, subjects,
                                                            conversion))

        if not recorder in self._recorders:
            self._recorders.append(recorder)

        return recorder
