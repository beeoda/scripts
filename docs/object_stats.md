# Object statistics

Calculate a summary statistic of pixels within each segment for an input image

```
usage: object_stats.py [-h] [-of FORMAT] [-b [BANDS [BANDS ...]]] [--version]
                       [--verbose]
                       image segment output [stat [stat ...]]

Calculate a given statistic for pixels in each segment

positional arguments:
  image                 input image raster file
  segment               input segment raster file
  output                output raster file
  stat                  statistic to calculate (mean, var, num, max, min, sum,
                        mode)

optional arguments:
  -h, --help            show this help message and exit
  -of FORMAT            GDAL format for output file (default "GTiff")
  -b [BANDS [BANDS ...]], --bands [BANDS [BANDS ...]]
                        Bands within input image to process
  --version             show program's version number and exit
  --verbose, -v         increase output verbosity
```
