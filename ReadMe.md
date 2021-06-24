DESCRIPTION
-----------

Landsat Collection 2 Level-1 and Level-2 Quality Assessment (QA) bands
(`QA_PIXEL`) provide useful information to users wanting to optimize the value
of pixels as a first level indicator of certain conditions within Landsat data.

The *i.landsat8.c2l2.qc* module generates rules which can be used with
[r.reclass](r.reclass.html) to reclassify the `QA_PIXEL` band according to
user-requested pixel quality characteristics and create new raster maps that
can function as masks. In the output raster map, the _requested qualities will
be set to `NULL` and all other values to `1`_. Filtering then observations
(pixels) of other Landsat bands is easy with the use of `r.mask`.

> Requesting for `cloud=Yes` means that cloudy observations will be set to
> `NULL`, so they can be masked out in a subsequent masking step. All of the
> rest of pixels will be set to `1`, meaning they will be retained after
> masking.

The Quality Assessment (`QA_PIXEL`) band from Landsat8 contains 16bit integer
values that represent _bit-packed combinations of surface, atmosphere, and
sensor conditions that can affect the overall usefulness of a given pixel_. The
`QA_PIXEL` band is available for Landsat 8 OLI/TIRS Collection 2, Level **1** &
Level **2** products.

The following quality relevant conditions are represented as _single bits_ in
the Landsat8 QA band:

| Flag          | Bit Position |
|---------------|--------------|
| Fill          | 0            |
| Dilated Cloud | 1            |
| Cirrus        | 2            |
| Cloud         | 3            |
| Cloud Shadow  | 4            |
| Snow          | 5            |
| Clear         | 6            |
| Water         | 7            |

Possible choices for _single bit_ flags:

| Value | Description                                     | Bit representation |
|-------|-------------------------------------------------|--------------------|
| No    | No or low confidence or not high confidence     | 0                  |
| Yes   | Fill image or Cloud dilation or High confidence | 1                  |

The following quality relevant conditions are represented as _double bits_ in
the Landsat8 QA band:

| Flag                    | Bit Position |
|-------------------------|--------------|
| Cloud Confidence        | 8-9          |
| Cloud Shadow Confidence | 10-11        |
| Snow/Ice Confidence     | 12-13        |
| Cirrus Confidence       | 14-15        |

Possible choices for the _double bit_ flags:

| Value | Description                     | Bit representation |
|-------|---------------------------------|--------------------|
| No    | No confidence level set         | 00                 |
| Low   | Low confidence                  | 01                 |
| Maybe | Medium confidence (or Reserved) | 10                 |
| High  | High confidence                 | 11                 |

NOTES
-----

> This module is largely based on
> [i.landsat8.qa](https://gitlab.com/NikosAlexandris/i.landsat8.qa) which was
> based on older versions of i.landsat.qc (see [Remove i.landsat8.qc (replaced
> by i.landsat.qa)
> (#505)](https://github.com/OSGeo/grass-addons/commit/1e9d32fc15c771fa423c2ecde2dfe000b6255858)

EXAMPLE
-------

Let's create a `water` raster mask:

    i.landsat8.c2.qa water=Yes output=qa_water.rules

    r.reclass input=QA_PIXEL rules=qa_water.rules output=water_mask

where:

-   **`water=`** the quality flag of interest

-   **`output=`** the name for the file to write the generated reclassification
    rules

![Water mask][water-mask]

[water-mask]: figures/water_mask.png

and the same example with the addition of the **`i`** flag which will invert
the generated reclassification rules -- think of an inverted mask!

    i.landsat8.c2.qa -i water=Yes output=qa_inverted_water.rules

    r.reclass input=QA_PIXEL rules=qa_inverted_water.rules output=inverted_water_mask

![Inverted water mask][inverted-water-mask]

[inverted-water-mask]: figures/inverted_water_mask.png

SEE ALSO
--------

*[r.reclass](r.reclass.html), [i.modis.qc](i.modis.qc.html), [r.bitpattern](r.bitpattern.html), [i.landsat8.swlst](i.landsat8.swlst.html)*

REFERENCES
----------

- [Landsat 8-9Operational Land Imager (OLI) -Thermal Infrared Sensor
  (TIRS)Collection 2 Level 1 (L1)Data Format Control Book
  (DFCB)](https://prd-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/atoms/files/LSDS-1822_Landsat8-9-OLI-TIRS-C2-L1-DFCB-v6.pdf)
- [Landsat 8-9Operational Land Imager (OLI) - Thermal Infrared Sensor (TIRS)
  Collection 2 Level 2 (L2) Data Format Control Book
  (DFCB)](https://prd-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/atoms/files/LSDS-1328_Landsat8-9-OLI-TIRS-C2-L2-DFCB-v6.pdf).

AUTHOR
------

Nikos Alexandris, Joint Research Centre, European Commission, Ispra (Italy)
