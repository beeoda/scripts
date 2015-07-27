# Sample map

Generate a stratified or simple random sample from a map

```
Generate random sample of a map

Usage:
    sample_map.py [options] (simple | stratified | systematic) <map>

Options:
    --allocation <allocation>   Sample allocation
    --size <n>                  Sample size for allocation [default: 500]
    --mask <values>             Values to be excluded from sample [default: 0]
    --order                     Order or sort output samples by strata
    --ndv <NoDataValue>         NoDataValue for output raster [default: 255]
    --raster <filename>         Raster filename [default: sample.gtif]
    --rformat <format>          Raster file format [default: GTiff]
    --vector <filename>         Vector filename [default: sample.shp]
    --vformat <format>          Vector file format [default: ESRI Shapefile]
    --seed_val <seed_value>     Initial RNG seed value [default: None]
    -v --verbose                Show verbose debugging messages
    -h --help                   Show help

Sample size (--size) "<n>" options:
    <specified>                 Specify an integer for sample count
    variance                    Estimate sample count from variance formula

Allocation (--allocation) "<allocation>" options:
    proportional                Allocation proportional to area
    good_practices              "Good Practices" allocation
    equal                       Equal allocation across classes
    <specified>                 Comma or space separated list of integers

Example:

    Output stratified random sample using specified allocation to a shapefile
        and raster image in a randomized order and a specified seed value.

    > sample_map.py -v --size 200 --allocation "50 25 25 100"
    ... --mask 0 --ndv 255
    ... --raster output.gtif --vector samples.shp --seed 10000
    ... stratified input_map.gtif

```
