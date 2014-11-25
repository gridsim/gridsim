"""
.. moduleauthor:: Michael Clausen <clm@hevs.ch>
.. codeauthor:: Michael Clausen <clm@hevs.ch>

Gridsim core module. Defines the interface to the different simulation modules
and controls the sequence of the whole simulation.

To create a new Gridsim simulation you have to initialize a :class:`Simulator`
object. Then you will use the different simulation modules in order to define
the electrical and thermal topology and parametrize the data recorders and
controllers to form the complete simulation.

Once done, you should always start with a reset to ensure that all simulation
elements are in a defined state. Then you can either do a simple step using the
method :func:`Simulator.step` or run a simulation until a given time with a
given step size using the method :func:`Simulator.run`.

*Example:*

.. literalinclude:: ../../demo/simplesimulation.py
    :linenos:

The example above is pretty useless, but it illustrates the different stages
when defining a new simulation.

* On line 1 we import the gridsim.core module.
* On line 4 we create an instance of the Gridsim core Simulator class.
* At line 6 we just have a comment indicating that you can define the
  topology. This can be done by instantiating objects from the simulation
  modules and calling the modules API, so please have a look at the
  documentation of the different modules how to do that.
* We do a simulator reset at line 9.
* On line 12 we calculate a single step of about 100ms.
* On line 15 the simulation is run for 3600 seconds with a resolution (step
  size) of 100ms.

You can get access to the simulation modules by using special attributes of the 
core simulation object::

    sim = Simulation()
    sim.<module_name>

The <module_name> is per convention the name of the simulation module
    **gridsim.<module_name>**.

So if you import for example :mod:`gridsim.electrical`, you can get the
simulation module by typing::

    from gridsim.electrical import *

    sim = Simulator()
    el = sim.electrical

"""
from .decorators import accepts, returns


class AbstractSimulationModule(object):

    def __init__(self):
        """
        **This section will be only interesting for Gridsim module developers,
        if you just use the library, you can skip this section.**

        Interface for simulation modules. Gridsim groups different simulation
        aspects into different Python modules in oder to separate and
        organize the implementations.

        All Gridsim simulation modules have to implement the pure abstract
        methods of this interface class.

        *Example of a minimal simulation module:*

        .. literalinclude:: ../../demo/minimalmodule.py
        """
        super(AbstractSimulationModule, self).__init__()
        self.simulator = None

    @returns(str)
    def attribute_name(self):
        """
        This method should return the module's attribute name which can be used 
        in order to get the reference to the module at the main simulation
        level. If for example this string is "electrical", the reference to the
        simulation module can be retrieved using this name as the attribute
        passed to the simulation object.

        If the user wants a reference to the simulation's module, he uses::

            sim = Simulation()
            sim.<attribute_name>

        :returns: Attribute name under which the module should be accessible on 
            the main simulator object.
        :rtype: str
        """
        raise NotImplementedError('Abstract method called!')

    def all_elements(self):
        """
        This method should return a list of all elements contained in the
        module. The core simulator will use these lists in order to be able
        to retrieve objects or list of objects by certain criteria.
        """
        raise NotImplementedError('Abstract method called!')

    @accepts((1, int),
             ((2, 5), (str, type(None))),
             ((3, 4), (type, type(None))))
    def find(self, uid=None, friendly_name=None, element_class=None,
             instance_of=None, has_attribute=None):
        """
        Convenience method, already implemented for all modules in Gridsim.core.
        Finds all AbstractSimulationElement derived objects matching the
        given criteria by searching this Gridsim simulation module. Note that
        the method returns always a list of elements, even if only a single
        instance is found. All parameters are optionaresetl, if find() will be
        called without any parameters, the list of all elements in the actual
        simulation module will be returned.

        :param uid: ID of the element. Note that these ID's are only unique for
            a given class , so you should never search just for an ID without 
            specifying the class.
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
            'power' attribute.
        :type has_attribute: str

        """
        return self.simulator.find(
            module=self.attribute_name(), uid=uid, friendly_name=friendly_name,
            element_class=element_class, instance_of=instance_of,
            has_attribute=has_attribute
        )

    def reset(self):
        """
        The module has to reset/initialize his internal variables and to call 
        the reset method of all simulation elements it owns/manages.
        """
        raise NotImplementedError('Abstract method called!')

    def update(self, time, delta_time):
        """
        The master simulation object executes this method on all registered
        simulation modules in order to finish a simulation step. The module has
        to update its external state/variables and/or call the update() method
        on all simulation elements it owns/manages.

        :param time: The actual simulation time.
        :type time: float

        :param delta_time: The time period for which the update has
            to be done.
        :type delta_time: float
        """
        raise NotImplementedError('Abstract method called!')

    def calculate(self, time, delta_time):
        """
        The master simulation object executes this method on all registered
        simulation modules in order to calculate a step during the simulation
        process. The module has to calculate its internal state and/or call
        the update() method on all simulation elements it owns/manages.

        :param time: The actual simulation time.
        :type time: unit

        :param delta_time: The time period for which the calculation
            has to be done.
        :type delta_time: unit
        """
        raise NotImplementedError('Abstract method called!')


class AbstractSimulationElement(object):

    @accepts((1, str), (2, (int, type(None))))
    def __init__(self, friendly_name, element_id=None):
        """
        **This section will be only interesting for Gridsim module developers,
        if you just use the library, you can skip this section.**

        This class is the base for all elements that can be part of the 
        simulation. It basically defines the 'friendly_name' and the 'id'
        properties and all abstract methods an element should provide for to be
        part of a simulation in Gridsim.

        :param friendly_name: Friendly name for the element. Should be unique 
            within the simulation module.
        :type friendly_name: str
        
        :param element_id: ID of the element. Has to be unique per module and 
            element class. Defaults to None.
        :type element_id: int

        You find an example of an :class:`.AbstractSimulationElement` in the 
            description of :class:`.AbstractSimulationModule`.

        """
        super(AbstractSimulationElement, self).__init__()

        self.id = element_id
        """
        ID of the simulation element. Note that the ID has not to be unique 
            simulation wide, it has just to be unique in order a simulation 
            module can retrieve the element using the ID and the class 
            (base-class) information.
        """

        self.friendly_name = friendly_name
        """
        User friendly name of the simulation element. Note that the name has not
            to be unique simulation wide, it has just to be unique in order a 
            simulation module can retrieve the element using the friendly name 
            and the class (base-class) information.
        """

    def reset(self):
        """
        This method is called by the core simulator or the simulator module in 
        order to reset the elements internal data and state to initial values.
        Each simulation element has to implement this method without exception.
        """
        raise NotImplementedError('Pure abstract method!')

    def calculate(self, time, delta_time):
        """
        This method is called by the core simulator or the simulator module in 
        order to calculate the element's next state. Each element should have an
        internal and an external representation of its state and data. During
        the calculation step (this method) an element should only update its
        internal state and data, another method 'update()' will be used to copy
        these values to the public properties/attributes.

        :param time: The actual time of the simulator.
        :type time: unit
        
        :param delta_time: The delta time for which the calculation has to be 
            done.
        :type delta_time: unit
        """
        raise NotImplementedError('Pure abstract method!')

    def update(self, time, delta_time):
        """
        This method will be called after all simulation elements have done their
        calculation step. Each element should copy its internal state and data
        to the external accessible locations.

        :param time: The actual time of the simulator.
        :type time: unit
        
        :param delta_time: The delta time for which the update has to be done.
        :type delta_time: unit
        """
        raise NotImplementedError('Pure abstract method!')
