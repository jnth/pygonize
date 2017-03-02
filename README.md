# pygonize

Polygonize raster data into polygons vector.  
It's depend of `shapely`, `numpy`, `pyshp` and `GDAL` libraries.  

This script is under development and work with Python 3.5 and 3.6.

[![Build Status](https://travis-ci.org/jnth/pygonize.svg?branch=master)](https://travis-ci.org/jnth/pygonize)



## Install

Clone this repository :

    $ git clone https://github.com/jnth/pygonize.git
    $ cd pygonize

Create virtual environnement :

    $ python3.6 -m pyvenv env
    $ source env/bin/activate

Install dependencies :

    $ pip install -r requirements.txt



## Testing

    $ python -m unittest discover test/
    


## Example of use

    import pygonize
    print(pygonize.__version__)  # show the version
    
    # To get logging message...
    import logging
    log = logging.getLogger('pygonize')
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler())

    # Using the library
    p = pygonize.Pygonize()
    p.read_raster('/path/of/input/raster')
    p.write_shapefile([0, 10, 20, 30, 40, 50], '/path/of/output/shapefile.shp')
    


## To do

See [TODO.md](TODO.md) for details.







[Andreas Hilboll]: http://www.iup.uni-bremen.de/~hilboll/blog/2013/2013-10_installing-gdal-in-a-virtualenv.html
