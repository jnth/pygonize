#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Pygonize: polygonize raster data into isoband vector. """


from setuptools import setup
import pygonize

req = [l.strip() for l in open('requirements.txt').readlines() if l.strip()]

setup(name='pygonize',
      version=pygonize.__version__,
      description='Polygonize raster data into isoband vector.',
      author='jnth',
      author_email='jonathan.virga@gmail.com',
      packages=['pygonize'],
      install_requires=req
      )
