#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Pygonize: polygonize raster data. """


import math
import multiprocessing
from . import marchingsquares
import numpy
from osgeo import gdal
from shapely.geometry import Point
import shapefile


def vectorize_isoband_worker(wp1, wp2, wp3, wp4, wlevels):
    """ Function to be used by the multiprocessing module.
    """
    fsq = marchingsquares.Square(wp1, wp2, wp3, wp4)
    out = fsq.vectorize_isobands(wlevels)
    del fsq
    return out


def precision_and_scale(x):
    """ Get precision and scale of a number.
    Source: http://stackoverflow.com/a/3019027

    :param x: number.
    :return: precision, scale
    """
    max_digits = 14
    int_part = int(abs(x))
    magnitude = 1 if int_part == 0 else int(math.log10(int_part)) + 1
    if magnitude >= max_digits:
        return magnitude, 0
    frac_part = abs(x) - int_part
    multiplier = 10 ** (max_digits - magnitude)
    frac_digits = multiplier + int(multiplier * frac_part + 0.5)
    while frac_digits % 10 == 0:
        frac_digits /= 10
    scale = int(math.log10(frac_digits))
    return magnitude + scale, scale


def limits(x, l):
    """ Get limits of a value 'x' inside a list 'l'.

    :param x: value.
    :param l: list of values.
    :return: (min, max) or None
    """
    l = sorted(l)
    if x < min(l):
        return None  # outside the list
    if x > max(l):
        return None  # outside the list
    if x in l:
        return x, x  # exact value
    mn = max([i for (i, j) in zip(l, [x]*len(l)) if j > i])
    mx = min([i for (i, j) in zip(l, [x]*len(l)) if j < i])
    return mn, mx


class Pygonize:
    def __init__(self):
        self.lx = None
        self.ly = None
        self.z = None

    def read_array(self, x, y, z):
        """ Read data from numpy arrays.
        :param x: X coordinates as 1 axis array.
        :param y: Y coordinates as 1 axis array.
        :param z: Z coordinates with (y, x) shape.
        """
        # Check
        assert len(x.shape) == 1
        assert len(y.shape) == 1
        assert len(z.shape) == 2
        assert z.shape == (y.shape[0], x.shape[0])

        self.lx = x
        self.ly = y
        self.z = z

    def read_raster(self, fn, band=1):
        """ Read raster data.
        :param fn: path of raster.
        :param band: band number.
        """
        dst = gdal.Open(fn)
        self.z = dst.GetRasterBand(band).ReadAsArray()
        xmin, dx, _, ymin, _, dy = dst.GetGeoTransform()  # geographic informations
        dst = None  # close dataset

        ny, nx = self.z.shape
        self.lx = numpy.arange(xmin + dx / 2, xmin + nx * dx, dx)
        self.ly = numpy.arange(ymin + dy / 2, ymin + ny * dy, dy)

    def vectorize_isobands(self, levels):
        """ Vectorization of isobands.

        :param levels: list of levels.
        :return: list of shapely.geometry.Polygon.
        """
        levels = sorted(levels)
        pool = multiprocessing.Pool()  # start a pool of worker on the local machine
        outs = list()  # list of multiprocessing.pool.AsyncResult

        ny, nx = self.z.shape

        # Grid of X and Y
        x, y = numpy.meshgrid(self.lx, self.ly)

        # Split dataset into squares and vectorize
        for iy in range(ny - 1):
            for ix in range(nx - 1):
                part_z = self.z[iy:iy+2, ix:ix+2]
                part_x = x[iy:iy+2, ix:ix+2]
                part_y = y[iy:iy+2, ix:ix+2]

                p1 = Point(part_x[0, 0], part_y[0, 0], part_z[0, 0])
                p2 = Point(part_x[0, 1], part_y[0, 1], part_z[0, 1])
                p3 = Point(part_x[1, 1], part_y[1, 1], part_z[1, 1])
                p4 = Point(part_x[1, 0], part_y[1, 0], part_z[1, 0])

                w = pool.apply_async(vectorize_isoband_worker, args=(p1, p2, p3, p4, levels))  # create task
                outs.append(w)

        # Wait for all process to be terminated
        pool.close()
        pool.join()

        # Join all resulting polygons
        polys = list()
        for w in outs:
            polys += w.get()

        return polys

    def write_shapefile(self, levels, fn):
        """ Vectorization of isobands and save result into shapefile.

        :param levels: list of levels.
        :param fn: path of shapefile.
        """
        levels = sorted(levels)
        polys = self.vectorize_isobands(levels)
        inf = map(precision_and_scale, levels)  # precision and scale of levels
        precision, scale = max(inf)

        # Writing shapefile
        w = shapefile.Writer(shapeType=shapefile.POLYGON)
        w.field('id', 'N')
        w.field('lvlmn', 'N', size=precision, decimal=scale)
        w.field('lvlmx', 'N', size=precision, decimal=scale)

        for ipoly, poly in enumerate(polys, start=1):

            # Find lvl min and max
            zs = numpy.array([z for (x, y, z) in poly.exterior.coords[:]])
            zmin, zmax = zs.min(), zs.max()

            # Limits from levels
            zmn1, zmn2 = limits(zmin, levels)
            zmx1, zmx2 = limits(zmax, levels)
            zmin = min(zmn1, zmn2)
            zmax = max(zmx1, zmx2)

            zmin = format(zmin, '.{scale}f'.format(scale=scale))  # convert with specific scale
            zmax = format(zmax, '.{scale}f'.format(scale=scale))
            del zs

            w.poly(parts=poly.__geo_interface__['coordinates'])
            w.record(ipoly, zmin, zmax)

        w.save(fn)


