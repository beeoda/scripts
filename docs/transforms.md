# Image transforms

Compute image transformations, including vegetation indices or the Tasseled Cap, for an input image

```
Usage: transforms.py [OPTIONS] <src> <dst> <transform>

Options:
  -f, --format <str>    Output file format (default: GTiff)
  -ot, --dtype <dtype>  Output data type (default: None)
  --scaling <scaling>   Scaling factor for reflectance (default: 10,000)
  --sensor <sensor>     Landsat sensor type (for Tasseled Cap) (default: LT5)
  --blue <int>          Band number for blue band in <src> (default: 1)
  --green <int>         Band number for green band in <src> (default: 2)
  --red <int>           Band number for red band in <src> (default: 3)
  --nir <int>           Band number for near IR band in <src> (default: 4)
  --swir1 <int>         Band number for first SWIR band in <src> (default: 5)
  --swir2 <int>         Band number for second SWIR band in <src> (default: 6)
  -v, --verbose         Show verbose messages
  --version             Show the version and exit.
  -h, --help            Show this message and exit.
```
