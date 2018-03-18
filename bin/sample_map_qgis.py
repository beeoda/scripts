##Allocation=string '0 0 0'
###NoData=number 0
##Map=raster
##Output=output file

from qgis.core import *
from qgis.utils import iface
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import logging
import os
import sys

import numpy as np
try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except:
    import gdal
    import ogr
    import osr

__version__ = '0.1.0'

_allocation_methods = ['proportional', 'equal', 'good_practices']

VERBOSE = False

gdal.UseExceptions()
gdal.AllRegister()

ogr.UseExceptions()
ogr.RegisterAll()

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.INFO,
                    datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


def str2num(string):
    """ parse string into int, or float """
    try:
        v = int(string)
    except ValueError:
        v = float(string)
    return v


def random_stratified(image, classes, counts):
    """
    Return pixel strata, row, column from within image from a random stratified
    sample of classes specified
    Args:
        image (ndarray)         input map image
        classes (ndarray)       map image classes to be sampled
        counts (ndarray)        map image class sample counts
    Return:
        (strata, col, row)      tuple of ndarrays
    """
    # Initialize outputs
    strata = np.array([])
    rows = np.array([])
    cols = np.array([])

    logger.debug('Performing sampling')

    for c, n in zip(classes, counts):
        logger.debug('Sampling class {c}'.format(c=c))

        # Find pixels containing class c
        row, col = np.where(image == c)

        # Check for sample size > population size
        if n > col.size:
            logger.warning(
                'Class {0} sample size larger than population'.format(c))
            logger.warning('Reducing sample count to size of population')

            n = col.size

        # Randomly sample x / y without replacement
        # NOTE: np.random.choice new to 1.7.0...
        # TODO: check requirement and provide replacement
        samples = np.random.choice(col.size, n, replace=False)

        logger.debug('    collected samples')

        strata = np.append(strata, np.repeat(c, n))
        rows = np.append(rows, row[samples])
        cols = np.append(cols, col[samples])

    return (strata, cols, rows)


def random_simple(image, classes, count):
    """
    Return pixel strata, row, column from within image from a simple random
    sample of classes specified. The strata returned will be all equal to 1
    because there are no strata in a non-stratified design.
    Args:
        image (ndarray)         input map image
        classes (ndarray)       map image classes to be sampled
        counts (ndarray)        map image class sample counts
    Return:
        (strata, col, row)      tuple of ndarrays
    """
    # Check
    if isinstance(count, np.ndarray):
        if count.ndim > 1 or count[0].ndim > 1:
            logger.error('Allocation for simple random sample must be one \
                number')
            logger.error('Allocation was:')
            logger.error(count)
            sys.exit(1)
        else:
            count = count[0]

    logger.debug('Performing sampling')

    # Find all pixels in `image` in `classes` and store locations
    rows, cols = np.where(np.in1d(image, classes).reshape(image.shape))

    if count > cols.size:
        logger.error('Sample size greater than population of all classes \
            included')
        logger.error('Sample count: {n}'.format(n=count))
        logger.error('Population size: {n}'.format(n=cols.size))
        sys.exit(1)

    # Sample some of these locations
    sample = np.random.choice(cols.size, count, replace=False)
    logger.debug('    collected samples')

    return (np.ones(count), cols[sample], rows[sample])


def random_systematic(image, classes, counts):
    """ """
    raise NotImplementedError(
        "Sorry - haven't added Systematic Sampling")


def sample(image, method,
           size=None, allocation=None,
           mask=None, order=False):
    """
    Make sampling decisions and perform sampling
    Args:
      image (np.ndarray): 1 dimensional array of the image
      method (str): Sampling method
      size (int, optional): Total sample size
      allocation (str, or list/np.ndarray): Allocation strategy specified as a
        string, or user specified allocation as list or np.ndarray
      mask (list or np.ndarray, optional): Values to exclude from `image`
      order (bool, optional): Order the output by strata, or not
    Returns:
        output (tuple): strata, row numbers, and column numbers
    """
    # Find map classes within image
    classes = np.sort(np.unique(image))

    # Exclude masked values
    classes = classes[~np.in1d(classes, mask)]

    logger.debug('Found {n} classes'.format(n=classes.size))
    for c in classes:
        px = np.sum(image == c)
        logger.debug(
            '    class {c} - {pix}px ({pct}%)'.format(
                c=c,
                pix=px,
                pct=np.round(float(px) / image.size * 100.0, decimals=2)))

    # Determine class counts from allocation type and total sample size
    if allocation is None:
        counts = size
    elif isinstance(allocation, str):
        # If allocationd determined by method, we must specify a size
        if not isinstance(size, int):
            raise TypeError('Must specify sample size if allocation to '
                            'calculate allocation')
        raise NotImplementedError(
            "Sorry - haven't added any allocation types")

    # Or use specified allocation
    elif isinstance(allocation, list):
        counts = np.array(allocation)
    elif isinstance(allocation, np.ndarray):
        if allocation.ndim != 1:
            raise TypeError('Allocation must be 1D array')
        counts = allocation
    else:
        raise TypeError(
            'Allocation must be a str for a method, or a list/np.ndarray')

    # Ensure we found allocation for each class if stratified random
    if method == 'stratified':
        if classes.size != counts.size:
            raise ValueError(
                'Sample counts must be given for each unmasked class in map')

    # Perform sample using desired method
    if method == 'stratified':
        strata, cols, rows = random_stratified(image, classes, counts)
    elif method == 'random':
        strata, cols, rows = random_simple(image, classes, counts)
    elif method == 'systematic':
        strata, cols, rows = random_systematic(image, classes, counts)

    # Randomize samples if not ordered
    if order is not True:
        logger.debug('Randomizing order of samples')
        sort_index = np.random.choice(strata.size, strata.size, replace=False)

        strata = strata[sort_index]
        cols = cols[sort_index]
        rows = rows[sort_index]

    return (strata, cols, rows)


def write_raster_output(strata, cols, rows, map_ds, output,
                        gdal_frmt='GTiff', ndv=255):
    """
    """
    # Init and fill output array with samples
    raster = np.ones((map_ds.RasterYSize, map_ds.RasterXSize),
                     dtype=np.uint8) * ndv

    for s, c, r in zip(strata, cols, rows):
        raster[r, c] = s

    # Get output driver
    driver = gdal.GetDriverByName(gdal_frmt)

    # Create output dataset
    sample_ds = driver.Create(output,
                              map_ds.RasterXSize, map_ds.RasterYSize, 1,
                              gdal.GetDataTypeByName('Byte'))

    # Write out band
    sample_ds.GetRasterBand(1).SetNoDataValue(ndv)
    sample_ds.GetRasterBand(1).WriteArray(raster)

    # Port over metadata, projection, geotransform, etc
    sample_ds.SetProjection(map_ds.GetProjection())
    sample_ds.SetGeoTransform(map_ds.GetGeoTransform())
    sample_ds.SetMetadata(map_ds.GetMetadata())

    # Close
    sample_ds = None


def write_vector_output(strata, cols, rows, map_ds, output,
                        ogr_frmt='ESRI Shapefile'):
    """
    """
    # Corners of pixel in pixel coordinates
    corners = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]

    # Raster geo-transform
    gt = map_ds.GetGeoTransform()
    # Get OSR spatial reference from raster to give to OGR dataset
    map_sr = osr.SpatialReference()
    map_sr.ImportFromWkt(map_ds.GetProjectionRef())

    # Get OGR driver
    driver = ogr.GetDriverByName(ogr_frmt)
    # Create OGR dataset and layer
    sample_ds = driver.CreateDataSource(output)
    layer = sample_ds.CreateLayer('sample', map_sr, geom_type=ogr.wkbPolygon)

    # Add fields for layer
    # Sample ID field
    layer.CreateField(ogr.FieldDefn('ID', ogr.OFTInteger))
    # Row/Col fields
    layer.CreateField(ogr.FieldDefn('ROW', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('COL', ogr.OFTInteger))
    # Strata field
    layer.CreateField(ogr.FieldDefn('STRATUM', ogr.OFTInteger))

    # Loop through samples adding to layer
    for i, (stratum, col, row) in enumerate(zip(strata, cols, rows)):
        # Feature
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetField('ID', i)
        feature.SetField('ROW', row)
        feature.SetField('COL', col)
        feature.SetField('STRATUM', stratum)

        # Geometry
        ring = ogr.Geometry(type=ogr.wkbLinearRing)

        for corner in corners:
            ring.AddPoint(
                gt[0] + (col + corner[0]) * gt[1] + (row + corner[1]) * gt[2],
                gt[3] + (col + corner[1]) * gt[4] + (row + corner[1]) * gt[5])
        square = ogr.Geometry(type=ogr.wkbPolygon)
        square.AddGeometry(ring)

        feature.SetGeometry(square)

        layer.CreateFeature(feature)

        feature.Destroy()

    sample_ds = None


def main():
    """ Read in arguments, test them, then sample map """
    ### Read in and test arguments
    # Read in inputs
    image_fn = Map

    method = 'stratified'

    # Test if allocation is built-in; if not then it needs to be list of ints
    allocation = np.array([str2num(i) for i in
                           Allocation.replace(',', ' ').split(' ') if
                           i != ''])
    size = np.sum(allocation)


    output_vector = Output

    ### Finally do some real work
    # Read in image
    try:
        image_ds = gdal.Open(image_fn, gdal.GA_ReadOnly)
    except:
        logger.error('Could not open {f}'.format(f=image_fn))
        sys.exit(1)

    image = image_ds.GetRasterBand(1).ReadAsArray()
    logger.debug('Read in map image to be sampled')

    # Do the sampling
    strata, cols, rows = sample(image, method,
                                size=size,
                                allocation=allocation,mask=NoData)
    logger.debug('Finished collecting samples')

    image = None

    # Write outputs
    if output_vector is not None:
        logger.debug('Writing vector output to {f}'.format(f=output_vector))
        write_vector_output(strata, cols, rows,
                            image_ds, output_vector)

    logger.debug('Sampling complete')

main()
