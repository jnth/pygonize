#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Creating raster dataset to test. """

from osgeo import gdal
import numpy


# Configuration
x0, y0 = 898879, 6317011
dx, dy = 25, 25
nx, ny = 5, 5
dat = [[500, 450, 400, 300, 200],
       [460, 440, 410, 300, 250],
       [450, 430, 420, 380, 350],
       [455, 470, 440, 420, 400],
       [460, 465, 470, 460, 450]]
fno = '../test/data/raster.tif'

# Create raster dataset
driver = gdal.GetDriverByName('GTiff')
dst_ds = driver.Create(fno, nx, ny, 1, gdal.GDT_UInt16)
dst_ds.SetGeoTransform([x0, dx, 0, y0, 0, -dy])

raster = numpy.array(dat)
dst_ds.GetRasterBand(1).WriteArray(raster)

dst_ds = None  # close dataset

