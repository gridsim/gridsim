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

        :param c: The thermal capacity in ``J/kgK``.
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
        The thermal capacity in **[J/kgK]**
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
        The thermal capacity in **[J/kgK]**
        In order to get the thermal capacity of an object, you only have to
        multiply this specific capacity with the object's mass in gram::

            # Calculate the thermal capacity of 1kg of air.
            t_cap = AIR().thermal_capacity

        .. note::
            Source: http://www.engineeringtoolbox.com/specific-heat-solids-d_154.html

        :return: the thermal capacity
        :rtype: thermal capacity, see :mod:`gridsim.unit`
        """
        return self._c

    @property
    def weight(self):
        """
        The weight of the material in **[kg/m3]**.

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

        * Thermal capacity: ``490 J/kgK``
        * Weight: ``7700 kg/m3``
        * Thermal conductivity ``46.6 W/Km``

        """
        super(Steel, self).__init__(490., 7700., 46.6)


class Stone(Material):
    def __init__(self):
        """
        Implementation of stone:

        * Thermal capacity: ``750 J/kgK``
        * Weight: ``2515 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Stone, self).__init__(750., 2515., None)


class Gold(Material):
    def __init__(self):
        """
        Implementation of gold:

        * Thermal capacity: ``130 J/kgK``
        * Weight: ``19200 kg/m3``
        * Thermal conductivity ``317.1 W/Km``

        """
        super(Gold, self).__init__(130., 19200., 317.1)


class Copper(Material):
    def __init__(self):
        """
        Implementation of copper:

        * Thermal capacity: ``383 J/kgK``
        * Weight: ``2200 kg/m3``
        * Thermal conductivity ``401.2 W/Km``

        """
        super(Copper, self).__init__(383., 2200., 401.2)


class Petrol(Material):
    def __init__(self):
        """
        Implementation of petrol:

        * Thermal capacity: ``2140 J/kgK``
        * Weight: ``881 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Petrol, self).__init__(2140., 881., None)


class Wax(Material):
    def __init__(self):
        """
        Implementation of wax:

        * Thermal capacity: ``3430 J/kgK``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``unknown (None)``

        """
        super(Wax, self).__init__(3430., None, None)


class Sandstone(Material):
    def __init__(self):
        """
        Implementation of sandstone:

        * Thermal capacity: ``920 J/kgK``
        * Weight: ``2323 kg/m3``
        * Thermal conductivity ``2.5 W/Km``

        """
        super(Sandstone, self).__init__(920., 2323., 2.5)


class Cobalt(Material):
    def __init__(self):
        """
        Implementation of cobalt:

        * Thermal capacity: ``460 J/kgK``
        * Weight: ``8900 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Cobalt, self).__init__(460., 8900., None)


class Zinc(Material):
    def __init__(self):
        """
        Implementation of zinc:

        * Thermal capacity: ``380 J/kgK``
        * Weight: ``7140 kg/m3``
        * Thermal conductivity ``11 W/Km``

        """
        super(Zinc, self).__init__(380., 7140., 11.)


class Marple(Material):
    def __init__(self):
        """
        Implementation of marple:

        * Thermal capacity: ``880 J/kgK``
        * Weight: ``2563 kg/m3``
        * Thermal conductivity ``2.08 W/Km``

        """
        super(Marple, self).__init__(880., 2563., 2.08)


class Granite(Material):
    def __init__(self):
        """
        Implementation of granite:

        * Thermal capacity: ``790 J/kgK``
        * Weight: ``2400 kg/m3``
        * Thermal conductivity ``2.855 W/Km``

        """
        super(Granite, self).__init__(790., 2400, 2.855)


class Silk(Material):
    def __init__(self):
        """
        Implementation of silk:

        * Thermal capacity: ``1380 J/kgK``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``unknown (None)``

        """
        super(Silk, self).__init__(1380., None, None)


class Hydrogen(Material):
    def __init__(self):
        """
        Implementation of hydrogen:

        * Thermal capacity: ``14320 J/kgK``
        * Weight: ``69600 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Hydrogen, self).__init__(14320., 69.6, None)


class HardBrick(Material):
    def __init__(self):
        """
        Implementation of hard brick:

        * Thermal capacity: ``1000 J/kgK``
        * Weight: ``2403 kg/m3``
        * Thermal conductivity ``1.31 W/Km``

        """
        super(HardBrick, self).__init__(1000., 2403., 1.31)


class Platinum(Material):
    def __init__(self):
        """
        Implementation of platinum:

        * Thermal capacity: ``130 J/kgK``
        * Weight: ``21450 kg/m3``
        * Thermal conductivity ``71.61 W/Km``

        """
        super(Platinum, self).__init__(130., 21450., 71.61)


class Aluminium(Material):
    def __init__(self):
        """
        Implementation of aluminium:

        * Thermal capacity: ``896 J/kgK``
        * Weight: ``1522 kg/m3``
        * Thermal conductivity ``236.9 W/Km``

        """
        super(Aluminium, self).__init__(896., 1522., 236.9)


class ArtificialWool(Material):
    def __init__(self):
        """
        Implementation of artificial wool:

        * Thermal capacity: ``1357 J/kgK``
        * Weight: ``1314 kg/m3``
        * Thermal conductivity ``0.049 W/Km``

        """
        super(ArtificialWool, self).__init__(1357., 1314., 0.049)


class Tar(Material):
    def __init__(self):
        """
        Implementation of tar:

        * Thermal capacity: ``1470 J/kgK``
        * Weight: ``1153 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Tar, self).__init__(1470., 1153., None)


class Chromium(Material):
    def __init__(self):
        """
        Implementation of chromium:

        * Thermal capacity: ``500 J/kgK``
        * Weight: ``6856 kg/m3``
        * Thermal conductivity ``93.93 W/Km``

        """
        super(Chromium, self).__init__(500., 6856., 93.93)


class Slate(Material):
    def __init__(self):
        """
        Implementation of slate:

        * Thermal capacity: ``760 J/kgK``
        * Weight: ``2691 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Slate, self).__init__(760., 2691., None)


class DryEarth(Material):
    def __init__(self):
        """
        Implementation of dry earth:

        * Thermal capacity: ``1260 J/kgK``
        * Weight: ``1249 kg/m3``
        * Thermal conductivity ``0.864 W/Km``

        """
        super(DryEarth, self).__init__(1260., 1249., 0.864)


class Rubber(Material):
    def __init__(self):
        """
        Implementation of rubber:

        * Thermal capacity: ``2010 J/kgK``
        * Weight: ``1522 kg/m3``
        * Thermal conductivity ``0.16 W/Km``

        """
        super(Rubber, self).__init__(2010., 1522., 0.16)


class Concrete(Material):
    def __init__(self):
        """
        Implementation of concrete:

        * Thermal capacity: ``750 J/kgK``
        * Weight: ``2403 kg/m3``
        * Thermal conductivity ``1.04 W/Km``

        """
        super(Concrete, self).__init__(750., 2403., 1.04)


class Pvc(Material):
    def __init__(self):
        """
        Implementation of pvc:

        * Thermal capacity: ``880 J/kgK``
        * Weight: ``1200 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Pvc, self).__init__(880., 1200., None)


class Paper(Material):
    def __init__(self):
        """
        Implementation of paper:

        * Thermal capacity: ``1336 J/kgK``
        * Weight: ``1201 kg/m3``
        * Thermal conductivity ``0.05 W/Km``

        """
        super(Paper, self).__init__(1336., 1201., 0.05)


class Graphite(Material):
    def __init__(self):
        """
        Implementation of graphite:

        * Thermal capacity: ``710 J/kgK``
        * Weight: ``2070 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Graphite, self).__init__(710., 2070., None)


class Iron(Material):
    def __init__(self):
        """
        Implementation of iron:

        * Thermal capacity: ``452 J/kgK``
        * Weight: ``2500 kg/m3``
        * Thermal conductivity ``80.43 W/Km``

        """
        super(Iron, self).__init__(452., 2500., 80.43)


class Clay(Material):
    def __init__(self):
        """
        Implementation of clay:

        * Thermal capacity: ``920 J/kgK``
        * Weight: ``1073 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Clay, self).__init__(920., 1073., None)


class GraphiteCarbon(Material):
    def __init__(self):
        """
        Implementation of graphite carbon:

        * Thermal capacity: ``710 J/kgK``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``unknown (None)``

        """
        super(GraphiteCarbon, self).__init__(710., None, None)


class Salt(Material):
    def __init__(self):
        """
        Implementation of salt:

        * Thermal capacity: ``880 J/kgK``
        * Weight: ``1000 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Salt, self).__init__(880., 1000., None)


class Mercury(Material):
    def __init__(self):
        """
        Implementation of mercury:

        * Thermal capacity: ``140 J/kgK``
        * Weight: ``13534 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Mercury, self).__init__(140., 13534., None)


class Charcoal(Material):
    def __init__(self):
        """
        Implementation of charcoal:

        * Thermal capacity: ``1000 J/kgK``
        * Weight: ``208 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Charcoal, self).__init__(1000., 208., None)


class Oil(Material):
    def __init__(self):
        """
        Implementation of oil:

        * Thermal capacity: ``1670. J/kgK``
        * Weight: ``942 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Oil, self).__init__(1670., 942., None)


class Nickel(Material):
    def __init__(self):
        """
        Implementation of nickel:

        * Thermal capacity: ``461 J/kgK``
        * Weight: ``8666 kg/m3``
        * Thermal conductivity ``90.95 W/Km``

        """
        super(Nickel, self).__init__(461., 8666., 90.95)


class Silicone(Material):
    def __init__(self):
        """
        Implementation of silicone:

        * Thermal capacity: ``750 J/kgK``
        * Weight: ``2330 kg/m3``
        * Thermal conductivity ``0.3 W/Km``

        """
        super(Silicone, self).__init__(750, 2330., 0.3)


class DryCement(Material):
    def __init__(self):
        """
        Implementation of dry cement:

        * Thermal capacity: ``1550 J/kgK``
        * Weight: ``1506 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(DryCement, self).__init__(1550., 1506., None)


class Cork(Material):
    def __init__(self):
        """
        Implementation of cork:

        * Thermal capacity: ``1900 J/kgK``
        * Weight: ``240 kg/m3``
        * Thermal conductivity ``0.0435 W/Km``

        """
        super(Cork, self).__init__(1900., 240., 0.0435)


class Chalk(Material):
    def __init__(self):
        """
        Implementation of chalk:

        * Thermal capacity: ``900 J/kgK``
        * Weight: ``2499 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Chalk, self).__init__(900., 2499., None)


class Gypsum(Material):
    def __init__(self):
        """
        Implementation of gypsum:

        * Thermal capacity: ``1090 J/kgK``
        * Weight: ``2787 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Gypsum, self).__init__(1090., 2787., None)


class Wood(Material):
    def __init__(self):
        """
        Implementation of wood:

        * Thermal capacity: ``2000 J/kgK``
        * Weight: ``500 kg/m3``
        * Thermal conductivity ``0.14 W/Km``

        """
        super(Wood, self).__init__(2000., 500., 0.14)


class GlassWool(Material):
    def __init__(self):
        """
        Implementation of glass wool:

        * Thermal capacity: ``670 J/kgK``
        * Weight: ``25 kg/m3``
        * Thermal conductivity ``0.04 W/Km``

        """
        super(GlassWool, self).__init__(670., 25., 0.04)


class Butane(Material):
    def __init__(self):
        """
        Implementation of butane:

        * Thermal capacity: ``1658 J/kgK``
        * Weight: ``2.006 kg/m3``
        * Thermal conductivity ``0.01607 W/Km``

        """
        super(Butane, self).__init__(1658., 2.006, 0.01607)


class Tungsten(Material):
    def __init__(self):
        """
        Implementation of tungsten:

        * Thermal capacity: ``134 J/kgK``
        * Weight: ``19220 kg/m3``
        * Thermal conductivity ``174.2 W/Km``

        """
        super(Tungsten, self).__init__(134., 19220., 174.2)


class Air(Material):
    def __init__(self):
        """
        Implementation of air:

        * Thermal capacity: ``1005 J/kgK``
        * Weight: ``1.200 kg/m3``
        * Thermal conductivity ``0.02587 W/Km``

        """
        super(Air, self).__init__(1005., 1.2, 0.02587)


class Helium(Material):
    def __init__(self):
        """
        Implementation of helium:

        * Thermal capacity: ``5193 J/kgK``
        * Weight: ``138 kg/m3``
        * Thermal conductivity ``0.1535 W/Km``

        """
        super(Helium, self).__init__(5193., 138., 0.1535)


class Silver(Material):
    def __init__(self):
        """
        Implementation of silver:

        * Thermal capacity: ``230 J/kgK``
        * Weight: ``10500 kg/m3``
        * Thermal conductivity ``429.0 W/Km``

        """
        super(Silver, self).__init__(230., 10500., 429.0)


class Diamond(Material):
    def __init__(self):
        """
        Implementation of diamond:

        * Thermal capacity: ``630 J/kgK``
        * Weight: ``3510 kg/m3``
        * Thermal conductivity ``2.2 W/Km``

        """
        super(Diamond, self).__init__(630., 3510., 2.2)


class Lead(Material):
    def __init__(self):
        """
        Implementation of lead:

        * Thermal capacity: ``129 J/kgK``
        * Weight: ``11389 kg/m3``
        * Thermal conductivity ``35.33 W/Km``

        """
        super(Lead, self).__init__(129., 11389., 35.33)


class Asphalt(Material):
    def __init__(self):
        """
        Implementation of asphalt:

        * Thermal capacity: ``920. J/kgK``
        * Weight: ``721 kg/m3``
        * Thermal conductivity ``0.75 W/Km``

        """
        super(Asphalt, self).__init__(920., 721., 0.75)


class LightConcrete(Material):
    def __init__(self):
        """
        Implementation of light concrete:

        * Thermal capacity: ``960 J/kgK``
        * Weight: ``1400 kg/m3``
        * Thermal conductivity ``0.42 W/Km``

        """
        super(LightConcrete, self).__init__(960., 1400., 0.42)


class Plaster(Material):
    def __init__(self):
        """
        Implementation of plaster:

        * Thermal capacity: ``1300 J/kgK``
        * Weight: ``849 kg/m3``
        * Thermal conductivity ``0.478 W/Km``

        """
        super(Plaster, self).__init__(1300., 849., 0.478)


class CommonBrick(Material):
    def __init__(self):
        """
        Implementation of common brick:

        * Thermal capacity: ``900 J/kgK``
        * Weight: ``1922 kg/m3``
        * Thermal conductivity ``1.26 W/Km``

        """
        super(CommonBrick, self).__init__(900., 1922., 1.26)


class Water(Material):
    def __init__(self):
        """
        Implementation of water:

        * Thermal capacity: ``4190 J/kgK``
        * Weight: ``1000 kg/m3``
        * Thermal conductivity ``0.5985 W/Km``

        """
        super(Water, self).__init__(4190., 1000., 0.5985)


class Glass(Material):
    def __init__(self):
        """
        Implementation of glass:

        * Thermal capacity: ``840 J/kgK``
        * Weight: ``2579 kg/m3``
        * Thermal conductivity ``1.0 W/Km``

        """
        super(Glass, self).__init__(840., 2579., 1.0)


class DrySoil(Material):
    def __init__(self):
        """
        Implementation of dry soil:

        * Thermal capacity: ``800 J/kgK``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``unknown (None)``

        """
        super(DrySoil, self).__init__(800., None, None)


class Ethanol(Material):
    def __init__(self):
        """
        Implementation of ethanol:

        * Thermal capacity: ``2430 J/kgK``
        * Weight: ``789 kg/m3``
        * Thermal conductivity ``0.1664 W/Km``

        """
        super(Ethanol, self).__init__(2430., 789., 0.1664)


class Carbon(Material):
    def __init__(self):
        """
        Implementation of carbon:

        * Thermal capacity: ``520 J/kgK``
        * Weight: ``2146 kg/m3``
        * Thermal conductivity ``0.0146 W/Km``

        """
        super(Carbon, self).__init__(520., 2146., 0.0146)


class WetSoil(Material):
    def __init__(self):
        """
        Implementation of wet soil:

        * Thermal capacity: ``1480 J/kgK``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``unknown (None)``

        """
        super(WetSoil, self).__init__(1480., None, None)


class Wool(Material):
    def __init__(self):
        """
        Implementation of wool:

        * Thermal capacity: ``1260 J/kgK``
        * Weight: ``1314 kg/m3``
        * Thermal conductivity ``0.049 W/Km``

        """
        super(Wool, self).__init__(1260., 1314., 0.049)


class Porcelain(Material):
    def __init__(self):
        """
        Implementation of porcelain:

        * Thermal capacity: ``1070 J/kgK``
        * Weight: ``2403 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(Porcelain, self).__init__(1070., 2403., None)


class DryLeather(Material):
    def __init__(self):
        """
        Implementation of dry leather:

        * Thermal capacity: ``1500 J/kgK``
        * Weight: ``945 kg/m3``
        * Thermal conductivity ``unknown (None)``

        """
        super(DryLeather, self).__init__(1500., 945., None)


class Aerogel(Material):
    def __init__(self):
        """
        Implementation of aerogel:

        * Thermal capacity: ``unknown (None)``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``0.003 W/Km``

        """
        super(Aerogel, self).__init__(None, None, 0.003)