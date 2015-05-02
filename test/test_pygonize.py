#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Test. """

from __future__ import print_function, division
import tempfile
import unittest
import numpy
from pygonize import pygonize
from test_base_class import PygonizeTest


class TestPygonize(PygonizeTest):
    def setUp(self):
        self.npx = numpy.array([2, 6, 10])
        self.npy = numpy.array([11, 7, 3])
        self.npz = numpy.array([[50, 40, 20], [45, 42, 35], [46, 47, 45]])

    def test_precision_and_scale(self):
        self.assertEqual(pygonize.precision_and_scale(0), (1, 0))
        self.assertEqual(pygonize.precision_and_scale(1), (1, 0))
        self.assertEqual(pygonize.precision_and_scale(10), (2, 0))
        self.assertEqual(pygonize.precision_and_scale(250), (3, 0))
        self.assertEqual(pygonize.precision_and_scale(2629), (4, 0))
        self.assertEqual(pygonize.precision_and_scale(262915), (6, 0))
        self.assertEqual(pygonize.precision_and_scale(123456789), (9, 0))
        self.assertEqual(pygonize.precision_and_scale(26.29), (4, 2))
        self.assertEqual(pygonize.precision_and_scale(1.12345), (6, 5))
        self.assertEqual(pygonize.precision_and_scale(-10), (2, 0))
        self.assertEqual(pygonize.precision_and_scale(-10.005), (5, 3))

    def test_limits(self):
        self.assertEqual(pygonize.limits(5, [0, 2, 4, 6, 8, 10]), (4, 6))
        self.assertEqual(pygonize.limits(5.5, [0, 2, 4, 6, 8, 10]), (4, 6))
        self.assertEqual(pygonize.limits(0.01, [0, 2, 4, 6, 8, 10]), (0, 2))
        self.assertEqual(pygonize.limits(12, [0, 2, 4, 6, 8, 10]), None)
        self.assertEqual(pygonize.limits(-5, [0, 2, 4, 6, 8, 10]), None)
        self.assertEqual(pygonize.limits(5, [0, 4, 8, 6, 2, 10]), (4, 6))
        self.assertEqual(pygonize.limits(4, [0, 4, 8, 6, 2, 10]), (4, 4))
        self.assertEqual(pygonize.limits(10.0, [0, 2, 4, 6, 8, 10]), (10, 10))
        self.assertEqual(pygonize.limits(0.5, [0, 0.2, 0.4, 0.6, 0.8, 1]), (0.4, 0.6))
        self.assertEqual(pygonize.limits(0.6, [0, 0.2, 0.4, 0.6, 0.8, 1]), (0.6, 0.6))
        self.assertEqual(pygonize.limits(1.0, [0, 0.2, 0.4, 0.6, 0.8, 1]), (1.0, 1.0))

    def test_read_array(self):
        p = pygonize.Pygonize()
        p.read_array(x=self.npx, y=self.npy, z=self.npz)
        self.assertEqual(p.lx.tolist(), self.npx.tolist())
        self.assertEqual(p.ly.tolist(), self.npy.tolist())
        self.assertEqual(p.z.tolist(), self.npz.tolist())

    def test_read_raster(self):
        # Raster information...
        x0, y0 = 898879, 6317011
        dx, dy = 25, 25
        nx, ny = 5, 5
        dat = [[500, 450, 400, 300, 200],
               [460, 440, 410, 300, 250],
               [450, 430, 420, 380, 350],
               [455, 470, 440, 420, 400],
               [460, 465, 470, 460, 450]]

        p = pygonize.Pygonize()
        p.read_raster('../test/data/raster.tif')
        self.assertEqual(p.lx.tolist(), numpy.arange(x0 + dx / 2., x0 + dx * nx, dx).tolist())
        self.assertEqual(p.ly.tolist(), numpy.arange(y0 - dy / 2., y0 - dy * ny, -dy).tolist())
        self.assertEqual(p.z.tolist(), dat)

    def test_vectorize_isobands_from_array_1(self):
        p = pygonize.Pygonize()
        p.read_array(x=self.npx, y=self.npy, z=self.npz)
        polys = p.vectorize_isobands([40, 41, 42, 43, 44, 45])

        self.assertEqual(len(polys), 15)
        self.valid_poly(polys[0], [[5.6, 11, 41], [6, 11, 40], [6, 9, 41], [5.6, 11, 41]])
        self.valid_poly(polys[1], [[5.2, 11, 42], [5.6, 11, 41], [6, 9, 41], [6, 7, 42], [5.2, 11, 42]])
        self.valid_poly(polys[2], [[4.8, 11, 43], [5.2, 11, 42], [6, 7, 42], [4.67, 7, 43], [4.8, 11, 43]])
        self.valid_poly(polys[3], [[4.4, 11, 44], [4.8, 11, 43], [4.67, 7, 43], [3.33, 7, 44], [4.4, 11, 44]])
        self.valid_poly(polys[4], [[4, 11, 45], [4.4, 11, 44], [3.33, 7, 44], [2, 7, 45], [4, 11, 45]])
        self.valid_poly(polys[5], [[6, 11, 40], [7.14, 7, 40], [6.57, 7, 41], [6, 9, 41], [6, 11, 40]])
        self.valid_poly(polys[6], [[6.57, 7, 41], [6, 7, 42], [6, 9, 41], [6.57, 7, 41]])
        self.valid_poly(polys[7], [[4.67, 7, 43], [6, 7, 42], [6, 6.2, 43], [4.67, 7, 43]])
        self.valid_poly(polys[8], [[3.33, 7, 44], [4.67, 7, 43], [6, 6.2, 43], [6, 5.4, 44], [3.33, 7, 44]])
        self.valid_poly(polys[9], [[2, 7, 45], [3.33, 7, 44], [6, 5.4, 44], [6, 4.6, 45], [2, 7, 45]])
        self.valid_poly(polys[10], [[6.57, 7, 41], [7.14, 7, 40], [10, 5, 40], [10, 4.6, 41], [6.57, 7, 41]])
        self.valid_poly(polys[11], [[6, 7, 42], [6.57, 7, 41], [10, 4.6, 41], [10, 4.2, 42], [6, 7, 42]])
        self.valid_poly(polys[12], [[6, 7, 42], [10, 4.2, 42], [10, 3.8, 43], [6, 6.2, 43], [6, 7, 42]])
        self.valid_poly(polys[13], [[10, 3.8, 43], [10, 3.4, 44], [6, 5.4, 44], [6, 6.2, 43], [10, 3.8, 43]])
        self.valid_poly(polys[14], [[10, 3.4, 44], [10, 3, 45], [6, 4.6, 45], [6, 5.4, 44], [10, 3.4, 44]])

    def test_vectorize_isobands_from_array_2(self):
        p = pygonize.Pygonize()
        p.read_array(x=self.npx, y=self.npy, z=self.npz)
        polys = p.vectorize_isobands([0, 10, 20, 30, 40, 50, 60])

        self.assertEqual(len(polys), 7)
        self.valid_poly(polys[0], [[2, 11, 50], [6, 11, 40], [6, 7, 42], [2, 7, 45], [2, 11, 50]])
        self.valid_poly(polys[1], [[8, 11, 30], [10, 11, 20], [10, 8.33, 30], [8, 11, 30]])
        self.valid_poly(polys[2], [[6, 11, 40], [8, 11, 30], [10, 8.33, 30], [10, 7, 35], [7.14, 7, 40], [6, 11, 40]])
        self.valid_poly(polys[3], [[6, 11, 40], [7.14, 7, 40], [6, 7, 42], [6, 11, 40]])
        self.valid_poly(polys[4], [[2, 7, 45], [6, 7, 42], [6, 3, 47], [2, 3, 46], [2, 7, 45]])
        self.valid_poly(polys[5], [[7.14, 7, 40], [10, 7, 35], [10, 5, 40], [7.14, 7, 40]])
        self.valid_poly(polys[6], [[6, 7, 42], [7.14, 7, 40], [10, 5, 40], [10, 3, 45], [6, 3, 47], [6, 7, 42]])

    def test_vectorize_isobands_from_array_3(self):
        p = pygonize.Pygonize()
        p.read_array(x=self.npx, y=self.npy, z=self.npz)
        polys = p.vectorize_isobands(range(0, 60, 5))

        self.assertEqual(len(polys), 12)
        self.valid_poly(polys[0], [[4, 11, 45], [6, 11, 40], [6, 7, 42], [2, 7, 45], [4, 11, 45]])
        self.valid_poly(polys[1], [[2, 11, 50], [4, 11, 45], [2, 7, 45], [2, 11, 50]])
        self.valid_poly(polys[2], [[9, 11, 25], [10, 11, 20], [10, 9.67, 25], [9, 11, 25]])
        self.valid_poly(polys[3], [[8, 11, 30], [9, 11, 25], [10, 9.67, 25], [10, 8.33, 30], [8, 11, 30]])
        self.valid_poly(polys[4], [[7, 11, 35], [8, 11, 30], [10, 8.33, 30], [10, 7, 35], [7, 11, 35]])
        self.valid_poly(polys[5], [[6, 11, 40], [7, 11, 35], [10, 7, 35], [7.14, 7, 40], [6, 11, 40]])
        self.valid_poly(polys[6], [[6, 11, 40], [7.14, 7, 40], [6, 7, 42], [6, 11, 40]])
        self.valid_poly(polys[7], [[2, 7, 45], [6, 7, 42], [6, 4.6, 45], [2, 7, 45]])
        self.valid_poly(polys[8], [[2, 7, 45], [6, 4.6, 45], [6, 3, 47], [2, 3, 46], [2, 7, 45]])
        self.valid_poly(polys[9], [[7.14, 7, 40], [10, 7, 35], [10, 5, 40], [7.14, 7, 40]])
        self.valid_poly(polys[10], [[6, 7, 42], [7.14, 7, 40], [10, 5, 40], [10, 3, 45], [6, 4.6, 45], [6, 7, 42]])
        self.valid_poly(polys[11], [[10, 3, 45], [6, 3, 47], [6, 4.6, 45], [10, 3, 45]])

    def test_vectorize_isobands_from_raster_1(self):
        p = pygonize.Pygonize()
        p.read_raster('../test/data/raster.tif')
        polys = p.vectorize_isobands([200, 250, 300, 350, 400, 450, 500])
        self.assertEqual(len(polys), 32)
        self.valid_with_file(polys, '../test/data/isoband_from_raster_1.txt')

    def test_vectorize_isobands_from_raster_1_export_shapefile(self):
        t = tempfile.NamedTemporaryFile().name  # temporay filename

        p = pygonize.Pygonize()
        p.read_raster('../test/data/raster.tif')
        p.write_shapefile([200, 250, 300, 350, 400, 450, 500], t)

        for ext in ['.shp', '.shx', '.dbf']:
            with open('../test/data/isoband_from_raster_1' + ext, 'rb') as f1, open(t + ext, 'rb') as f2:
                self.assertEqual(f1.read(), f2.read())

if __name__ == '__main__':
    unittest.main()
