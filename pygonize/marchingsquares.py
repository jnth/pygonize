#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Marching squares algorithm. """

from __future__ import print_function, division
import numpy
from shapely.geometry import Point, Polygon
from interp import interpolate


class Isoband(Polygon):
    """ Add methods and properties of shapely Polygon. """
    @property
    def z_min(self):
        """ Get minimal Z value of exterior ring. """
        return min([pts[2] for pts in list(self.exterior.coords)])

    @property
    def z_max(self):
        """ Get maximal Z value of exterior ring. """
        return max([pts[2] for pts in list(self.exterior.coords)])


def remove_duplicate_point(lp):
    """ Remove duplicate point.

    :param lp: list of points (shapely's PointZ object).
    :return: list of points (shapely's PointZ object).
    """
    lo = []
    for p in lp:  # for each element...
        if (p.x, p.y, p.z) not in lo:
            lo.append((p.x, p.y, p.z))
    out = [Point(x, y, z) for (x, y, z) in lo]
    return out


def get_idx_isoline(v, i):
    """ Index of marching square algorithm for an isoline.

    :param v: value for comparison.
    :param i: isoline value.
    :return: 0 if v < ref, 1 if v >= ref
    """
    if v < i:
        return 0
    return 1


def get_idx_isoband(v, mn, mx):
    """ Index of marching square algorithm for an isoband.

    :param v: value for comparison.
    :param mn: minimum value of an isoband.
    :param mx: maximal value of an isoband.
    :return: 0 if v <= mn, 2 if v >= mx, 1 if v between mn and mx.
    """
    if mn > mx:
        mn, mx = mx, mn  # inverse data

    if v <= mn:
        return 0
    if v >= mx:
        return 2
    return 1


def isoband_on_edge(p1, p2, mn, mx):
    """ Create 'isoband' points from two points.

    :param p1: 1st point (shapely.geometry.Point).
    :param p2: 2nd point (shapely.geometry.Point).
    :param mn: minimum value of an isoband.
    :param mx: maximal value of an isoband.
    :return: list of shapely.geometry.Point.
    """
    idx1 = get_idx_isoband(p1.z, mn, mx)
    idx2 = get_idx_isoband(p2.z, mn, mx)
    idx = "{0}{1}".format(idx1, idx2)
    
    if idx == '00' or idx == '22':
        return []

    if idx == '11':
        return [p1, p2]

    if idx == '01':
        return [interpolate(p1, p2, mn), p2]

    if idx == '10':
        return [p1, interpolate(p1, p2, mn)]

    if idx == '12':
        return [p1, interpolate(p1, p2, mx)]

    if idx == '21':
        return [interpolate(p1, p2, mx), p2]

    if idx == '02':
        return [interpolate(p1, p2, mn), interpolate(p1, p2, mx)]

    if idx == '20':
        return [interpolate(p1, p2, mx), interpolate(p1, p2, mn)]


def is_clockwise(p):
    """ Check if the polygon vertices are clockwise.
    Source: http://stackoverflow.com/a/1165943

    :param p: geometry.shapely.Polygon object.
    :return: boolean.
    """
    xy = numpy.array(p.exterior.coords.xy)
    x, y = xy[0, :], xy[1, :]
    v = ((numpy.roll(x, shift=-1) - x) * (numpy.roll(y, shift=-1) + y)).sum()

    if v < 0:
        return False
    return True


def make_polygon(*ps):
    """ Create polygon from a list of points.

    :param ps: list of shapely.geometry.Point
    :return: Isoband object
    """
    if len(ps) < 3:
        return None
    p = Isoband([e.coords[:][0] for e in ps])
    if not is_clockwise(p):
        p = Isoband(p.exterior.coords[::-1])
    return p


class SquareError(Exception):
    pass


class Square:
    def __init__(self, p1, p2, p3, p4):
        """ Define a square with four points.

            p1 +-----+ p2
               |     |
               |     |
            p4 +-----+ p3

        :param p1: upper-left point (shapely.geometry.Point object in 3 dimensions).
        :param p2: upper-right point (shapely.geometry.Point object in 3 dimensions).
        :param p3: lower-right point (shapely.geometry.Point object in 3 dimensions).
        :param p4: lower-left point (shapely.geometry.Point object in 3 dimensions).
        :return:
        """
        if not p1.has_z:
            raise SquareError("p1 has no z coordinate.")
        if not p2.has_z:
            raise SquareError("p2 has no z coordinate.")
        if not p3.has_z:
            raise SquareError("p3 has no z coordinate.")
        if not p4.has_z:
            raise SquareError("p4 has no z coordinate.")

        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

    @property
    def x(self):
        """ Get the X coordinates.

        :return: list.
        """
        return self.p1.x, self.p2.x, self.p3.x, self.p4.x

    @property
    def y(self):
        """ Get the Y coordinates.

        :return: list.
        """
        return self.p1.y, self.p2.y, self.p3.y, self.p4.y

    @property
    def z(self):
        """ Get the Z coordinates.

        :return:
        """
        return self.p1.z, self.p2.z, self.p3.z, self.p4.z

    @property
    def edges(self):
        """ Get the edge.

        :return: list of (pi, pe).
        """
        return [self.p1, self.p2], [self.p2, self.p3], [self.p3, self.p4], [self.p4, self.p1]

    @property
    def points(self):
        """ Get the list of points.

        :return: list of points.
        """
        return self.p1, self.p2, self.p3, self.p4

    @property
    def centralmean(self):
        """ Get the central data value (average of cornes).

        :return: number.
        """
        return numpy.array(self.z).mean()

    def isoband_classif(self, lvlmn, lvlmx):
        """ Calculating the ternary index of the square to find isoband.

        :param lvlmn: minimum of the isoband value.
        :param lvlmx: maximum of the isoband value.
        :return: string.
        """
        idxp = list()
        for p in self.points:
            idxp.append(get_idx_isoband(p.z, lvlmn, lvlmx))
        return "".join([str(e) for e in idxp])

    def vectorize_isoband(self, lvlmn, lvlmx):
        """ Vectorization of one isoband.

        :param lvlmn: minimum of the isoband value.
        :param lvlmx: maximum of the isoband value.
        :return: list of shapely.geometry.Polygon.
        """
        idx = self.isoband_classif(lvlmn, lvlmx)

        # Get points on the edge
        ps = []
        for pi, pe in self.edges:
            ps += isoband_on_edge(pi, pe, lvlmn, lvlmx)

        # Remove duplicate points
        ps = remove_duplicate_point(ps)

        # Create polygons
        if idx == '0101' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 6-sided
            return [make_polygon(*ps[0:3]), make_polygon(*ps[3:6])]

        elif idx == '1010' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 6-sided
            return [make_polygon(ps[0], ps[1], ps[5]), make_polygon(*ps[2:5])]

        elif idx == '2121' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 6-sided
            return [make_polygon(*ps[0:3]), make_polygon(*ps[3:6])]

        elif idx == '1212' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 6-sided
            return [make_polygon(ps[0], ps[1], ps[5]), make_polygon(*ps[2:5])]

        elif idx == '2120' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 7-sided
            return [make_polygon(*ps[0:3]), make_polygon(*ps[3:7])]

        elif idx == '2021' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 7-sided
            return [make_polygon(*ps[0:4]), make_polygon(*ps[4:7])]

        elif idx == '1202' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 7-sided
            return [make_polygon(ps[0], ps[1], ps[6]), make_polygon(*ps[2:6])]

        elif idx == '0212' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 7-sided
            return [make_polygon(ps[0], ps[1], ps[5], ps[6]), make_polygon(*ps[2:5])]

        elif idx == '0102' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 7-sided
            return [make_polygon(*ps[0:3]), make_polygon(*ps[3:7])]

        elif idx == '0201' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 7-sided
            return [make_polygon(*ps[0:4]), make_polygon(*ps[4:7])]

        elif idx == '1020' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 7-sided
            return [make_polygon(ps[0], ps[1], ps[6]), make_polygon(*ps[2:6])]

        elif idx == '2010' and not lvlmn <= self.centralmean <= lvlmx:  # saddles case, 7-sided
            return [make_polygon(ps[0], ps[1], ps[5], ps[6]), make_polygon(*ps[2:5])]

        elif idx == '2020' and self.centralmean < lvlmn:  # saddles case, 8-sided
            return [make_polygon(ps[0], ps[1], ps[6], ps[7]), make_polygon(*ps[2:6])]

        elif idx == '2020' and self.centralmean > lvlmx:  # saddles case, 8-sided
            return [make_polygon(*ps[0:4]), make_polygon(*ps[4:8])]

        elif idx == '0202' and self.centralmean < lvlmn:  # saddles case, 8-sided
            return [make_polygon(*ps[0:4]), make_polygon(*ps[4:8])]

        elif idx == '0202' and self.centralmean > lvlmx:  # saddles case, 8-sided
            return [make_polygon(ps[0], ps[1], ps[6], ps[7]), make_polygon(*ps[2:6])]

        else:  # regular case
            poly = make_polygon(*ps)
            return [poly] if poly else None

    def vectorize_isobands(self, levels):
        """ Vectorization of isobands.

        :param levels: list of levels.
        :return: list of shapely.geometry.Polygon.
        """
        polys = list()
        for lmn, lmx in zip(levels, levels[1:]):
            out = self.vectorize_isoband(lmn, lmx)
            if out is not None:
                polys += out
            del out
        return polys
