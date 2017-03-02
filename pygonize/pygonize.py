#!/usr/bin/env python3
# coding: utf-8

"""Pygonize: polygonize raster data."""


import math
import multiprocessing
from . import marchingsquares
import numpy
from osgeo import gdal
from shapely.geometry import Point
import shapefile
import logging


log = logging.getLogger(__name__)


def vectorize_isoband_worker(wp1, wp2, wp3, wp4, wlevels):
    """Function to be used by the multiprocessing module."""
    fsq = marchingsquares.Square(wp1, wp2, wp3, wp4)
    out = fsq.vectorize_isobands(wlevels)
    del fsq
    return out


def precision_and_scale(x):
    """Get precision and scale of a number.

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
    """Get limits of a value 'x' inside a list 'l'.

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
    """Pygonize : polygonize raster data into polygons vector."""

    def __init__(self):
        """Pygonize : polygonize raster data into polygons vector."""
        self.lx = None
        self.ly = None
        self.z = None

    def read_array(self, x, y, z):
        """Read data from numpy arrays.

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

        # Log
        log.info("read array of {0} x {1}".format(len(x), len(y)))
        log.debug("data value from {0:.2f} to {1:.2f}".format(z.min(), z.max()))

    def read_raster(self, fn, band=1):
        """Read raster data.

        :param fn: path of raster.
        :param band: band number.
        """
        dst = gdal.Open(fn)
        self.z = dst.GetRasterBand(band).ReadAsArray()
        xmin, dx, _, ymin, _, dy = dst.GetGeoTransform()  # geographic info
        dst = None  # close dataset
        del dst

        ny, nx = self.z.shape
        self.lx = numpy.arange(xmin + dx / 2, xmin + nx * dx, dx)
        self.ly = numpy.arange(ymin + dy / 2, ymin + ny * dy, dy)

        # Log
        log.info("read raster of {0} x {1}".format(nx, ny))
        log.debug("data value from {0:.2f} to {1:.2f}".format(
            self.z.min(), self.z.max()))

    def vectorize_isobands(self, levels):
        """Vectorization of isobands.

        :param levels: list of levels.
        :return: list of shapely.geometry.Polygon.
        """
        levels = sorted(levels)
        log.debug("create pool of worker to vectorize data")
        pool = multiprocessing.Pool()  # start a pool of worker
        outs = list()  # list of multiprocessing.pool.AsyncResult

        ny, nx = self.z.shape

        # Grid of X and Y
        x, y = numpy.meshgrid(self.lx, self.ly)

        # Split dataset into squares and vectorize
        log.info("starting isoband vectorization with levels {0}...".format(
            levels))
        for iy in range(ny - 1):
            for ix in range(nx - 1):
                part_z = self.z[iy:iy+2, ix:ix+2]
                part_x = x[iy:iy+2, ix:ix+2]
                part_y = y[iy:iy+2, ix:ix+2]

                p1 = Point(part_x[0, 0], part_y[0, 0], part_z[0, 0])
                p2 = Point(part_x[0, 1], part_y[0, 1], part_z[0, 1])
                p3 = Point(part_x[1, 1], part_y[1, 1], part_z[1, 1])
                p4 = Point(part_x[1, 0], part_y[1, 0], part_z[1, 0])

                # Create task
                w = pool.apply_async(vectorize_isoband_worker,
                                     args=(p1, p2, p3, p4, levels))
                outs.append(w)

        # Wait for all process to be terminated
        log.debug("create {n} tasks".format(n=len(outs)))
        pool.close()
        pool.join()

        # Join all resulting polygons
        polys = list()
        for w in outs:
            polys += w.get()

        log.info("isoband vectorization done.")
        log.debug(" -> {n} polygons".format(n=len(polys)))
        return polys

    def write_shapefile(self, levels, fn):
        """Vectorization of isobands and save result into shapefile.

        :param levels: list of levels.
        :param fn: path of shapefile.
        """
        log.info("writing isobands into shapefile...")
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

            # convert with specific scale
            zmin = format(zmin, '.{scale}f'.format(scale=scale))
            zmax = format(zmax, '.{scale}f'.format(scale=scale))
            del zs

            w.poly(parts=poly.__geo_interface__['coordinates'])
            w.record(ipoly, zmin, zmax)

        w.save(fn)
        log.info("writing isobands into shapefile done.")
