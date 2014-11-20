"""
.. moduleauthor:: Gillian Basso <gillian.basso@hevs.ch>

.. codeauthor:: Michael Clausen <clm@hevs.ch>

Gridsim util module. Defines utility classes and functions.

"""
import math

from .decorators import accepts, returns
from .unit import units


class Position(object):
    """
    Represents an abstract position on a three-dimensional space. The coordinate
    system is WGS84.
    """

    @accepts(((1, 2, 3), (int, float)))
    def __init__(self, latitude=0, longitude=0, altitude=0):
        """
        Represents an abstract position on a three-dimensional space. The
        coordinate system is WGS84.

        :param latitude: North-south point location the on the Earth's surface.
        :type latitude: int, float

        :param longitude: East-west position of a point on the Earth's surface.
        :type longitude: int, float

        :param altitude: Altitude. We recommend to use sea level as reference.
        :type altitude: int, float

        *Example:*
        ::

            from agreflex.core import Position

            # Create a point and output the coordinates.
            office = Position(46.240301, 7.358394, 566)
            print office

            # Create a second point.
            home = Position(46.309180, 7.972517, 676)

            # Calculate the difference between the two points.
            print home.distance_to(office)


        *Output:*
        ::

            Position: {
                latitude: 46,
                longitude: 7,
                altitude: 566
            }
        """
        super(Position, self).__init__()

        self.latitude = float(latitude)
        """Specifies the north-south point location on the Earth's surface."""

        self.longitude = float(longitude)
        """Specifies the east-west point position of on the Earth's surface."""

        self.altitude = float(altitude)
        """Altitude, we recommend to use the WGS84's sea level as reference."""

    def __eq__(self, other):
        return self.latitude == other.latitude \
            and self.longitude == other.longitude \
            and self.altitude == other.altitude

    def __ne__(self, other):
        return not self.__eq__(other)

    @returns(float)
    def distance_to(self, other):
        """
        Calculates the distance between two points in meters [m]. It uses the
            haversine formula to calculate the distance, so the altitude is
            ignored completely and the distance is calculated for booth points
            using the earth radius of 6371 km.

        :param other: The point to which the distance has to be calculated.
        :type other: Position

        :returns: The distance between the two points in meters [m].
        """
        d_lat = math.pi * (self.latitude - other.latitude) / 180.
        d_long = math.pi * (self.longitude - other.longitude) / 180.
        a = math.sin(d_lat / 2.) * math.sin(d_lat / 2.) + \
            math.cos(math.pi * other.latitude / 180.) * math.cos(
                math.pi * self.latitude) * \
            math.sin(d_long / 2.) * math.sin(d_long / 2.)
        return 6371000. * 2. * math.atan2(math.sqrt(a), math.sqrt(1. - a))


### ALL MATERIALS


class _MaterialType(type):
    """
    This is a meta class which authorized only one instance of Material and
    prevent to subclass a child of Material.
    """
    def __call__(cls, *args, **kwargs):

        if cls is Material:
            raise SyntaxError("Do not instantiate a Material class directly")
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(_MaterialType, cls).\
                __call__(*args, **kwargs)
            return cls.__instance

    def __init__(cls, name, bases, dct):
        if name is not "Material" and Material not in bases:
            raise SyntaxError("Do not subclass a child of Material, "
                              "directly subclass Material instead")

        super(_MaterialType, cls).__init__(name, bases, dct)


class Material(object):

    __metaclass__ = _MaterialType

    @accepts(((1, 2, 3), (int, float)))
    def __init__(self, c, p, k):
        """
        This class cannot be instanced directly. Each Material must inherit this
        class

        :param c: The thermal capacity in **[J/gK]**
        :type c: int, float
        :param p: The weight of the material in **[g/m3]**.
        :type p: int, float
        :param k: The thermal conductivity in **[W/Km]**.
        :type k: int, float
        :return:
        """

        super(Material, self).__init__()

        self._c = c*units.heat_capacity
        """
        The thermal capacity in **[J/gK]**
        In order to get the thermal capacity of an object, you only have to
        multiply this specific capacity with the object's mass in gram::

        # Calculate the thermal capacity of 1kg of air.
        t_cap = SpecificThermalCapacity.AIR * 1000

        .. note::
        Source: http://www.engineeringtoolbox.com/specific-heat-solids-d_154.html
        """
        self._p = p*units.mass_density
        """
        The weight of the material in **[g/m3]**.

        In order to get the mass of an object, you have just to multiply this
        specific wight with the object's volume in m3::

            # Calculate the mass capacity of 1m3 of air.
            t_cap = SpecificWeight.AIR * 1

        .. note::
            Source: http://www.simetric.co.uk/si_materials.htm
        """
        self._k = k*units.thermal_conductivity
        """
        The thermal conductivity in **[W/K*m]**.

        In order to get the thermal conductivity of an object, you have just to
        multiply this specific conductivity with the object's area in m2 and
        divide it with the objects thickness::

            # Calculate the thermal conductivity of a window with 1m2 surface
            # and a thickness of 3mm.
            t_cond = SpecificThermalConductivity.GLASS * 1 / 0.003

        .. note::
            Source: https://www.wolframalpha.com and
            http://en.wikipedia.org/wiki/List_of_thermal_conductivities
        """

    @property
    def thermal_capacity(self):
        return self._c

    @property
    def weight(self):
        return self._p

    @property
    def thermal_conductivity(self):
        return self._k


class Air(Material):
    def __init__(self):
        super(Air, self).__init__(1.005, 1200, 429)


class Aluminium(Material):
    def __init__(self):
        super(Aluminium, self).__init__(0.896, 1522000, 2.5)


class ArtificialWool(Material):
    def __init__(self):
        super(ArtificialWool, self).__init__(1.357, 1314000, 0.049)


class Asphalt(Material):
    def __init__(self):
        super(Asphalt, self).__init__(0.92, 721000, 0.75)


class Butane(Material):
    def __init__(self):
        super(Butane, self).__init__(1.658, 2006, 0.01607)


class Steel(Material):
    def __init__(self):
        super(Steel, self).__init__(0.49, 46.6, 7700000.0)


class Stone(Material):
    def __init__(self):
        super(Stone, self).__init__(0.49, None, 2515000.0)


class Gold(Material):
    def __init__(self):
        super(Gold, self).__init__(0.13, 317.1, 19200000.0)


class Copper(Material):
    def __init__(self):
        super(Copper, self).__init__(0.383, 401.2, 2200000.0)


class Petrol(Material):
    def __init__(self):
        super(Petrol, self).__init__(2.14, None, 881000.0)


class Sandstone(Material):
    def __init__(self):
        super(Sandstone, self).__init__(0.92, 2.5, 2323000.0)


class Cobalt(Material):
    def __init__(self):
        super(Cobalt, self).__init__(0.46, None, 8900000.0)


class Zinc(Material):
    def __init__(self):
        super(Zinc, self).__init__(0.38, 11.0, 0.38)


class Marple(Material):
    def __init__(self):
        super(Marple, self).__init__(0.88, 2.08, 2563000.0)


class Granite(Material):
    def __init__(self):
        super(Granite, self).__init__(0.79, 2.855, 2400000.0)


class Silk(Material):
    def __init__(self):
        super(Silk, self).__init__(1.38, None, None)


class Hydrogen(Material):
    def __init__(self):
        super(Hydrogen, self).__init__(14.32, None, 69600.0)


class HardBrick(Material):
    def __init__(self):
        super(HardBrick, self).__init__(1.0, 1.31, 2403000.0)


class Platinum(Material):
    def __init__(self):
        super(Platinum, self).__init__(0.13, 71.61, 21450000.0)


class Gypsum(Material):
    def __init__(self):
        super(Gypsum, self).__init__(1.09, None, 2787000.0)


class Tar(Material):
    def __init__(self):
        super(Tar, self).__init__(1.47, None, 1153000.0)


class Chromium(Material):
    def __init__(self):
        super(Chromium, self).__init__(0.5, 93.93, 6856000.0)


class Slate(Material):
    def __init__(self):
        super(Slate, self).__init__(0.76, None, 2691000.0)


class DryEarth(Material):
    def __init__(self):
        super(DryEarth, self).__init__(1.26, 0.864, 1249000.0)


class Rubber(Material):
    def __init__(self):
        super(Rubber, self).__init__(2.01, 0.16, 1522000.0)


class Concrete(Material):
    def __init__(self):
        super(Concrete, self).__init__(0.75, 1.04, 2403000.0)


class Pvc(Material):
    def __init__(self):
        super(Pvc, self).__init__(0.88, None, 1200000.0)


class Paper(Material):
    def __init__(self):
        super(Paper, self).__init__(1.336, 0.05, 1201000.0)


class Graphite(Material):
    def __init__(self):
        super(Graphite, self).__init__(0.71, None, 2070000.0)


class Iron(Material):
    def __init__(self):
        super(Iron, self).__init__(0.452, 80.43, 2500000.0)


class Clay(Material):
    def __init__(self):
        super(Clay, self).__init__(0.92, None, 1073000.0)


class GraphiteCarbon(Material):
    def __init__(self):
        super(GraphiteCarbon, self).__init__(0.71, None, None)


class Salt(Material):
    def __init__(self):
        super(Salt, self).__init__(0.88, None, 1000000.0)


class Mercury(Material):
    def __init__(self):
        super(Mercury, self).__init__(0.14, None, 13534000.0)


class Charcoal(Material):
    def __init__(self):
        super(Charcoal, self).__init__(1.0, None, 208000.0)


class Nickel(Material):
    def __init__(self):
        super(Nickel, self).__init__(0.461, 90.95, 8666000.0)


class Silicone(Material):
    def __init__(self):
        super(Silicone, self).__init__(0.75, 0.3, 2330000.0)


class DryCement(Material):
    def __init__(self):
        super(DryCement, self).__init__(1.55, None, 1506000.0)


class Cork(Material):
    def __init__(self):
        super(Cork, self).__init__(1.9, 0.0435, 240000.0)


class Chalk(Material):
    def __init__(self):
        super(Chalk, self).__init__(0.9, None, 2499000.0)


class Oil(Material):
    def __init__(self):
        super(Oil, self).__init__(1.67, None, 942000.0)


class Wood(Material):
    def __init__(self):
        super(Wood, self).__init__(2.0, 0.14, 500000.0)


class GlassWool(Material):
    def __init__(self):
        super(GlassWool, self).__init__(0.67, 0.04, 25000.0)


class Wax(Material):
    def __init__(self):
        super(Wax, self).__init__(3.43, None, None)


class Tungsten(Material):
    def __init__(self):
        super(Tungsten, self).__init__(0.134, 174.2, 19220000.0)


class Helium(Material):
    def __init__(self):
        super(Helium, self).__init__(5.193, 0.1535, 138000.0)


class Silver(Material):
    def __init__(self):
        super(Silver, self).__init__(0.23, 429.0, 10500000.0)


class Diamond(Material):
    def __init__(self):
        super(Diamond, self).__init__(0.63, 2.2, 3510000.0)


class Lead(Material):
    def __init__(self):
        super(Lead, self).__init__(0.129, 35.33, 11389000.0)


class LightConcrete(Material):
    def __init__(self):
        super(LightConcrete, self).__init__(0.96, 0.42, 1400000.0)


class Plaster(Material):
    def __init__(self):
        super(Plaster, self).__init__(1.3, 0.478, 849000.0)


class CommonBrick(Material):
    def __init__(self):
        super(CommonBrick, self).__init__(0.9, 1.26, 1922000.0)


class Water(Material):
    def __init__(self):
        super(Water, self).__init__(4.19, 0.5985, 1000000.0)


class Glass(Material):
    def __init__(self):
        super(Glass, self).__init__(0.84, 1.0, 2579000.0)


class DrySoil(Material):
    def __init__(self):
        super(DrySoil, self).__init__(0.8, None, None)


class Ethanol(Material):
    def __init__(self):
        super(Ethanol, self).__init__(2.43, 0.1664, 789000.0)


class Carbon(Material):
    def __init__(self):
        super(Carbon, self).__init__(0.52, 0.0146, 2146000.0)


class WetSoil(Material):
    def __init__(self):
        super(WetSoil, self).__init__(1.48, None, None)


class Wool(Material):
    def __init__(self):
        super(Wool, self).__init__(1.26, 0.049, 1314000.0)


class Porcelain(Material):
    def __init__(self):
        super(Porcelain, self).__init__(1.07, None, 2403000.0)


class DryLeather(Material):
    def __init__(self):
        super(DryLeather, self).__init__(1.5, None, 945000.0)
