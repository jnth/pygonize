# pygonize

Polygonize raster data into vector.  
It's depend of `shapely`, `numpy`, `gdal` and `pyshp` libraries.


## Install

    python setup.py install


## Example of use

    import pygonize
    p = pygonize.Pygonize()
    p.read_raster('/path/of/input/raster')
    p.write_shapefile([0, 10, 20, 30, 40, 50], '/path/of/output/shapefile.shp')
