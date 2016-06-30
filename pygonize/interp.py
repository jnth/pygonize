#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Linear interpolation."""

from __future__ import print_function, division
from shapely.geometry import LineString


def interpolate(p1, p2, lvl):
    """Interpolate between two points from a level value.

    :param p1: 1st point (shapely's PointZ object).
    :param p2: 2nd point (shapely's PointZ object).
    :param lvl: level value.
    :return: point (shapely's PointZ object).
    """
    mn = min(p1.z, p2.z)
    mx = max(p1.z, p2.z)

    # Check
    if lvl < mn:
        return None
    if lvl > mx:
        return None

    if p1.z < p2.z:
        l = LineString((list(p1.coords)[0], list(p2.coords)[0]))
    else:
        l = LineString((list(p2.coords)[0], list(p1.coords)[0]))

    dist = (lvl - mn) / (mx - mn)
    return l.interpolate(dist, normalized=True)
