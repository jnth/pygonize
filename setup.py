#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Pygonize: polygonize raster data into isoband vector. """


from setuptools import setup
import pygonize

setup(name='pygonize',
      version=pygonize.__version__,
      description='Polygonize raster data into isoband vector.',
      author='jnth',
      author_email='jonathan.virga@gmail.com',
      packages=['pygonize'],
      install_requires=['numpy>=1.6.1', 'shapely>=1.3.0', 'gdal>=1.10.0', 'pyshp>=1.1.4']
      )
