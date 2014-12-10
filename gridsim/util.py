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

            from gridsim.util import Position

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
        __init__(self, c, p, k)

        .. warning:: This class cannot be instanced directly. Use sub classes instead.
                     Each Material must inherit this class.

        This class offer simple access to constants of materials.

        *Example*::

            >>> from gridsim.util import Air
            >>> print Air().thermal_conductivity
            0.02587 thermal_conductivity

        With ``thermal_conductivity`` is ``W/Km``, see :mod:`gridsim.unit`
        for more information.

        :param c: The thermal capacity in ``J/gK``.
        :type c: int, float
        :param p: The weight of the material in ``g/m3``.
        :type p: int, float
        :param k: The thermal conductivity in ``W/Km``.
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
        The thermal conductivity in **[W/Km]**.

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
        """
        The thermal capacity in **[J/gK]**
        In order to get the thermal capacity of an object, you only have to
        multiply this specific capacity with the object's mass in gram::

            # Calculate the thermal capacity of 1kg of air.
            t_cap = AIR().thermal_capacity * 1000

        .. note::
            Source: http://www.engineeringtoolbox.com/specific-heat-solids-d_154.html

        :return: the thermal capacity
        :rtype: thermal capacity, see :mod:`gridsim.unit`
        """
        return self._c

    @property
    def weight(self):
        """
        The weight of the material in **[g/m3]**.

        In order to get the mass of an object, you have just to multiply this
        specific wight with the object's volume in m3::

            # Calculate the mass capacity of 1m3 of air.
            t_cap = Air().weight * 1

        .. note::
            Source: http://www.simetric.co.uk/si_materials.htm

        :return: the weight of the material
        :rtype: weight, see :mod:`gridsim.unit`
        """
        return self._p

    @property
    def thermal_conductivity(self):
        """
        The thermal conductivity in **[W/Km]**.

        In order to get the thermal conductivity of an object, you have just to
        multiply this specific conductivity with the object's area in m2 and
        divide it with the objects thickness::

            # Calculate the thermal conductivity of a window with 1m2 surface
            # and a thickness of 3mm.
            t_cond = Glass().thermal_conductivity * 1 / 0.003

        .. note::
            Source: https://www.wolframalpha.com and
            http://en.wikipedia.org/wiki/List_of_thermal_conductivities

        :return: The thermal conductivity
        :rtype: thermal conductivity, see :mod:`gridsim.unit`
        """
        return self._k


class Steel(Material):
    def __init__(self):
        """
        Implementation of steel:

        * Thermal capacity: ``0.49 J/gK``
        * Weight: ``7700000 g/m3``
        * Thermal conductivity ``46.6 W/Km``

        """
        super(Steel, self).__init__(0.49, 7700000, 46.6)


class Stone(Material):
    def __init__(self):
        """
        Implementation of stone:

        * Thermal capacity: ``0.49 J/gK``
        * Weight: ``2515000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Stone, self).__init__(0.49, 2515000, None)


class Gold(Material):
    def __init__(self):
        """
        Implementation of gold:

        * Thermal capacity: ``0.13 J/gK``
        * Weight: ``19200000 g/m3``
        * Thermal conductivity ``317.1 W/Km``

        """
        super(Gold, self).__init__(0.13, 19200000, 317.1)


class Copper(Material):
    def __init__(self):
        """
        Implementation of copper:

        * Thermal capacity: ``0.383 J/gK``
        * Weight: ``2200000 g/m3``
        * Thermal conductivity ``401.2 W/Km``

        """
        super(Copper, self).__init__(0.383, 2200000, 401.2)


class Petrol(Material):
    def __init__(self):
        """
        Implementation of petrol:

        * Thermal capacity: ``2.14 J/gK``
        * Weight: ``881000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Petrol, self).__init__(2.14, 881000, None)


class Wax(Material):
    def __init__(self):
        """
        Implementation of wax:

        * Thermal capacity: ``3.43 J/gK``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``unknown (None)``

        """
        super(Wax, self).__init__(3.43, None, None)


class Sandstone(Material):
    def __init__(self):
        """
        Implementation of sandstone:

        * Thermal capacity: ``0.92 J/gK``
        * Weight: ``2323000 g/m3``
        * Thermal conductivity ``2.5 W/Km``

        """
        super(Sandstone, self).__init__(0.92, 2323000, 2.5)


class Cobalt(Material):
    def __init__(self):
        """
        Implementation of cobalt:

        * Thermal capacity: ``0.46 J/gK``
        * Weight: ``8900000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Cobalt, self).__init__(0.46, 8900000, None)


class Zinc(Material):
    def __init__(self):
        """
        Implementation of zinc:

        * Thermal capacity: ``0.38 J/gK``
        * Weight: ``0.38 g/m3``
        * Thermal conductivity ``11 W/Km``

        """
        super(Zinc, self).__init__(0.38, 0.38, 11)


class Marple(Material):
    def __init__(self):
        """
        Implementation of marple:

        * Thermal capacity: ``0.88 J/gK``
        * Weight: ``2563000 g/m3``
        * Thermal conductivity ``2.08 W/Km``

        """
        super(Marple, self).__init__(0.88, 2563000, 2.08)


class Granite(Material):
    def __init__(self):
        """
        Implementation of granite:

        * Thermal capacity: ``0.79 J/gK``
        * Weight: ``2400000 g/m3``
        * Thermal conductivity ``2.855 W/Km``

        """
        super(Granite, self).__init__(0.79, 2400000, 2.855)


class Silk(Material):
    def __init__(self):
        """
        Implementation of silk:

        * Thermal capacity: ``1.38 J/gK``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``unknown (None)``

        """
        super(Silk, self).__init__(1.38, None, None)


class Hydrogen(Material):
    def __init__(self):
        """
        Implementation of hydrogen:

        * Thermal capacity: ``14.32 J/gK``
        * Weight: ``69600 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Hydrogen, self).__init__(14.32, 69600, None)


class HardBrick(Material):
    def __init__(self):
        """
        Implementation of hard brick:

        * Thermal capacity: ``1 J/gK``
        * Weight: ``2403000 g/m3``
        * Thermal conductivity ``1.31 W/Km``

        """
        super(HardBrick, self).__init__(1, 2403000, 1.31)


class Platinum(Material):
    def __init__(self):
        """
        Implementation of platinum:

        * Thermal capacity: ``0.13 J/gK``
        * Weight: ``21450000 g/m3``
        * Thermal conductivity ``71.61 W/Km``

        """
        super(Platinum, self).__init__(0.13, 21450000, 71.61)


class Aluminium(Material):
    def __init__(self):
        """
        Implementation of aluminium:

        * Thermal capacity: ``0.896 J/gK``
        * Weight: ``1522000 g/m3``
        * Thermal conductivity ``236.9 W/Km``

        """
        super(Aluminium, self).__init__(0.896, 1522000, 236.9)


class ArtificialWool(Material):
    def __init__(self):
        """
        Implementation of artificial wool:

        * Thermal capacity: ``1.357 J/gK``
        * Weight: ``1314000 g/m3``
        * Thermal conductivity ``0.049 W/Km``

        """
        super(ArtificialWool, self).__init__(1.357, 1314000, 0.049)


class Tar(Material):
    def __init__(self):
        """
        Implementation of tar:

        * Thermal capacity: ``1.47 J/gK``
        * Weight: ``1153000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Tar, self).__init__(1.47, 1153000, None)


class Chromium(Material):
    def __init__(self):
        """
        Implementation of chromium:

        * Thermal capacity: ``0.5 J/gK``
        * Weight: ``6856000 g/m3``
        * Thermal conductivity ``93.93 W/Km``

        """
        super(Chromium, self).__init__(0.5, 6856000, 93.93)


class Slate(Material):
    def __init__(self):
        """
        Implementation of slate:

        * Thermal capacity: ``0.76 J/gK``
        * Weight: ``2691000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Slate, self).__init__(0.76, 2691000, None)


class DryEarth(Material):
    def __init__(self):
        """
        Implementation of dry earth:

        * Thermal capacity: ``1.26 J/gK``
        * Weight: ``1249000 g/m3``
        * Thermal conductivity ``0.864 W/Km``

        """
        super(DryEarth, self).__init__(1.26, 1249000, 0.864)


class Rubber(Material):
    def __init__(self):
        """
        Implementation of rubber:

        * Thermal capacity: ``2.01 J/gK``
        * Weight: ``1522000 g/m3``
        * Thermal conductivity ``0.16 W/Km``

        """
        super(Rubber, self).__init__(2.01, 1522000, 0.16)


class Concrete(Material):
    def __init__(self):
        """
        Implementation of concrete:

        * Thermal capacity: ``0.75 J/gK``
        * Weight: ``2403000 g/m3``
        * Thermal conductivity ``1.04 W/Km``

        """
        super(Concrete, self).__init__(0.75, 2403000, 1.04)


class Pvc(Material):
    def __init__(self):
        """
        Implementation of pvc:

        * Thermal capacity: ``0.88 J/gK``
        * Weight: ``1200000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Pvc, self).__init__(0.88, 1200000, None)


class Paper(Material):
    def __init__(self):
        """
        Implementation of paper:

        * Thermal capacity: ``1.336 J/gK``
        * Weight: ``1201000 g/m3``
        * Thermal conductivity ``0.05 W/Km``

        """
        super(Paper, self).__init__(1.336, 1201000, 0.05)


class Graphite(Material):
    def __init__(self):
        """
        Implementation of graphite:

        * Thermal capacity: ``0.71 J/gK``
        * Weight: ``2070000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Graphite, self).__init__(0.71, 2070000, None)


class Iron(Material):
    def __init__(self):
        """
        Implementation of iron:

        * Thermal capacity: ``0.452 J/gK``
        * Weight: ``2500000 g/m3``
        * Thermal conductivity ``80.43 W/Km``

        """
        super(Iron, self).__init__(0.452, 2500000, 80.43)


class Clay(Material):
    def __init__(self):
        """
        Implementation of clay:

        * Thermal capacity: ``0.92 J/gK``
        * Weight: ``1073000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Clay, self).__init__(0.92, 1073000, None)


class GraphiteCarbon(Material):
    def __init__(self):
        """
        Implementation of graphite carbon:

        * Thermal capacity: ``0.71 J/gK``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``unknown (None)``

        """
        super(GraphiteCarbon, self).__init__(0.71, None, None)


class Salt(Material):
    def __init__(self):
        """
        Implementation of salt:

        * Thermal capacity: ``0.88 J/gK``
        * Weight: ``1000000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Salt, self).__init__(0.88, 1000000, None)


class Mercury(Material):
    def __init__(self):
        """
        Implementation of mercury:

        * Thermal capacity: ``0.14 J/gK``
        * Weight: ``13534000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Mercury, self).__init__(0.14, 13534000, None)


class Charcoal(Material):
    def __init__(self):
        """
        Implementation of charcoal:

        * Thermal capacity: ``1 J/gK``
        * Weight: ``208000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Charcoal, self).__init__(1, 208000, None)


class Oil(Material):
    def __init__(self):
        """
        Implementation of oil:

        * Thermal capacity: ``1.67 J/gK``
        * Weight: ``942000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Oil, self).__init__(1.67, 942000, None)


class Nickel(Material):
    def __init__(self):
        """
        Implementation of nickel:

        * Thermal capacity: ``0.461 J/gK``
        * Weight: ``8666000 g/m3``
        * Thermal conductivity ``90.95 W/Km``

        """
        super(Nickel, self).__init__(0.461, 8666000, 90.95)


class Silicone(Material):
    def __init__(self):
        """
        Implementation of silicone:

        * Thermal capacity: ``0.75 J/gK``
        * Weight: ``2330000 g/m3``
        * Thermal conductivity ``0.3 W/Km``

        """
        super(Silicone, self).__init__(0.75, 2330000, 0.3)


class DryCement(Material):
    def __init__(self):
        """
        Implementation of dry cement:

        * Thermal capacity: ``1.55 J/gK``
        * Weight: ``1506000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(DryCement, self).__init__(1.55, 1506000, None)


class Cork(Material):
    def __init__(self):
        """
        Implementation of cork:

        * Thermal capacity: ``1.9 J/gK``
        * Weight: ``240000 g/m3``
        * Thermal conductivity ``0.0435 W/Km``

        """
        super(Cork, self).__init__(1.9, 240000, 0.0435)


class Chalk(Material):
    def __init__(self):
        """
        Implementation of chalk:

        * Thermal capacity: ``0.9 J/gK``
        * Weight: ``2499000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Chalk, self).__init__(0.9, 2499000, None)


class Gypsum(Material):
    def __init__(self):
        """
        Implementation of gypsum:

        * Thermal capacity: ``1.09 J/gK``
        * Weight: ``2787000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Gypsum, self).__init__(1.09, 2787000, None)


class Wood(Material):
    def __init__(self):
        """
        Implementation of wood:

        * Thermal capacity: ``2 J/gK``
        * Weight: ``500000 g/m3``
        * Thermal conductivity ``0.14 W/Km``

        """
        super(Wood, self).__init__(2, 500000, 0.14)


class GlassWool(Material):
    def __init__(self):
        """
        Implementation of glass wool:

        * Thermal capacity: ``0.67 J/gK``
        * Weight: ``25000 g/m3``
        * Thermal conductivity ``0.04 W/Km``

        """
        super(GlassWool, self).__init__(0.67, 25000, 0.04)


class Butane(Material):
    def __init__(self):
        """
        Implementation of butane:

        * Thermal capacity: ``1.658 J/gK``
        * Weight: ``2006 g/m3``
        * Thermal conductivity ``0.01607 W/Km``

        """
        super(Butane, self).__init__(1.658, 2006, 0.01607)


class Tungsten(Material):
    def __init__(self):
        """
        Implementation of tungsten:

        * Thermal capacity: ``0.134 J/gK``
        * Weight: ``19220000 g/m3``
        * Thermal conductivity ``174.2 W/Km``

        """
        super(Tungsten, self).__init__(0.134, 19220000, 174.2)


class Air(Material):
    def __init__(self):
        """
        Implementation of air:

        * Thermal capacity: ``1.005 J/gK``
        * Weight: ``1200 g/m3``
        * Thermal conductivity ``0.02587 W/Km``

        """
        super(Air, self).__init__(1.005, 1200, 0.02587)


class Helium(Material):
    def __init__(self):
        """
        Implementation of helium:

        * Thermal capacity: ``5.193 J/gK``
        * Weight: ``138000 g/m3``
        * Thermal conductivity ``0.1535 W/Km``

        """
        super(Helium, self).__init__(5.193, 138000, 0.1535)


class Silver(Material):
    def __init__(self):
        """
        Implementation of silver:

        * Thermal capacity: ``0.23 J/gK``
        * Weight: ``10500000 g/m3``
        * Thermal conductivity ``429.0 W/Km``

        """
        super(Silver, self).__init__(0.23, 10500000, 429.0)


class Diamond(Material):
    def __init__(self):
        """
        Implementation of diamond:

        * Thermal capacity: ``0.63 J/gK``
        * Weight: ``3510000 g/m3``
        * Thermal conductivity ``2.2 W/Km``

        """
        super(Diamond, self).__init__(0.63, 3510000, 2.2)


class Lead(Material):
    def __init__(self):
        """
        Implementation of lead:

        * Thermal capacity: ``0.129 J/gK``
        * Weight: ``11389000 g/m3``
        * Thermal conductivity ``35.33 W/Km``

        """
        super(Lead, self).__init__(0.129, 11389000, 35.33)


class Asphalt(Material):
    def __init__(self):
        """
        Implementation of asphalt:

        * Thermal capacity: ``0.92 J/gK``
        * Weight: ``721000 g/m3``
        * Thermal conductivity ``0.75 W/Km``

        """
        super(Asphalt, self).__init__(0.92, 721000, 0.75)


class LightConcrete(Material):
    def __init__(self):
        """
        Implementation of light concrete:

        * Thermal capacity: ``0.96 J/gK``
        * Weight: ``1400000 g/m3``
        * Thermal conductivity ``0.42 W/Km``

        """
        super(LightConcrete, self).__init__(0.96, 1400000, 0.42)


class Plaster(Material):
    def __init__(self):
        """
        Implementation of plaster:

        * Thermal capacity: ``1.3 J/gK``
        * Weight: ``849000 g/m3``
        * Thermal conductivity ``0.478 W/Km``

        """
        super(Plaster, self).__init__(1.3, 849000, 0.478)


class CommonBrick(Material):
    def __init__(self):
        """
        Implementation of common brick:

        * Thermal capacity: ``0.9 J/gK``
        * Weight: ``1922000 g/m3``
        * Thermal conductivity ``1.26 W/Km``

        """
        super(CommonBrick, self).__init__(0.9, 1922000, 1.26)


class Water(Material):
    def __init__(self):
        """
        Implementation of water:

        * Thermal capacity: ``4.19 J/gK``
        * Weight: ``1000000 g/m3``
        * Thermal conductivity ``0.5985 W/Km``

        """
        super(Water, self).__init__(4.19, 1000000, 0.5985)


class Glass(Material):
    def __init__(self):
        """
        Implementation of glass:

        * Thermal capacity: ``0.84 J/gK``
        * Weight: ``2579000 g/m3``
        * Thermal conductivity ``1.0 W/Km``

        """
        super(Glass, self).__init__(0.84, 2579000, 1.0)


class DrySoil(Material):
    def __init__(self):
        """
        Implementation of dry soil:

        * Thermal capacity: ``0.8 J/gK``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``unknown (None)``

        """
        super(DrySoil, self).__init__(0.8, None, None)


class Ethanol(Material):
    def __init__(self):
        """
        Implementation of ethanol:

        * Thermal capacity: ``2.43 J/gK``
        * Weight: ``789000 g/m3``
        * Thermal conductivity ``0.1664 W/Km``

        """
        super(Ethanol, self).__init__(2.43, 789000, 0.1664)


class Carbon(Material):
    def __init__(self):
        """
        Implementation of carbon:

        * Thermal capacity: ``0.52 J/gK``
        * Weight: ``2146000 g/m3``
        * Thermal conductivity ``0.0146 W/Km``

        """
        super(Carbon, self).__init__(0.52, 2146000, 0.0146)


class WetSoil(Material):
    def __init__(self):
        """
        Implementation of wet soil:

        * Thermal capacity: ``1.48 J/gK``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``unknown (None)``

        """
        super(WetSoil, self).__init__(1.48, None, None)


class Wool(Material):
    def __init__(self):
        """
        Implementation of wool:

        * Thermal capacity: ``1.26 J/gK``
        * Weight: ``1314000 g/m3``
        * Thermal conductivity ``0.049 W/Km``

        """
        super(Wool, self).__init__(1.26, 1314000, 0.049)


class Porcelain(Material):
    def __init__(self):
        """
        Implementation of porcelain:

        * Thermal capacity: ``1.07 J/gK``
        * Weight: ``2403000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Porcelain, self).__init__(1.07, 2403000, None)


class DryLeather(Material):
    def __init__(self):
        """
        Implementation of dry leather:

        * Thermal capacity: ``1.5 J/gK``
        * Weight: ``945000 g/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(DryLeather, self).__init__(1.5, 945000, None)


class Aerogel(Material):
    def __init__(self):
        """
        Implementation of aerogel:

        * Thermal capacity: ``unknown (None)``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``0.003 W/Km``

        """
        super(Aerogel, self).__init__(None, None, 0.003)