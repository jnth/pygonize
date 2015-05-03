#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Pygonize: polygonize raster data into isoband vector. """


from setuptools import setup


setup(name='pygonize',
      version='0.1.dev1',
      description='Polygonize raster data into isoband vector.',
      author='jnth',
      author_email='jonathan.virga@gmail.com',
      packages=['pygonize'],
      install_requires=['numpy', 'shapely', 'gdal', 'pyshp']
      )
