##Sample=vector
##Map=raster
##Attribute=string 'TRUTH'
##Output=output file

from qgis.core import *
from qgis.utils import iface
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from osgeo import ogr, osr
import numpy as np
import gdal
import os
#import sys

import logging
import os
import sys

import numpy as np
try:
    from osgeo import gdal
    from osgeo import ogr
except:
    import gdal
    import ogr



ogr.UseExceptions()
ogr.RegisterAll()
gdal.PushErrorHandler('CPLQuietErrorHandler')


__version__ = '0.1.0'

VERBOSE = False

gdal.UseExceptions()
gdal.AllRegister()

ogr.UseExceptions()
ogr.RegisterAll()

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.INFO,
                    datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


def rasterize_map(raster_file, vector_file, attribute, layer=1):
    """ Rasterizes vector file to extent/size of raster """
    # Open raster file

    raster_ds = gdal.Open(raster_file, gdal.GA_ReadOnly)
    raster = raster_ds.GetRasterBand(1).ReadAsArray()
    logger.debug('Read in raster file')

    # Get raster NoDataValue
    ndv = raster_ds.GetRasterBand(1).GetNoDataValue()
    if not ndv:
        logger.warning('Could not find NoDataValue for raster')
        logger.warning('Setting NoDataValue to 0')
        ndv = 0

    # Open vector file
    vector = ogr.Open(vector_file)
    logger.debug('Opened vector file')

    # Try getting layer - try by index if layer is int, or string if not
    try:
        layer = int(layer)
    except:
        pass

    if isinstance(layer, int):
        logger.debug('Trying to open layer by index')

        layer = vector.GetLayerByIndex(layer)
        if layer is None:
            logger.debug('Could not open layer by index... trying by name')
            layer = str(layer)
        else:
            logger.debug('Opened layer by index')

    if isinstance(layer, str):
        # GetLayerByName
        logger.debug('Trying to open layer by name {n}'.format(n=layer))
        layer = vector.GetLayerByName(layer)


        logger.debug('Opened layer by name')

    # Try to get attribute by name
    layer_defn = layer.GetLayerDefn()
    field_names = []
    for i in range(layer_defn.GetFieldCount()):
        field_defn = layer_defn.GetFieldDefn(i)
        field_names.append(field_defn.GetName())

    if attribute not in field_names:
        logger.error(
            'Cannot find attribute {a} in vector file'.format(a=attribute))
        logger.error('Available attributes are: {f}'.format(f=field_names))
    logger.debug('Found attribute {a} in vector file'.format(a=attribute))

    # If we've passed checks so far, setup memory raster
    logger.debug('Setting up memory raster for rasterization')
    mem_driver = gdal.GetDriverByName('MEM')

    mem_ds = mem_driver.Create('',
                               raster_ds.RasterXSize,
                               raster_ds.RasterYSize,
                               1,
                               raster_ds.GetRasterBand(1).DataType)
    mem_ds.SetProjection(raster_ds.GetProjection())
    mem_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    logger.debug('Set up memory dataset for rasterization')

    # Fill with NDV
    mem_ds.GetRasterBand(1).Fill(ndv)

    # Rasterize
    status = gdal.RasterizeLayer(mem_ds,
                                 [1],
                                 layer,
                                 None, None,
                                 burn_values=[ndv],
                                 options=['ALL_TOUCHED=FALSE',
                                          'ATTRIBUTE={a}'.format(a=attribute)]
                                 )

    if status != 0:
        logger.error('Could not rasterize vector')
    else:
        logger.debug('Rasterized vector file')

    # Get raster from dataset and return
    print(np.unique(mem_ds.GetRasterBand(1).ReadAsArray()))
    return (mem_ds.GetRasterBand(1).ReadAsArray(), raster, ndv)


def crosstabulate(rasterized, raster, ndv=0):
    """ Crosstabulate raster against rasterized vector file """
    # Find all values in either dataset
    uniqs = np.unique(np.concatenate([
        np.unique(rasterized[rasterized != ndv]),
        np.unique(raster[raster != ndv])]))

    # Crosstabulate
    tab = np.zeros((uniqs.size, uniqs.size))

    for i, uv_row in enumerate(uniqs):
        for j, uv_col in enumerate(uniqs):
            tab[i, j] = (raster[rasterized == uv_row] == uv_col).sum()
    logger.debug('Crosstabulated map with reference data')

    # Setup array headers
    rownames = np.array(['Ref-Class_' + str(u)
                         for u in uniqs])[:, np.newaxis]
    colnames = ['']
    colnames.extend(['Map-Class_' + str(u) for u in uniqs])

    pretty_tab = np.hstack((rownames, np.char.mod('%i', tab)))
    pretty_tab = np.vstack((colnames, pretty_tab))

    # Return with reference labels across & map labels down
    return pretty_tab.T

if not os.path.isfile(Map):
    logging.error('Input raster map {r} does not exist'.format(r=Map))


# Layer in shapefile
layer = 0

# Rasterize vector file
rasterized, raster_image, ndv = rasterize_map(
    Map, Sample, Attribute, layer=layer)

# Crosstabulate
crosstab = crosstabulate(rasterized, raster_image, ndv=ndv)

with open(Output, 'w') as f:
    np.savetxt(f, crosstab, fmt='%s', delimiter=',')

