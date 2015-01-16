from gridsim.simulation import Simulator
from gridsim.unit import units
from gridsim.electrical.network import ElectricalPVBus, ElectricalPQBus,\
    ElectricalTransmissionLine, ElectricalGenTransformer
from gridsim.electrical.element import GaussianRandomElectricalCPSElement, \
    ConstantElectricalCPSElement
from gridsim.recorder import PlotRecorder
from gridsim.electrical.loadflow import DirectLoadFlowCalculator

from gridsim.iodata.output import FigureSaver

# Create the simulation.
sim = Simulator()
esim = sim.electrical
esim.load_flow_calculator = DirectLoadFlowCalculator()

# add buses to simulator
# slack bus has been automatically added
esim.add(ElectricalPQBus('Bus 1'))
esim.add(ElectricalPQBus('Bus 2'))
esim.add(ElectricalPQBus('Bus 3'))
esim.add(ElectricalPVBus('Bus 4'))

# add branches to simulator
# this operation directly connects them to buses, buses have to be already added
# variant 1
esim.connect('Branch 5-3', esim.bus('Slack Bus'), esim.bus('Bus 3'),
             ElectricalGenTransformer('Tap 1', complex(1.05), 0.03*units.ohm))
tl1 = esim.connect('Branch 3-1', esim.bus('Bus 3'), esim.bus('Bus 1'),
                   ElectricalTransmissionLine('Line 1',
                                              1.0*units.metre,
                                              0.35*units.ohm, 0.1*units.ohm))
tl2 = esim.connect('Branch 3-2', esim.bus('Bus 3'), esim.bus('Bus 2'),
                   ElectricalTransmissionLine('Line 2',
                                              1.0*units.metre,
                                              0.3*units.ohm, 0.08*units.ohm,
                                              2*0.25*units.siemens))
tl3 = esim.connect('Branch 1-2', esim.bus('Bus 1'), esim.bus('Bus 2'),
                   ElectricalTransmissionLine('Line 3',
                                              1.0*units.metre,
                                              0.25*units.ohm, 0.04*units.ohm,
                                              2*0.25*units.siemens))
esim.connect('Branch 4-2', esim.bus('Bus 4'), esim.bus('Bus 2'),
             ElectricalGenTransformer('Tap 2', complex(1.05), 0.015*units.ohm))

# attach electrical elements to buses, electrical elements are automatically
# added to simulator
esim.attach('Bus 1', GaussianRandomElectricalCPSElement('Load1',
                        1.6*units.watt, 0.1*units.watt))
esim.attach('Bus 2', GaussianRandomElectricalCPSElement('Load2',
                        2.0*units.watt, 0.2*units.watt))
esim.attach('Bus 3', GaussianRandomElectricalCPSElement('Load3',
                        3.7*units.watt, 0.3*units.watt))
esim.attach('Bus 4', ConstantElectricalCPSElement('Gen', -5.0*units.watt))

# Create a plot recorder which records power on each bus.
bus_pwr = PlotRecorder('P', units.second, units.watt)
sim.record(bus_pwr, esim.find(element_class=ElectricalPQBus))

# Create a plot recorder which records power on transmission lines.
line_pwr = PlotRecorder('Pij', units.second, units.watt)
sim.record(line_pwr, [tl1, tl2, tl3])

# It is recommended to perform the simulator reset operation.
sim.reset()

print("Running simulation...")

# Run the simulation for two hours with a resolution of 1 minute.
total_time = 2*units.hours
delta_time = 1*units.minutes
sim.run(total_time, delta_time)

print("Saving data...")

# Save the figures as images.
saver = FigureSaver(bus_pwr, "PQ Bus power")
saver.save('./output/bus_pwr.pdf')
saver = FigureSaver(line_pwr, "Line power")
saver.save('./output/line_pwr.pdf')
