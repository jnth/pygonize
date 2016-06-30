#!/usr/bin/env python
# coding: utf-8

import pygonize
print(pygonize.__version__)
print(pygonize.__file__)

# To get logging message...
import logging
log = logging.getLogger('pygonize')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

# Using the library
p = pygonize.Pygonize()
p.read_raster('./test/data/raster.tif')
p.write_shapefile(range(200, 600, 100), '/tmp/shapefile.shp')


