from gridsim.unit import units
from gridsim.iodata.input import CSVReader
from gridsim.timeseries import TimeSeriesObject

# Load time series into a new object.
obj = TimeSeriesObject(CSVReader())
obj.load('./data/example.csv')

# Print value at start time.
print obj.temperature

# Proceed 120 and output the temperature at that moment.
obj.set_time(120*units.second)
print obj.temperature
