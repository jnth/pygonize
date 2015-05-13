# pygonize

Polygonize raster data into polygons vector.  
It's depend of `shapely`, `numpy`, `pyshp` and `GDAL` libraries.  

This script is under development...



## Install

Clone this repository :

    $ git clone https://github.com/jnth/pygonize.git
    $ cd pygonize

Create virtual environnement :

    $ virtualenv env
    $ source env/bin/activate

Install dependencies `numpy`, `shapely` and `pyshp` :

    $ pip install numpy shapely pyshp

Install GDAL from source or from your distribution.  
__The version of the Python bindings must match the GDAL library version.__
(source [Andreas Hilboll])  
`gdal-config` is used to view the installed GDAL version :

    $ gdal-config --version

Install the GDAL Python bindings (update the version number below) :

    $ pip install GDAL==1.8.1

Check your GDAL installation :

    $ python -c "from osgeo import gdal"

This command must return nothing.

Install of `pygonize` :

    $ python setup.py install



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
