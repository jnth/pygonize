#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Test base class """


import unittest
from shapely.geometry import Point
import numpy
import shapefile
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except:
    pass


def prettify(val, ndigits=2):
    """ Pretty number format
    :param val:
    :param ndigits:
    :return:
    """
    if isinstance(val, int):
        return val
    if val % 1 == 0.0:
        return int(val)
    return round(val, ndigits=ndigits)

def ppolys(polys, output='stdout'):
    """ Print poly coordinates
    :param polys: shapely.geometry.Polygon or list of shapely.geometry.Polygon object.
    :param output: 'stdout' to print string, all other value to return string.
    :return: string.
    """
    if not isinstance(polys, list):
        polys = [polys]
    out = list()
    for poly in polys:
        out.append(str([[prettify(v) for v in e] for e in poly.exterior.coords[:]]))
    if output == 'stdout':
        print('\n'.join(out))
    else:
        return '\n'.join(out)


def figpolys(polys, x=None, y=None, fno=None):
    if not isinstance(polys, list):
        polys = [polys]

    fig, ax = plt.subplots(1, figsize=(6, 6))
    ax.set(aspect=1)
    for p in polys:
        color = numpy.random.rand(3, 1)
        mp = mpatches.Polygon(numpy.asarray(p.exterior)[:, 0:2], color=color, alpha=0.5)
        ax.add_patch(mp)
    if x is not None and y is not None:
        gx, gy = numpy.meshgrid(x, y)
        ax.set_xlim(x.min() - 5, x.max() + 5)
        ax.set_ylim(y.min() - 5, y.max() + 5)
        plt.plot(gx, gy, 'o', color='black')
    if fno:
        plt.savefig(fno)
    else:
        plt.show()


class PygonizeTest(unittest.TestCase):
    def valid_point(self, p, o):
        """ Validate Point object.
        :param p: shapely.geometry.Point object.
        :param o: tuple of (x, y, z) or Point object.
        """
        if not isinstance(o, Point):
            o = Point(*o)

        self.assertAlmostEqual(p.x, o.x, delta=0.1)
        self.assertAlmostEqual(p.y, o.y, delta=0.1)
        self.assertAlmostEqual(p.z, o.z, delta=0.1)

    def valid_poly(self, p, coo):
        """ Valid Polygon object (only the exterior ring).
        :param p: shapely.geometry.Polygon object.
        :param coo: list of (x, y, z).
        """
        coords = list(p.exterior.coords)
        self.assertEqual(len(coords), len(coo))
        msg = "differences between coordinates !\nlist1 = {c1}\nlist2 = {c2}".format(
            c1=str(coo), c2=ppolys(p, output='str'))
        for (x1, y1, z1), (x2, y2, z2) in zip(coords, coo):
            self.assertAlmostEqual(x1, x2, delta=0.1, msg=msg)
            self.assertAlmostEqual(y1, y2, delta=0.1, msg=msg)
            self.assertAlmostEqual(z1, z2, delta=0.1, msg=msg)

    def valid_list(self, l1, l2):
        """ Validate two list.
        :param l1: 1st list.
        :param l2: 2nd list.
        """
        self.assertEqual(len(l1), len(l2))
        for e1, e2 in zip(l1, l2):
            self.assertAlmostEqual(e1, e2, delta=0.1)

    def valid_with_file(self, polys, fn):
        """ Valid Polygon object with file containing coords.
        :param polys: list of polygons.
        :param fn: path of file.
        """
        v1 = ppolys(polys, output='').strip().replace('\r', '')
        v2 = open(fn, 'rb').read().strip().replace('\r', '')
        self.assertEqual(v1, v2)

    def valid_with_fig(self, polys, **kwargs):
        """ Create figure to a visual validation of polygons
        :param polys: list of polygons.
        :param kwargs: options.
        """
        ppolys(polys)  # print coordinate
        figpolys(polys, **kwargs)  # show figure
        
    def valid_with_gis(self, polys, fno):
        """ Create shapefile from polygons to validate with a GIS software.
        :param polys: list of polygons.
        """
        shp = shapefile.Writer(shapefile.POLYGON)
        shp.field('id', 'N', 10, 0)
        shp.field('lvl_min', 'N', 10, 0)
        shp.field('lvl_max', 'N', 10, 0)
        for i, p in enumerate(polys):
            lvl_min = min([e[2] for e in p.exterior.coords])
            lvl_max = max([e[2] for e in p.exterior.coords])
            shp.poly(parts=[[e[0:2] for e in p.exterior.coords]])
            shp.record(i, lvl_min, lvl_max)
        shp.save(fno)
