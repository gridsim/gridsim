import time

from gridsim.unit import units

class ExecutionManager(object):
    def __init__(self):
        super(ExecutionManager, self).__init__()

    def reset(self):
        raise NotImplementedError('Pure abstract method!')

    def preprocess(self):
        raise NotImplementedError('Pure abstract method!')

    def postprocess(self):
        raise NotImplementedError('Pure abstract method!')

class RealTimeExecutionManager(ExecutionManager):
    @units.wraps(None, (None, units.second))
    def __init__(self, time):
        super(RealTimeExecutionManager, self).__init__()

        self.time = time
        self.start = 0
        self.elapsed = 0

    def reset(self):
        self.start = time.time()
        self.elapsed = 0

    def preprocess(self):
        pass

    def postprocess(self):
        self.elapsed = time.time() - self.start  # execution time correction
        towait = self.time - self.elapsed
        if towait > 0:
            time.sleep(towait)  # time to remaining to wait on, block
        self.start = time.time()