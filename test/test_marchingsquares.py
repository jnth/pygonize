#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Test. """

from __future__ import print_function, division
import unittest
from shapely.geometry import Point, Polygon
from pygonize import marchingsquares, interp
from test_base_class import PygonizeTest


class TestBaseFunctions(PygonizeTest):
    def setUp(self):
        """ Define some points and variables...
        """
        self.p1 = Point(2, 11, 50)
        self.p2 = Point(6, 11, 40)
        self.p3 = Point(15, 11, 30)

    def test_get_idx_isoline(self):
        self.assertEqual(marchingsquares.get_idx_isoline(5, 10), 0)
        self.assertEqual(marchingsquares.get_idx_isoline(10, 15), 0)
        self.assertEqual(marchingsquares.get_idx_isoline(20, 20), 1)
        self.assertEqual(marchingsquares.get_idx_isoline(25, 22), 1)

    def test_get_idx_isoband(self):
        self.assertEqual(marchingsquares.get_idx_isoband(2, 5, 10), 0)
        self.assertEqual(marchingsquares.get_idx_isoband(5, 5, 10), 1)
        self.assertEqual(marchingsquares.get_idx_isoband(6, 5, 10), 1)
        self.assertEqual(marchingsquares.get_idx_isoband(10, 5, 10), 1)
        self.assertEqual(marchingsquares.get_idx_isoband(12, 5, 10), 2)
        self.assertEqual(marchingsquares.get_idx_isoband(15, 10, 5), 2)

    def test_remove_duplicate_point(self):
        """ Test the 'remove_duplicate_point' function.
        """
        lp = [self.p1, self.p2, self.p3]
        new = marchingsquares.remove_duplicate_point(lp)
        self.assertEqual(len(new), 3)
        self.valid_point(new[0], self.p1)
        self.valid_point(new[1], self.p2)
        self.valid_point(new[2], self.p3)

        lp = [self.p3, self.p1, self.p2, self.p1, self.p3]
        new = marchingsquares.remove_duplicate_point(lp)
        self.assertEqual(len(new), 3)
        self.valid_point(new[0], self.p3)
        self.valid_point(new[1], self.p1)
        self.valid_point(new[2], self.p2)

    def test_interpolate(self):
        """ Test the 'interpolate' function.
        """
        self.valid_point(interp.interpolate(self.p1, self.p2, 40), (6, 11, 40))
        self.valid_point(interp.interpolate(self.p1, self.p2, 45), (4, 11, 45))
        self.valid_point(interp.interpolate(self.p1, self.p2, 46), (3.6, 11, 46))
        self.valid_point(interp.interpolate(self.p1, self.p2, 50), (2, 11, 50))
        self.valid_point(interp.interpolate(self.p2, self.p1, 46), (3.6, 11, 46))
        self.assertIsNone(interp.interpolate(self.p1, self.p2, 35))
        self.assertIsNone(interp.interpolate(self.p1, self.p2, 55))

    def test_isoband_on_edge(self):
        p1 = Point(10, 10, 5)
        p2 = Point(20, 10, 25)

        self.assertEqual(marchingsquares.isoband_on_edge(p1, p2, 1, 2), [])

        self.assertEqual(marchingsquares.isoband_on_edge(p1, p2, 30, 35), [])

        p = marchingsquares.isoband_on_edge(p1, p2, 1, 5)
        self.assertEqual(len(p), 2)
        self.valid_point(p[0], (10, 10, 5))
        self.valid_point(p[1], (10, 10, 5))

        p = marchingsquares.isoband_on_edge(p1, p2, 1, 6)
        self.assertEqual(len(p), 2)
        self.valid_point(p[0], (10, 10, 5))
        self.valid_point(p[1], (10.5, 10, 6))

        p = marchingsquares.isoband_on_edge(p1, p2, 1, 20)
        self.assertEqual(len(p), 2)
        self.valid_point(p[0], (10, 10, 5))
        self.valid_point(p[1], (17.5, 10, 20))

        p = marchingsquares.isoband_on_edge(p1, p2, 1, 30)
        self.assertEqual(len(p), 2)
        self.valid_point(p[0], (10, 10, 5))
        self.valid_point(p[1], (20, 10, 25))

        p = marchingsquares.isoband_on_edge(p1, p2, 10, 30)
        self.assertEqual(len(p), 2)
        self.valid_point(p[0], (12.5, 10, 10))
        self.valid_point(p[1], (20, 10, 25))

        p = marchingsquares.isoband_on_edge(p1, p2, 10, 20)
        self.assertEqual(len(p), 2)
        self.valid_point(p[0], (12.5, 10, 10))
        self.valid_point(p[1], (17.5, 10, 20))

    def test_is_clockwise(self):
        """ Test the 'is_clockwise' function.
        """
        p = Polygon([(5, 0), (6, 4), (4, 5), (1, 5), (1, 0)])
        self.assertFalse(marchingsquares.is_clockwise(p))

        p = Polygon([(6, 11), (6, 9), (5.6, 11), (6, 11)])
        self.assertTrue(marchingsquares.is_clockwise(p))


class TestMarchingSquares(PygonizeTest):
    def setUp(self):
        self.p1 = Point(10, 12, 15)
        self.p2 = Point(12, 14, 20)
        self.p3 = Point(15, 14, 18)
        self.p4 = Point(11, 15, 29)

    def test_init_shapely(self):
        p = Point(25, 11, 14)
        self.valid_point(p, (25, 11, 14))

    def test_init(self):
        sq = marchingsquares.Square(self.p1, self.p2, self.p3, self.p4)
        self.valid_point(sq.p1, (10, 12, 15))
        self.valid_point(sq.p2, (12, 14, 20))
        self.valid_point(sq.p3, (15, 14, 18))
        self.valid_point(sq.p4, (11, 15, 29))
        self.valid_list(sq.x, [10, 12, 15, 11])
        self.valid_list(sq.y, [12, 14, 14, 15])
        self.valid_list(sq.z, [15, 20, 18, 29])
        self.assertEqual(sq.centralmean, 20.5)

    def test_egdes(self):
        sq = marchingsquares.Square(self.p1, self.p2, self.p3, self.p4)
        egdes = sq.edges
        self.valid_point(egdes[0][0], self.p1)
        self.valid_point(egdes[0][1], self.p2)
        self.valid_point(egdes[1][0], self.p2)
        self.valid_point(egdes[1][1], self.p3)
        self.valid_point(egdes[2][0], self.p3)
        self.valid_point(egdes[2][1], self.p4)
        self.valid_point(egdes[3][0], self.p4)
        self.valid_point(egdes[3][1], self.p1)

    def test_points(self):
        sq = marchingsquares.Square(self.p1, self.p2, self.p3, self.p4)
        lp = sq.points
        self.valid_point(lp[0], self.p1)
        self.valid_point(lp[1], self.p2)
        self.valid_point(lp[2], self.p3)
        self.valid_point(lp[3], self.p4)

    def test_isoband_classif(self):
        sq = marchingsquares.Square(self.p1, self.p2, self.p3, self.p4)
        self.assertEqual(sq.isoband_classif(10, 12), "2222")
        self.assertEqual(sq.isoband_classif(55, 60), "0000")
        self.assertEqual(sq.isoband_classif(10, 15), "1222")
        self.assertEqual(sq.isoband_classif(10, 20), "1112")
        self.assertEqual(sq.isoband_classif(16, 20), "0112")
        self.assertEqual(sq.isoband_classif(20, 25), "0102")
        self.assertEqual(sq.isoband_classif(25, 30), "0001")

    def test_make_polygon(self):
        self.assertIsNone(marchingsquares.make_polygon())
        self.assertIsNone(marchingsquares.make_polygon(self.p1))
        self.assertIsNone(marchingsquares.make_polygon(self.p1, self.p2))

        poly = marchingsquares.make_polygon(self.p1, self.p2, self.p3)
        self.valid_poly(poly, [[10, 12, 15], [12, 14, 20], [15, 14, 18], [10, 12, 15]])

        poly = marchingsquares.make_polygon(self.p4, self.p3, self.p2)
        self.valid_poly(poly, [[11, 15, 29], [15, 14, 18], [12, 14, 20], [11, 15, 29]])

        poly = marchingsquares.make_polygon(self.p1, self.p4, self.p3, self.p2)
        self.valid_poly(poly, [[10, 12, 15], [11, 15, 29], [15, 14, 18], [12, 14, 20], [10, 12, 15]])


class TestVectorizeIsoband(PygonizeTest):
    def init_point(self, z1, z2, z3, z4, lmn, lmx):
        """ Define the 4 points, isoband level for the test and create a Square.

        :param z1:
        :param z2:
        :param z3:
        :param z4:
        :param lmn:
        :param lmx:
        :return:
        """
        self.p1 = Point(10, 20, z1)
        self.p2 = Point(20, 20, z2)
        self.p3 = Point(20, 10, z3)
        self.p4 = Point(10, 10, z4)
        self.lmn = lmn
        self.lmx = lmx

        # Create square
        self.sq = marchingsquares.Square(self.p1, self.p2, self.p3, self.p4)

        # Return isoband classification and polygons
        cl = self.sq.isoband_classif(self.lmn, self.lmx)
        poly = self.sq.vectorize_isoband(self.lmn, self.lmx)
        return cl, poly

    def test_vectorize_2222(self):
        cl, poly = self.init_point(30, 31, 32, 33, 10, 20)
        self.assertEqual(cl, '2222')
        self.assertIsNone(poly)

    def test_vectorize_0000(self):
        cl, poly = self.init_point(30, 31, 32, 33, 40, 50)
        self.assertEqual(cl, '0000')
        self.assertIsNone(poly)

    def test_vectorize_2221(self):
        cl, poly = self.init_point(30, 31, 32, 15, 10, 20)
        self.assertEqual(cl, '2221')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[12.94, 10, 20], [10, 10, 15], [10, 13.33, 20], [12.94, 10, 20]])

    def test_vectorize_2212(self):
        cl, poly = self.init_point(30, 31, 15, 32, 10, 20)
        self.assertEqual(cl, '2212')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 13.13, 20], [20, 10, 15], [17.06, 10, 20], [20, 13.13, 20]])

    def test_vectorize_2122(self):
        cl, poly = self.init_point(30, 15, 31, 32, 10, 20)
        self.assertEqual(cl, '2122')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[16.67, 20, 20], [20, 20, 15], [20, 16.88, 20], [16.67, 20, 20]])

    def test_vectorize_1222(self):
        cl, poly = self.init_point(15, 30, 31, 32, 10, 20)
        self.assertEqual(cl, '1222')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10, 20, 15], [13.33, 20, 20], [10, 17.06, 20], [10, 20, 15]])

    def test_vectorize_0001(self):
        cl, poly = self.init_point(5, 6, 7, 15, 10, 20)
        self.assertEqual(cl, '0001')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[16.25, 10, 10], [10, 10, 15], [10, 15, 10], [16.25, 10, 10]])

    def test_vectorize_0010(self):
        cl, poly = self.init_point(5, 6, 15, 6, 10, 20)
        self.assertEqual(cl, '0010')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 15.56, 10], [20, 10, 15], [14.44, 10, 10], [20, 15.56, 10]])

    def test_vectorize_0100(self):
        cl, poly = self.init_point(5, 15, 6, 6, 10, 20)
        self.assertEqual(cl, '0100')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[15, 20, 10], [20, 20, 15], [20, 14.44, 10], [15, 20, 10]])

    def test_vectorize_1000(self):
        cl, poly = self.init_point(15, 8, 6, 6, 10, 20)
        self.assertEqual(cl, '1000')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10, 20, 15], [17.14, 20, 10], [10, 14.44, 10], [10, 20, 15]])

    def test_vectorize_2220(self):
        cl, poly = self.init_point(22, 24, 26, 6, 10, 20)
        self.assertEqual(cl, '2220')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[17, 10, 20], [12, 10, 10], [10, 12.5, 10], [10, 18.75, 20], [17, 10, 20]])

    def test_vectorize_2202(self):
        cl, poly = self.init_point(22, 24, 6, 26, 10, 20)
        self.assertEqual(cl, '2202')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 17.78, 20], [20, 12.22, 10], [18, 10, 10], [13, 10, 20], [20, 17.78, 20]])

    def test_vectorize_2022(self):
        cl, poly = self.init_point(22, 6, 24, 26, 10, 20)
        self.assertEqual(cl, '2022')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[11.25, 20, 20], [17.5, 20, 10], [20, 17.78, 10], [20, 12.22, 20], [11.25, 20, 20]])

    def test_vectorize_0222(self):
        cl, poly = self.init_point(6, 22, 24, 26, 10, 20)
        self.assertEqual(cl, '0222')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[12.5, 20, 10], [18.75, 20, 20], [10, 13, 20], [10, 18, 10], [12.5, 20, 10]])

    def test_vectorize_0002(self):
        cl, poly = self.init_point(6, 8, 4, 26, 10, 20)
        self.assertEqual(cl, '0002')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[17.27, 10, 10], [12.73, 10, 20], [10, 13, 20], [10, 18, 10], [17.27, 10, 10]])

    def test_vectorize_0020(self):
        cl, poly = self.init_point(6, 8, 26, 4, 10, 20)
        self.assertEqual(cl, '0020')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 18.89, 10], [20, 13.33, 20], [17.27, 10, 20], [12.73, 10, 10], [20, 18.89, 10]])

    def test_vectorize_0200(self):
        cl, poly = self.init_point(6, 26, 8, 4, 10, 20)
        self.assertEqual(cl, '0200')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[12, 20, 10], [17, 20, 20], [20, 16.67, 20], [20, 11.11, 10], [12, 20, 10]])

    def test_vectorize_2000(self):
        cl, poly = self.init_point(26, 6, 8, 4, 10, 20)
        self.assertEqual(cl, '2000')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[13, 20, 20], [18, 20, 10], [10, 12.73, 10], [10, 17.27, 20], [13, 20, 20]])

    def test_vectorize_1111(self):
        cl, poly = self.init_point(12, 16, 18, 14, 10, 20)
        self.assertEqual(cl, '1111')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10, 20, 12], [20, 20, 16], [20, 10, 18], [10, 10, 14], [10, 20, 12]])

    def test_vectorize_0011(self):
        cl, poly = self.init_point(2, 6, 18, 14, 10, 20)
        self.assertEqual(cl, '0011')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 16.67, 10], [20, 10, 18], [10, 10, 14], [10, 13.33, 10], [20, 16.67, 10]])

    def test_vectorize_0110(self):
        cl, poly = self.init_point(2, 16, 18, 4, 10, 20)
        self.assertEqual(cl, '0110')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[15.71, 20, 10], [20, 20, 16], [20, 10, 18], [14.29, 10, 10], [15.71, 20, 10]])

    def test_vectorize_1100(self):
        cl, poly = self.init_point(12, 16, 8, 4, 10, 20)
        self.assertEqual(cl, '1100')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10, 20, 12], [20, 20, 16], [20, 12.5, 10], [10, 17.5, 10], [10, 20, 12]])

    def test_vectorize_1001(self):
        cl, poly = self.init_point(12, 6, 8, 14, 10, 20)
        self.assertEqual(cl, '1001')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10, 20, 12], [13.33, 20, 10], [16.67, 10, 10], [10, 10, 14], [10, 20, 12]])

    def test_vectorize_2211(self):
        cl, poly = self.init_point(22, 26, 18, 14, 10, 20)
        self.assertEqual(cl, '2211')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 12.5, 20], [20, 10, 18], [10, 10, 14], [10, 17.5, 20], [20, 12.5, 20]])

    def test_vectorize_2112(self):
        cl, poly = self.init_point(22, 16, 18, 24, 10, 20)
        self.assertEqual(cl, '2112')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[13.33, 20, 20], [20, 20, 16], [20, 10, 18], [16.67, 10, 20], [13.33, 20, 20]])

    def test_vectorize_1122(self):
        cl, poly = self.init_point(12, 16, 28, 24, 10, 20)
        self.assertEqual(cl, '1122')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10, 20, 12], [20, 20, 16], [20, 16.67, 20], [10, 13.33, 20], [10, 20, 12]])

    def test_vectorize_1221(self):
        cl, poly = self.init_point(12, 26, 28, 14, 10, 20)
        self.assertEqual(cl, '1221')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10, 20, 12], [15.71, 20, 20], [14.29, 10, 20], [10, 10, 14], [10, 20, 12]])

    def test_vectorize_2200(self):
        cl, poly = self.init_point(22, 26, 8, 4, 10, 20)
        self.assertEqual(cl, '2200')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 16.67, 20], [20, 11.11, 10], [10, 13.33, 10], [10, 18.89, 20], [20, 16.67, 20]])

    def test_vectorize_2002(self):
        cl, poly = self.init_point(22, 6, 8, 24, 10, 20)
        self.assertEqual(cl, '2002')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[11.25, 20, 20], [17.5, 20, 10], [18.75, 10, 10], [12.5, 10, 20], [11.25, 20, 20]])

    def test_vectorize_0022(self):
        cl, poly = self.init_point(2, 6, 28, 24, 10, 20)
        self.assertEqual(cl, '0022')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 18.18, 10], [20, 13.64, 20], [10, 11.82, 20], [10, 16.36, 10], [20, 18.18, 10]])

    def test_vectorize_0220(self):
        cl, poly = self.init_point(2, 26, 28, 4, 10, 20)
        self.assertEqual(cl, '0220')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[13.33, 20, 10], [17.5, 20, 20], [16.67, 10, 20], [12.5, 10, 10], [13.33, 20, 10]])

    def test_vectorize_0211(self):
        cl, poly = self.init_point(2, 26, 18, 14, 10, 20)
        self.assertEqual(cl, '0211')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[13.33, 20, 10], [17.5, 20, 20], [20, 12.5, 20], [20, 10, 18], [10, 10, 14], [10, 13.33, 10],
                         [13.33, 20, 10]])

    def test_vectorize_2110(self):
        cl, poly = self.init_point(22, 16, 18, 4, 10, 20)
        self.assertEqual(cl, '2110')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[13.33, 20, 20], [20, 20, 16], [20, 10, 18], [14.29, 10, 10], [10, 13.33, 10], [10, 18.89, 20],
                         [13.33, 20, 20]])

    def test_vectorize_1102(self):
        cl, poly = self.init_point(12, 16, 8, 24, 10, 20)
        self.assertEqual(cl, '1102')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [20, 20, 16], [20, 12.5, 10], [18.75, 10, 10], [12.5, 10, 20], [10, 13.33, 20],
                         [10, 20, 12]])

    def test_vectorize_1021(self):
        cl, poly = self.init_point(12, 6, 28, 14, 10, 20)
        self.assertEqual(cl, '1021')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [13.33, 20, 10], [20, 18.18, 10], [20, 13.64, 20], [14.29, 10, 20], [10, 10, 14],
                         [10, 20, 12]])

    def test_vectorize_2011(self):
        cl, poly = self.init_point(22, 6, 18, 14, 10, 20)
        self.assertEqual(cl, '2011')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[11.25, 20, 20], [17.5, 20, 10], [20, 16.67, 10], [20, 10, 18], [10, 10, 14], [10, 17.5, 20],
                         [11.25, 20, 20]])

    def test_vectorize_0112(self):
        cl, poly = self.init_point(2, 16, 18, 24, 10, 20)
        self.assertEqual(cl, '0112')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[15.71, 20, 10], [20, 20, 16], [20, 10, 18], [16.67, 10, 20], [10, 11.82, 20], [10, 16.36, 10],
                         [15.71, 20, 10]])

    def test_vectorize_1120(self):
        cl, poly = self.init_point(12, 16, 28, 4, 10, 20)
        self.assertEqual(cl, '1120')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [20, 20, 16], [20, 16.67, 20], [16.67, 10, 20], [12.5, 10, 10], [10, 17.5, 10],
                         [10, 20, 12]])

    def test_vectorize_1201(self):
        cl, poly = self.init_point(12, 26, 8, 14, 10, 20)
        self.assertEqual(cl, '1201')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [15.71, 20, 20], [20, 16.67, 20], [20, 11.11, 10], [16.67, 10, 10], [10, 10, 14],
                         [10, 20, 12]])

    def test_vectorize_2101(self):
        cl, poly = self.init_point(22, 16, 8, 14, 10, 20)
        self.assertEqual(cl, '2101')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[13.33, 20, 20], [20, 20, 16], [20, 12.5, 10], [16.67, 10, 10], [10, 10, 14], [10, 17.5, 20],
                         [13.33, 20, 20]])

    def test_vectorize_0121(self):
        cl, poly = self.init_point(2, 16, 28, 14, 10, 20)
        self.assertEqual(cl, '0121')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[15.71, 20, 10], [20, 20, 16], [20, 16.67, 20], [14.29, 10, 20], [10, 10, 14], [10, 13.33, 10],
                         [15.71, 20, 10]])

    def test_vectorize_1012(self):
        cl, poly = self.init_point(12, 6, 18, 24, 10, 20)
        self.assertEqual(cl, '1012')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [13.33, 20, 10], [20, 16.67, 10], [20, 10, 18], [16.67, 10, 20], [10, 13.33, 20],
                         [10, 20, 12]])

    def test_vectorize_1210(self):
        cl, poly = self.init_point(12, 26, 18, 4, 10, 20)
        self.assertEqual(cl, '1210')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [15.71, 20, 20], [20, 12.5, 20], [20, 10, 18], [14.29, 10, 10], [10, 17.5, 10],
                         [10, 20, 12]])

    def test_vectorize_1211(self):
        cl, poly = self.init_point(12, 26, 18, 14, 10, 20)
        self.assertEqual(cl, '1211')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [15.71, 20, 20], [20, 12.5, 20], [20, 10, 18], [10, 10, 14], [10, 20, 12]])

    def test_vectorize_2111(self):
        cl, poly = self.init_point(22, 16, 18, 14, 10, 20)
        self.assertEqual(cl, '2111')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[13.33, 20, 20], [20, 20, 16], [20, 10, 18], [10, 10, 14], [10, 17.5, 20], [13.33, 20, 20]])

    def test_vectorize_1112(self):
        cl, poly = self.init_point(12, 16, 18, 24, 10, 20)
        self.assertEqual(cl, '1112')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [20, 20, 16], [20, 10, 18], [16.67, 10, 20], [10, 13.33, 20], [10, 20, 12]])

    def test_vectorize_1121(self):
        cl, poly = self.init_point(12, 16, 28, 14, 10, 20)
        self.assertEqual(cl, '1121')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [20, 20, 16], [20, 16.67, 20], [14.29, 10, 20], [10, 10, 14], [10, 20, 12]])

    def test_vectorize_1011(self):
        cl, poly = self.init_point(12, 6, 18, 14, 10, 20)
        self.assertEqual(cl, '1011')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [13.33, 20, 10], [20, 16.67, 10], [20, 10, 18], [10, 10, 14], [10, 20, 12]])

    def test_vectorize_0111(self):
        cl, poly = self.init_point(2, 16, 18, 14, 10, 20)
        self.assertEqual(cl, '0111')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[15.71, 20, 10], [20, 20, 16], [20, 10, 18], [10, 10, 14], [10, 13.33, 10], [15.71, 20, 10]])

    def test_vectorize_1110(self):
        cl, poly = self.init_point(12, 16, 18, 4, 10, 20)
        self.assertEqual(cl, '1110')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [20, 20, 16], [20, 10, 18], [14.29, 10, 10], [10, 17.5, 10], [10, 20, 12]])

    def test_vectorize_1101(self):
        cl, poly = self.init_point(12, 16, 8, 14, 10, 20)
        self.assertEqual(cl, '1101')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [20, 20, 16], [20, 12.5, 10], [16.67, 10, 10], [10, 10, 14], [10, 20, 12]])

    def test_vectorize_1200(self):
        cl, poly = self.init_point(12, 26, 8, 4, 10, 20)
        self.assertEqual(cl, '1200')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [15.71, 20, 20], [20, 16.67, 20], [20, 11.11, 10], [10, 17.5, 10], [10, 20, 12]])

    def test_vectorize_0120(self):
        cl, poly = self.init_point(2, 16, 28, 4, 10, 20)
        self.assertEqual(cl, '0120')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[15.71, 20, 10], [20, 20, 16], [20, 16.67, 20], [16.67, 10, 20], [12.5, 10, 10],
                                  [15.71, 20, 10]])

    def test_vectorize_0012(self):
        cl, poly = self.init_point(2, 6, 18, 24, 10, 20)
        self.assertEqual(cl, '0012')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 16.67, 10], [20, 10, 18], [16.67, 10, 20], [10, 11.82, 20], [10, 16.36, 10],
                                  [20, 16.67, 10]])

    def test_vectorize_2001(self):
        cl, poly = self.init_point(22, 6, 8, 14, 10, 20)
        self.assertEqual(cl, '2001')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[11.25, 20, 20], [17.5, 20, 10], [16.67, 10, 10], [10, 10, 14], [10, 17.5, 20],
                                  [11.25, 20, 20]])

    def test_vectorize_1022(self):
        cl, poly = self.init_point(12, 6, 28, 24, 10, 20)
        self.assertEqual(cl, '1022')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10, 20, 12], [13.33, 20, 10], [20, 18.18, 10], [20, 13.64, 20], [10, 13.33, 20],
                                  [10, 20, 12]])

    def test_vectorize_2102(self):
        cl, poly = self.init_point(22, 16, 8, 24, 10, 20)
        self.assertEqual(cl, '2102')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[13.33, 20, 20], [20, 20, 16], [20, 12.5, 10], [18.75, 10, 10], [12.5, 10, 20],
                                  [13.33, 20, 20]])

    def test_vectorize_2210(self):
        cl, poly = self.init_point(22, 26, 18, 4, 10, 20)
        self.assertEqual(cl, '2210')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 12.5, 20], [20, 10, 18], [14.29, 10, 10], [10, 13.33, 10], [10, 18.89, 20],
                                  [20, 12.5, 20]])

    def test_vectorize_0221(self):
        cl, poly = self.init_point(2, 26, 28, 14, 10, 20)
        self.assertEqual(cl, '0221')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[13.33, 20, 10], [17.5, 20, 20], [14.29, 10, 20], [10, 10, 14], [10, 13.33, 10],
                                  [13.33, 20, 10]])

    def test_vectorize_1002(self):
        cl, poly = self.init_point(12, 6, 8, 24, 10, 20)
        self.assertEqual(cl, '1002')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [13.33, 20, 10], [18.75, 10, 10], [12.5, 10, 20], [10, 13.33, 20], [10, 20, 12]])

    def test_vectorize_2100(self):
        cl, poly = self.init_point(22, 16, 8, 4, 10, 20)
        self.assertEqual(cl, '2100')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[13.33, 20, 20], [20, 20, 16], [20, 12.5, 10], [10, 13.33, 10], [10, 18.89, 20],
                                  [13.33, 20, 20]])

    def test_vectorize_0210(self):
        cl, poly = self.init_point(2, 26, 18, 4, 10, 20)
        self.assertEqual(cl, '0210')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[13.33, 20, 10], [17.5, 20, 20], [20, 12.5, 20], [20, 10, 18], [14.29, 10, 10],
                                  [13.33, 20, 10]])

    def test_vectorize_0021(self):
        cl, poly = self.init_point(2, 6, 28, 14, 10, 20)
        self.assertEqual(cl, '0021')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 18.18, 10], [20, 13.64, 20], [14.29, 10, 20], [10, 10, 14], [10, 13.33, 10],
                                  [20, 18.18, 10]])

    def test_vectorize_1220(self):
        cl, poly = self.init_point(12, 26, 28, 4, 10, 20)
        self.assertEqual(cl, '1220')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [15.71, 20, 20], [16.67, 10, 20], [12.5, 10, 10], [10, 17.5, 10], [10, 20, 12]])

    def test_vectorize_0122(self):
        cl, poly = self.init_point(2, 16, 28, 24, 10, 20)
        self.assertEqual(cl, '0122')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[15.71, 20, 10], [20, 20, 16], [20, 16.67, 20], [10, 11.82, 20], [10, 16.36, 10],
                                  [15.71, 20, 10]])

    def test_vectorize_2012(self):
        cl, poly = self.init_point(22, 6, 18, 24, 10, 20)
        self.assertEqual(cl, '2012')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[11.25, 20, 20], [17.5, 20, 10], [20, 16.67, 10], [20, 10, 18], [16.67, 10, 20],
                                  [11.25, 20, 20]])

    def test_vectorize_2201(self):
        cl, poly = self.init_point(22, 26, 8, 14, 10, 20)
        self.assertEqual(cl, '2201')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[20, 16.67, 20], [20, 11.11, 10], [16.67, 10, 10], [10, 10, 14], [10, 17.5, 20],
                                  [20, 16.67, 20]])

    def test_vectorize_0101a(self):
        cl, poly = self.init_point(2, 12, 8, 14, 10, 20)
        self.assertEqual(cl, '0101')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[18, 20, 10], [20, 20, 12], [20, 15, 10], [18, 20, 10]])
        self.valid_poly(poly[1], [[16.67, 10, 10], [10, 10, 14], [10, 13.33, 10], [16.67, 10, 10]])

    def test_vectorize_0101b(self):
        cl, poly = self.init_point(2, 18, 8, 14, 10, 20)
        self.assertEqual(cl, '0101')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[15, 20, 10], [20, 20, 18], [20, 12, 10], [16.67, 10, 10], [10, 10, 14], [10, 13.33, 10],
                         [15, 20, 10]])

    def test_vectorize_1010a(self):
        cl, poly = self.init_point(12, 2, 18, 4, 10, 20)
        self.assertEqual(cl, '1010')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[10, 20, 12], [12, 20, 10], [10, 17.5, 10], [10, 20, 12]])
        self.valid_poly(poly[1], [[20, 15, 10], [20, 10, 18], [14.29, 10, 10], [20, 15, 10]])

    def test_vectorize_1010b(self):
        cl, poly = self.init_point(12, 8, 18, 4, 10, 20)
        self.assertEqual(cl, '1010')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 12], [15, 20, 10], [20, 18, 10], [20, 10, 18], [14.29, 10, 10], [10, 17.5, 10],
                         [10, 20, 12]])

    def test_vectorize_2121b(self):
        cl, poly = self.init_point(22, 18, 24, 14, 10, 20)
        self.assertEqual(cl, '2121')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[15, 20, 20], [20, 20, 18], [20, 16.67, 20], [16, 10, 20], [10, 10, 14], [10, 17.5, 20],
                         [15, 20, 20]])

    def test_vectorize_2121c(self):
        cl, poly = self.init_point(26, 18, 28, 14, 10, 20)
        self.assertEqual(cl, '2121')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[17.5, 20, 20], [20, 20, 18], [20, 18, 20], [17.5, 20, 20]])
        self.valid_poly(poly[1], [[14.29, 10, 20], [10, 10, 14], [10, 15, 20], [14.29, 10, 20]])

    def test_vectorize_1212b(self):
        cl, poly = self.init_point(18, 22, 12, 24, 10, 20)
        self.assertEqual(cl, '1212')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 18], [15, 20, 20], [20, 18, 20], [20, 10, 12], [13.33, 10, 20], [10, 16.67, 20],
                         [10, 20, 18]])

    def test_vectorize_1212b_center_equal_mx(self):
        cl, poly = self.init_point(18, 22, 14, 26, 10, 20)
        self.assertEqual(cl, '1212')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[10, 20, 18], [15, 20, 20], [20, 17.5, 20], [20, 10, 14], [15, 10, 20], [10, 17.5, 20],
                         [10, 20, 18]])

    def test_vectorize_1212c(self):
        cl, poly = self.init_point(18, 28, 14, 26, 10, 20)
        self.assertEqual(cl, '1212')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[10, 20, 18], [12, 20, 20], [10, 17.5, 20], [10, 20, 18]])
        self.valid_poly(poly[1], [[20, 14.29, 20], [20, 10, 14], [15, 10, 20], [20, 14.29, 20]])

    def test_vectorize_2120b(self):
        cl, poly = self.init_point(28, 18, 24, 6, 10, 20)
        self.assertEqual(cl, '2120')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[18, 20, 20], [20, 20, 18], [20, 16.67, 20], [17.78, 10, 20], [12.22, 10, 10], [10, 11.82, 10],
                         [10, 16.36, 20], [18, 20, 20]])

    def test_vectorize_2120c(self):
        cl, poly = self.init_point(28, 18, 29, 6, 10, 20)
        self.assertEqual(cl, '2120')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[18, 20, 20], [20, 20, 18], [20, 18.18, 20], [18, 20, 20]])
        self.valid_poly(poly[1], [[16.09, 10, 20], [11.74, 10, 10], [10, 11.82, 10], [10, 16.36, 20], [16.09, 10, 20]])

    def test_vectorize_2021b(self):
        cl, poly = self.init_point(28, 6, 24, 18, 10, 20)
        self.assertEqual(cl, '2021')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[13.64, 20, 20], [18.18, 20, 10], [20, 17.78, 10], [20, 12.22, 20], [13.33, 10, 20],
                                  [10, 10, 18], [10, 12, 20], [13.64, 20, 20]])

    def test_vectorize_2021c(self):
        cl, poly = self.init_point(28, 6, 29, 18, 10, 20)
        self.assertEqual(cl, '2021')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[13.64, 20, 20], [18.18, 20, 10], [20, 18.26, 10], [20, 13.91, 20], [13.64, 20, 20]])
        self.valid_poly(poly[1], [[11.82, 10, 20], [10, 10, 18], [10, 12, 20], [11.82, 10, 20]])

    def test_vectorize_1202b(self):
        cl, poly = self.init_point(18, 24, 6, 28, 10, 20)
        self.assertEqual(cl, '1202')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10, 20, 18], [13.33, 20, 20], [20, 17.78, 20], [20, 12.22, 10], [18.18, 10, 10],
                                  [13.64, 10, 20], [10, 18, 20], [10, 20, 18]])

    def test_vectorize_1202c(self):
        cl, poly = self.init_point(18, 29, 6, 28, 10, 20)
        self.assertEqual(cl, '1202')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[10, 20, 18], [11.82, 20, 20], [10, 18, 20], [10, 20, 18]])
        self.valid_poly(poly[1], [[20, 16.09, 20], [20, 11.74, 10], [18.18, 10, 10], [13.64, 10, 20], [20, 16.09, 20]])

    def test_vectorize_0212b(self):
        cl, poly = self.init_point(6, 24, 18, 28, 10, 20)
        self.assertEqual(cl, '0212')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0],
                        [[12.22, 20, 10], [17.78, 20, 20], [20, 13.33, 20], [20, 10, 18], [18, 10, 20], [10, 13.64, 20],
                         [10, 18.18, 10], [12.22, 20, 10]])

    def test_vectorize_0212c(self):
        cl, poly = self.init_point(6, 29, 18, 28, 10, 20)
        self.assertEqual(cl, '0212')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[11.74, 20, 10], [16.09, 20, 20], [10, 13.64, 20], [10, 18.18, 10], [11.74, 20, 10]])
        self.valid_poly(poly[1], [[20, 11.82, 20], [20, 10, 18], [18, 10, 20], [20, 11.82, 20]])

    def test_vectorize_0102a(self):
        cl, poly = self.init_point(2, 11, 4, 21, 10, 20)
        self.assertEqual(cl, '0102')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[18.89, 20, 10], [20, 20, 11], [20, 18.57, 10], [18.89, 20, 10]])
        self.valid_poly(poly[1], [[16.47, 10, 10], [10.59, 10, 20], [10, 10.53, 20], [10, 15.79, 10], [16.47, 10, 10]])

    def test_vectorize_0102b(self):
        cl, poly = self.init_point(8, 11, 4, 21, 10, 20)
        self.assertEqual(cl, '0102')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[16.67, 20, 10], [20, 20, 11], [20, 18.57, 10], [16.47, 10, 10], [10.59, 10, 20],
                                  [10, 10.77, 20], [10, 18.46, 10], [16.67, 20, 10]])

    def test_vectorize_0201a(self):
        cl, poly = self.init_point(2, 21, 4, 11, 10, 20)
        self.assertEqual(cl, '0201')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[14.21, 20, 10], [19.47, 20, 20], [20, 19.41, 20], [20, 13.53, 10], [14.21, 20, 10]])
        self.valid_poly(poly[1], [[11.43, 10, 10], [10, 10, 11], [10, 11.11, 10], [11.43, 10, 10]])

    def test_vectorize_0201b(self):
        cl, poly = self.init_point(8, 21, 4, 11, 10, 20)
        self.assertEqual(cl, '0201')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[11.54, 20, 10], [19.23, 20, 20], [20, 19.41, 20], [20, 13.53, 10], [11.43, 10, 10],
                                  [10, 10, 11], [10, 13.33, 10], [11.54, 20, 10]])

    def test_vectorize_1020a(self):
        cl, poly = self.init_point(11, 2, 21, 4, 10, 20)
        self.assertEqual(cl, '1020')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[10, 20, 11], [11.11, 20, 10], [10, 18.57, 10], [10, 20, 11]])
        self.valid_poly(poly[1], [[20, 15.79, 10], [20, 10.53, 20], [19.41, 10, 20], [13.53, 10, 10], [20, 15.79, 10]])

    def test_vectorize_1020b(self):
        cl, poly = self.init_point(11, 8, 21, 4, 10, 20)
        self.assertEqual(cl, '1020')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10, 20, 11], [13.33, 20, 10], [20, 18.46, 10], [20, 10.77, 20], [19.41, 10, 20],
                                  [13.53, 10, 10], [10, 18.57, 10], [10, 20, 11]])

    def test_vectorize_2010a(self):
        cl, poly = self.init_point(21, 2, 11, 4, 10, 20)
        self.assertEqual(cl, '2010')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[10.53, 20, 20], [15.79, 20, 10], [10, 13.53, 10], [10, 19.41, 20], [10.53, 20, 20]])
        self.valid_poly(poly[1], [[20, 11.11, 10], [20, 10, 11], [18.57, 10, 10], [20, 11.11, 10]])

    def test_vectorize_2010b(self):
        cl, poly = self.init_point(21, 8, 11, 4, 10, 20)
        self.assertEqual(cl, '2010')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10.77, 20, 20], [18.46, 20, 10], [20, 13.33, 10], [20, 10, 11], [18.57, 10, 10],
                                  [10, 13.53, 10], [10, 19.41, 20], [10.77, 20, 20]])

    def test_vectorize_2020a(self):
        cl, poly = self.init_point(21, -5, 22, -6, 10, 20)
        self.assertEqual(cl, '2020')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0],
                        [[10.38, 20, 20.0], [14.23, 20, 10.0], [10, 15.93, 10], [10, 19.63, 20], [10.38, 20, 20.0]])
        self.valid_poly(poly[1], [[20, 14.44, 10], [20, 10.74, 20], [19.29, 10, 20], [15.71, 10, 10], [20, 14.44, 10]])

    def test_vectorize_2020b(self):
        cl, poly = self.init_point(21, 5, 22, 6, 10, 20)
        self.assertEqual(cl, '2020')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[10.63, 20, 20], [16.88, 20, 10], [20, 17.06, 10], [20, 11.18, 20], [18.75, 10, 20],
                                  [12.5, 10, 10], [10, 12.67, 10], [10, 19.33, 20], [10.63, 20, 20]])

    def test_vectorize_2020c(self):
        cl, poly = self.init_point(35, 9, 29, 8, 10, 20)
        self.assertEqual(cl, '2020')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[15.77, 20, 20], [19.62, 20, 10], [20, 19.5, 10], [20, 14.5, 20], [15.77, 20, 20]])
        self.valid_poly(poly[1], [[15.71, 10, 20], [10.95, 10, 10], [10, 10.74, 10], [10, 14.44, 20], [15.71, 10, 20]])

    def test_vectorize_0202a(self):
        cl, poly = self.init_point(-5, 21, -6, 22, 10, 20)
        self.assertEqual(cl, '0202')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0],
                        [[15.77, 20, 10.0], [19.62, 20, 20.0], [20, 19.63, 20], [20, 15.93, 10], [15.77, 20, 10.0]])
        self.valid_poly(poly[1], [[14.29, 10, 10], [10.71, 10, 20], [10, 10.74, 20], [10, 14.44, 10], [14.29, 10, 10]])

    def test_vectorize_0202b(self):
        cl, poly = self.init_point(4, 21, 8, 22, 10, 20)
        self.assertEqual(cl, '0202')
        self.assertEqual(len(poly), 1)
        self.valid_poly(poly[0], [[13.53, 20, 10], [19.41, 20, 20], [20, 19.23, 20], [20, 11.54, 10], [18.57, 10, 10],
                                  [11.43, 10, 20], [10, 11.11, 20], [10, 16.67, 10], [13.53, 20, 10]])

    def test_vectorize_0202c(self):
        cl, poly = self.init_point(8, 41, 5, 32, 10, 20)
        self.assertEqual(cl, '0202')
        self.assertEqual(len(poly), 2)
        self.valid_poly(poly[0], [[10.61, 20, 10], [13.64, 20, 20], [10, 15, 20], [10, 19.17, 10], [10.61, 20, 10]])
        self.valid_poly(poly[1], [[20, 14.17, 20], [20, 11.39, 10], [18.15, 10, 10], [14.44, 10, 20], [20, 14.17, 20]])


class TestVectorizeIsobands(PygonizeTest):
    def init_point(self, z1, z2, z3, z4):
        """ Define the 4 points for the test and create a Square.

        :param z1:
        :param z2:
        :param z3:
        :param z4:
        :return:
        """

        self.p1 = Point(10, 20, z1)
        self.p2 = Point(20, 20, z2)
        self.p3 = Point(20, 10, z3)
        self.p4 = Point(10, 10, z4)

        # Create square
        self.sq = marchingsquares.Square(self.p1, self.p2, self.p3, self.p4)

    def test_vectorize_multiple_levels_1(self):
        self.init_point(50, 40, 42, 45)
        polys = self.sq.vectorize_isobands([42, 44, 46])
        self.assertEqual(len(polys), 2)
        self.valid_poly(polys[0], [[16, 20, 44], [18, 20, 42], [20, 10, 42], [13.33, 10, 44], [16, 20, 44]])
        self.valid_poly(polys[1], [[14, 20, 46], [16, 20, 44], [13.33, 10, 44], [10, 10, 45], [10, 12, 46], [14, 20, 46]])

    def test_vectorize_multiple_levels_2(self):
        self.init_point(50, 40, 42, 45)
        polys = self.sq.vectorize_isobands([40, 45, 50])
        self.assertEqual(len(polys), 2)
        self.valid_poly(polys[0], [[15, 20, 45], [20, 20, 40], [20, 10, 42], [10, 10, 45], [15, 20, 45]])
        self.valid_poly(polys[1], [[10, 20, 50], [15, 20, 45], [10, 10, 45], [10, 20, 50]])

    def test_vectorize_multiple_levels_3(self):
        self.init_point(50, 40, 42, 45)
        polys = self.sq.vectorize_isobands([20, 25, 30])
        self.assertEqual(len(polys), 0)

    def test_vectorize_multiple_levels_4(self):
        self.init_point(50, 40, 42, 45)
        polys = self.sq.vectorize_isobands([20, 25, 30, 35, 40])
        self.assertEqual(len(polys), 0)

    def test_vectorize_multiple_levels_5(self):
        self.init_point(50, 40, 42, 45)
        polys = self.sq.vectorize_isobands([20, 25, 30, 35, 40, 45, 50, 55, 60])
        self.assertEqual(len(polys), 2)
        self.valid_poly(polys[0], [[15, 20, 45], [20, 20, 40], [20, 10, 42], [10, 10, 45], [15, 20, 45]])
        self.valid_poly(polys[1], [[10, 20, 50], [15, 20, 45], [10, 10, 45], [10, 20, 50]])

    def test_vectorize_multiple_levels_6(self):
        self.init_point(50, 40, 42, 45)
        polys = self.sq.vectorize_isobands([0, 100])
        self.assertEqual(len(polys), 1)
        self.valid_poly(polys[0], [[10, 20, 50], [20, 20, 40], [20, 10, 42], [10, 10, 45], [10, 20, 50]])

    def test_vectorize_multiple_levels_7(self):
        self.init_point(50, 40, 42, 45)
        polys = self.sq.vectorize_isobands(range(30, 52, 2))
        self.assertEqual(len(polys), 5)
        self.valid_poly(polys[0], [[18, 20, 42], [20, 20, 40], [20, 10, 42], [18, 20, 42]])
        self.valid_poly(polys[1], [[16, 20, 44], [18, 20, 42], [20, 10, 42], [13.33, 10, 44], [16, 20, 44]])
        self.valid_poly(polys[2], [[14, 20, 46], [16, 20, 44], [13.33, 10, 44], [10, 10, 45], [10, 12, 46], [14, 20, 46]])
        self.valid_poly(polys[3], [[12, 20, 48], [14, 20, 46], [10, 12, 46], [10, 16, 48], [12, 20, 48]])
        self.valid_poly(polys[4], [[10, 20, 50], [12, 20, 48], [10, 16, 48], [10, 20, 50]])


if __name__ == '__main__':
    unittest.main()
