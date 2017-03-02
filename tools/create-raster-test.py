#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Creating raster dataset to test. """


import rasterio
import affine
import numpy


# Configuration
fno = '../test/data/raster.tif'
x0, y0 = 898879, 6317011
dx, dy = 25, 25
dat = numpy.array(
    [[500, 450, 400, 300, 200],
     [460, 440, 410, 300, 250],
     [450, 430, 420, 380, 350],
     [455, 470, 440, 420, 400],
     [460, 465, 470, 460, 450]],
    dtype=numpy.int16
)


# Create raster dataset
ny, nx = dat.shape
aff = affine.Affine(dx, 0, x0, 0, -dy, y0)
with rasterio.open(fno, 'w', driver='GTiff', height=ny, width=nx, count=1,
                   dtype=rasterio.dtypes.int16, affine=aff) as rst:
    rst.write(dat, 1)
