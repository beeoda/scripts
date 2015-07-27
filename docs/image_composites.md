# Image composites

Create image composites of many images with "best available pixel" data based on some criteria

```
Usage: image_composites.py [OPTIONS] [INPUTS]... OUTPUT

  Create image composites based on some criteria

  Output image composites retain original values from input images that meet
  a certain criteria. For example, in a maximum NDVI composite with 10 input
  images, all bands for a given pixel will contain the band values from the
  input raster that had the highest NDVI value.

  Users can choose from a set of predefined compositing algorithms or may
  specify an Snuggs S-expression that defines the compositing criteria.
  Normalized Differenced indexes can be computed using "(normdiff a b)" for
  the Normalized Difference between "a" and "b" (or "nir" and "red"). See
  https://github.com/mapbox/snuggs for more information on Snuggs
  expressions.

  The indexes for common optical bands (e.g., red, nir, blue) within the
  input rasters are included as optional arguments and are indexed in
  wavelength sequential order. You may need to overwrite the default indexes
  of bands used in a given S-expression with the correct band index.
  Additional bands may be identified and indexed using the '--band
  NAME=INDEX' option.

  Currently, input images must be "stacked", meaning that they contain the
  same bands and are the same shape and extent.

  Example:

  1. Create a composite based on maximum NDVI

      Use the built-in maxNDVI algorithm:

          $ image_composite.py --algo maxNDVI image1.gtif image2.gtif image3.gtif
              composite_maxNDVI.gtif

      or with S-expression:

          $ image_composite.py --expr '(max (/ (- nir red) (+ nir red)))'
              image1.gtif image2.gtif image3.gtif composite_maxNDVI.gtif

      or with S-expressions using the normdiff shortcut:

          $ image_composite.py --expr '(max (normdiff nir red))'
              image1.gtif image2.gtif image3.gtif composite_maxNDVI.gtif

  2. Create a composite based on median EVI (not recommended)

      With S-expression:

          $ evi='(median (/ (- nir red) (+ (- (+ nir (* 6 red)) (* 7.5 blue)) 1)))'
          $ image_composite.py --expr "$evi"  image1.gtif image2.gtif image3.gtif
              composite_medianEVI.gtif

  3. Create a composite based on median NBR

      With S-expression:

          $ image_composite.py --expr '(median (normdiff nir sswir))'
              image1.gtif image2.gtif image3.gtif composite_maxNBR.gtif

Options:
  --algo [maxNDVI|maxNIR|ZheZhu|medianNDVI|minBlue]
                                  Create composite based on specific algorithm
  --expr SNUGGS                   Create composite based on an expression
  -of, --format TEXT              Output image format
  --co NAME=VALUE                 Driver specific creation options.See the
                                  documentation for the selected output driver
                                  for more information.
  --blue INTEGER                  Band number for blue band in INPUTS
                                  (default: 1)
  --green INTEGER                 Band number for green band in INPUTS
                                  (default: 2)
  --red INTEGER                   Band number for red band in INPUTS (default:
                                  3)
  --nir INTEGER                   Band number for near IR band in INPUTS
                                  (default: 4)
  --fswir INTEGER                 Band number for first SWIR band in INPUTS
                                  (default: 5)
  --sswir INTEGER                 Band number for second SWIR band in INPUTS
                                  (default: 6)
  --band NAME=INDEX               Name and band number in INPUTS for
                                  additional bands
  -m, --mask_band INTEGER         Mask data in INPUTS with mask band
  -mv, --mask_val INTEGER         Mask data in INPUTS with these values in
                                  mask band
  -v, --verbose                   Show verbose messages
  -q, --quiet                     Do not show progress or messages
  --version                       Show the version and exit.
  -h, --help                      Show this message and exit.
```
