"""
.. moduleauthor:: Michael Clausen <clm@hevs.ch>
.. codeauthor:: Michael Clausen <clm@hevs.ch>

Gridsim core module. Defines the interface to the different simulation modules
and controls the sequence of the whole simulation.

This core module provides 2 interesting classes to add new features to Gridsim:
 * The :class:`gridsim.core.AbstractSimulationModule` that provides a simple
   way to add features to Gridsim.

   and
 * The :class:`gridsim.core.AbstractSimulationElement` that provides a simple
   way to a features in already implemented
   :class:`gridsim.core.AbstractSimulationModule`.

Despite the fact that the simulation module is completely free how to organize
its internal simulation behavior, the normal case is shown in the following
sequence diagram:

.. _fig-core-model-sequence2:

.. figure:: ./figures/model-sequence2.png
    :align: center
    :scale: 100 %

The :class:`gridsim.simulation.Simulator` is simply an aggregator of several
:class:`gridsim.core.AbstractSimulationModule`. When the user calls the
:func:`gridsim.simulation.Simulator.reset` the simulator simply calls the
:func:`gridsim.core.AbstractSimulationModule.reset` of every loaded modules.
Likewise, when the user calls the :func:`gridsim.simulation.Simulator.step` the
simulator calls first the :func:`gridsim.core.AbstractSimulationModule.calculate`
of every loaded modules then their :func:`gridsim.core.AbstractSimulationModule.update`.

Finally the :func:`gridsim.simulation.Simulator.run` function of the simulator
is only a set of sequential calls of :func:`gridsim.simulation.Simulator.step`
incrementing the time.
"""
from .decorators import accepts, returns


class AbstractSimulationModule(object):

    def __init__(self):
        """
        __init__(self)

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
        attribute_name(self)

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
        all_elements(self)

        This method should return a list of all elements contained in the
        module. The core simulator will use these lists in order to be able
        to retrieve objects or list of objects by certain criteria.
        """
        raise NotImplementedError('Abstract method called!')

    @accepts((1, int), ((2, 5), (str, type(None))), ((3, 4), (type, type(None))))
    @returns(list)
    def find(self, uid=None, friendly_name=None, element_class=None,
             instance_of=None, has_attribute=None):
        """
        find(self, uid=None, friendly_name=None, element_class=None, instance_of=None, has_attribute=None)

        Convenience method, already implemented for all modules in Gridsim.core.
        Finds all AbstractSimulationElement derived objects matching the
        given criteria by searching this Gridsim simulation module. Note that
        the method returns always a list of elements, even if only a single
        instance is found. All parameters are optional, if :func:`find` will be
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

        :return: a list of all :class:`.AbstractThermalElement`
        :rtype: list
        """
        return self.simulator.find(
            module=self.attribute_name(), uid=uid, friendly_name=friendly_name,
            element_class=element_class, instance_of=instance_of,
            has_attribute=has_attribute
        )

    def reset(self):
        """
        reset(self)

        The module has to reset/initialize his internal variables and to call 
        the reset method of all simulation elements it owns/manages.
        """
        raise NotImplementedError('Abstract method called!')

    @accepts(((1, 2), (int, float)))
    def update(self, time, delta_time):
        """
        update(self, time, delta_time)

        The master simulation object executes this method on all registered
        simulation modules in order to finish a simulation step. The module has
        to update its external state/variables and/or call the :func:`update`
        method on all simulation elements it owns/manages.

        :param time: The actual simulation time.
        :type time: int or float in in second

        :param delta_time: The time period for which the update has
            to be done.
        :type delta_time: int or float in second
        """
        raise NotImplementedError('Abstract method called!')

    @accepts(((1, 2), (int, float)))
    def calculate(self, time, delta_time):
        """
        calculate(self, time, delta_time)

        The master simulation object executes this method on all registered
        simulation modules in order to calculate a step during the simulation
        process. The module has to calculate its internal state and/or call
        the :func:`update` method on all simulation elements it owns/manages.

        :param time: The actual simulation time.
        :type time: int or float in in second

        :param delta_time: The time period for which the calculation
            has to be done.
        :type delta_time: int or float in second
        """
        raise NotImplementedError('Abstract method called!')


class AbstractSimulationElement(object):

    @accepts((1, str), (2, (int, type(None))))
    def __init__(self, friendly_name, element_id=None):
        """
        __init__(self, friendly_name, element_id=None)

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
        reset(self)

        This method is called by the core simulator or the simulator module in 
        order to reset the elements internal data and state to initial values.
        Each simulation element has to implement this method without exception.
        """
        raise NotImplementedError('Pure abstract method!')

    @accepts(((1, 2), (int, float)))
    def calculate(self, time, delta_time):
        """
        calculate(self, time, delta_time)

        This method is called by the core simulator or the simulator module in 
        order to calculate the element's next state. Each element should have an
        internal and an external representation of its state and data. During
        the calculation step (this method) an element should only update its
        internal state and data, another method :func:`update` will be used to
        copy these values to the public properties/attributes.

        :param time: The actual time of the simulator.
        :type time: time, see :mod:`gridsim.unit`
        
        :param delta_time: The delta time for which the calculation has to be 
            done.
        :type delta_time: time, see :mod:`gridsim.unit`
        """
        raise NotImplementedError('Pure abstract method!')

    @accepts(((1, 2), (int, float)))
    def update(self, time, delta_time):
        """
        update(self, time, delta_time)

        This method will be called after all simulation elements have done their
        calculation step. Each element should copy its internal state and data
        to the external accessible locations.

        :param time: The actual time of the simulator.
        :type time: time, see :mod:`gridsim.unit`
        
        :param delta_time: The delta time for which the update has to be done.
        :type delta_time: time, see :mod:`gridsim.unit`
        """
        raise NotImplementedError('Pure abstract method!')
