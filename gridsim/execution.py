import time

from gridsim.unit import units

class TimeManager(object):
    def __init__(self):
        super(TimeManager, self).__init__()

        self.start = 0
        self.elapsed = 0

    def reset(self):
        self.start = time.time()
        self.elapsed = 0

    def wait(self):
        raise NotImplementedError('Pure abstract method!')

class RealTimeManager(TimeManager):
    @units.wraps(None, (None, units.second))
    def __init__(self, time):
        super(RealTimeManager, self).__init__()

        self.time = time

    def wait(self):
        self.elapsed = time.time() - self.start  # execution time correction
        towait = self.time - self.elapsed
        if towait > 0:
            time.sleep(towait)  # time to remaing to wait on, block
        self.start = time.time()