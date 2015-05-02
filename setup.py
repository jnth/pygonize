#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Pygonize: polygonize raster data. """


from setuptools import setup


setup(name='pygonize',
      version='1.0rc2',
      description='Polygonize raster data into vector.',
      author='jnth',
      author_email='jonathan.virga@gmail.com',
      packages=['pygonize'],
      install_requires=['numpy', 'shapely', 'gdal', 'pyshp']
      )
