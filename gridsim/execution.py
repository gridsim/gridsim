"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from gridsim.unit import units

import time

class ExecutionManager(object):
    def __init__(self):
        """

        __init__(self)

        Abstract class of an execution manager object that does preprocess before stepping
        and postprocess after it.
        """
        super(ExecutionManager, self).__init__()

    def reset(self):
        """

        reset(self)

        Reset the execution manager object
        """
        raise NotImplementedError('Pure abstract method!')

    def preprocess(self):
        """

        preprocess(self)

        Preprocess the step (calculate, update). This function is executed at the beginning of the
        step of the simulation
        """
        raise NotImplementedError('Pure abstract method!')

    def postprocess(self):
        """

        postprocess(self)

        Postprocess the step (calculate, update). This function is executed directly after the step
        of the simulation
        """
        raise NotImplementedError('Pure abstract method!')


class DefaultExecutionManager(object):
    def __init__(self):
        """

        __init__(self)

        An execution manager that does not influence the execution
        """
        super(DefaultExecutionManager, self).__init__()

    def reset(self):
        """

        reset(self)

        Resets the execution manager object.
        """
        pass

    def preprocess(self):
        """

        preprocess(self)

        Preprocesses the step (calculate, update). This function is executed at the beginning of the
        step of the simulation.
        """
        pass

    def postprocess(self):
        """

        postprocess(self)

        Postprocesses the step (calculate, update). This function is executed directly after the step
        of the simulation.
        """
        pass


class RealTimeExecutionManager(ExecutionManager):
    @units.wraps(None, (None, units.second))
    def __init__(self, time):
        """

        __init__(self,time)

        Initialize the realtime manager with a default waiting time. That means if a step takes more
        time than an other step the average time will be always :param time:. This object will wait less
        time if the step uses more time than expected.

        :param time: time to wait between step in real time
        """
        super(RealTimeExecutionManager, self).__init__()

        self._time = time
        self._start = 0
        self._elapsed = 0

    def reset(self):
        self._start = time.time()
        self._elapsed = 0

    def preprocess(self):
        pass

    def postprocess(self):
        """

        postprocess(self)

        This function waits for the given time and adapt the remaining time to try to wait always
        :self.time:. If the step takes longer time than :self.time: the wait doesn't occur.
        """
        self._elapsed = time.time() - self._start  # execution time correction
        towait = self._time - self._elapsed
        if towait > 0:
            time.sleep(towait)  # time to remaining to wait on, block
        self._start = time.time()