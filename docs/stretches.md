# Image stretches

Create a color stretched version of a given image

```
Usage: stretches.py [OPTIONS] <src> <dst> <stretch>

Options:
  --ndv <ndv>               Image NoDataValue(s) (default: -9999)
  -mm, --minmax <min, max>  Stretch minimum and maximum (default: 0, 255)
  --pct <pct>               Linear percent stretch percent (default: 2)
  -f, --format <str>        Output file format (default: GTiff)
  -ot, --dtype <dtype>      Output data type (default: None)
  -v, --verbose             Show verbose messages
  --version                 Show the version and exit.
  -h, --help                Show this message and exit.
```
