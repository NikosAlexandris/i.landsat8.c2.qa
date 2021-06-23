#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 MODULE:       i.landsat8.c2.qa

 AUTHOR(S):    Nikos Alexandris <nik@nikosalexandris.net>
               Stefan Blumentrath <stefan.blumentrath@nina.no>, author of
               i.landsat8.qc

 PURPOSE:      Derive reclassification rules for user requested levels of
               quality conditions for a Landsat 8 Collection 2 Level-1/2
               Quality Assessment band 'QA_PIXEL'

 COPYRIGHT:    (C) 2021 by the GRASS Development Team

               This program is free software under the GNU General Public
               License (>=v2). Read the file COPYING that comes with GRASS
               for details.
"""

#%Module
#% description: Derive reclassification rules for user requested levels of quality conditions for a Landsat 8 Collection 2 Level-1/2 Quality Assessment band
#% keyword: imagery
#% keyword: qa
#% keyword: bitpattern
#% keyword: mask
#% keyword: landsat8
#% keyword: collection-2
#% keyword: level-1
#% keyword: level-2
#% keyword: qa_pixel
#%End

#%option G_OPT_F_OUTPUT
#% description: Output file with reclass rules
#% required: no
#%end

#%option
#% key: designated_fill
#% key_desc: string
#% type: string
#% description: Unacceptable conditions for Designated Fill (bit 0)
#% options: No, Yes
#% multiple: No
#% required : no
#%end

#%option
#% key: terrain_occlusion
#% key_desc: string
#% type: string
#% description: Unacceptable conditions for Terrain Occlusion (bit 1)
#% options: No, Yes
#% multiple: No
#% required : no
#%end

#%option
#% key: radiometric_saturation
#% key_desc: string
#% type: string
#% description: Unacceptable conditions for Radiometric Saturation (bits 2-3)
#% options: No, 1-2, 3-4, 5
#% descriptions: No bands contain saturation, 1-2 bands contain saturation, 3-4 bands contain saturation, 5 or more bands contain saturation
##% descriptions: No;No bands contain saturation;1-2;1-2 bands contain saturation;3-4;3-4 bands contain saturation;5;5 or more bands contain saturation;
#% multiple: No
#% required : no
#%end

#%option
#% key: cloud
#% key_desc: string
#% type: string
#% description: Unacceptable conditions for Cloud (bit 4)
#% options: No, Yes
#% multiple: yes
#% required : no
#%end

#%option
#% key: cloud_confidence
#% key_desc: string
#% type: string
#% description: Unacceptable conditions for Cloud Confidence (bits 5-6)
#% options: Not Determined, Low, Medium, High
#% multiple: yes
#% required : no
#%end

#%option
#% key: cloud_shadow
#% key_desc: string
#% type: string
#% description: Unacceptable conditions for Cloud Shadow Confidence (bits 7-8)
#% options: Not Determined, Low, Medium, High
#% multiple: yes
#% required : no
#%end

#%option
#% key: snow_ice
#% key_desc: string
#% type: string
#% description: Unacceptable conditions for Snow/Ice Confidence (bits 9-10)
#% options: Not Determined, Low, Medium, High
#% multiple: yes
#% required : no
#%end

#%option
#% key: cirrus
#% key_desc: string
#% type: string
#% description: Unacceptable conditions for Cirrus Confidence (bits 11-12)
#% options: Not Determined, Low, Medium, High
#% multiple: yes
#% required : no
#%end

##%option
##% key: reserved_13
## % key_desc: string
##% type: string
##% description: Unacceptable conditions for Reserved (currently not used) (bit 13)
##% options: No, Yes
##% multiple: No
##% required : no
##%end

##%option
##% key: reserved_14
##% key_desc: string
##% type: string
##% description: Unacceptable conditions for Reserved (currently not used) (bit 14)
##% options: No, Yes
##% multiple: No
##% required : no
##%end

##%option
##% key_desc: string
##% key: reserved_15
##% type: string
##% description: Unacceptable conditions for Reserved (currently not used) (bit 15)
##% options: No, Yes
##% multiple: No
##% required : no
##%end

#%rules
#% required: designated_fill,terrain_occlusion,radiometric_saturation,cloud,cloud_confidence,cloud_shadow,snow_ice,cirrus
#%end

import os
import sys
import grass.script as grass

if "GISBASE" not in os.environ:
    print('You must be in GRASS GIS to run this program.')
    sys.exit(1)


"""
Collection 1 Band Quality attributes
https://landsat.usgs.gov/collectionqualityband

0     Designated Fill
1     Terrain Occlusion
2-3   Radiometric Saturation
4     Cloud
5-6   Cloud Confidence
7-8   Cloud Shadow Confidence
9-10  Snow/Ice confidence
11-12 Cirrus confidence
13
14
15
"""

# Binary start positions and length (single or double bits)
quality_binaries = {'designated_fill': (0,1),
        'terrain_occlusion': (1,1),
        'radiometric_saturation': (2,2),
        'cloud': (4,1),
        'cloud_confidence': (5,2),
        'cloud_shadow': (7,2),
        'snow_ice': (9,2),
        'cirrus': (11,2),
        # 'reserved': (13,1),
        # 'reserved': (14,1),
        # 'reserved': (15,1)
        }

"""
For the single bits (0, 1, and 4):
    0 = "No" = This condition does not exist
    1 = "Yes" = This condition exists
"""
single_bits = {'No': '0',
               'Yes': '1'}

"""
For radiometric saturation bits (2-3), read from left to right, represent how many bands contain saturation:

00 - No bands contain saturation
01 - 1-2 bands contain saturation
10 - 3-4 bands contain saturation
11 - 5 or more bands contain saturation
"""
radiometric_saturation = {'No': '00',
                          '1-2': '01',
                          '3-4': '10',
                          '5': '11'}

"""
For the remaining double bits (5-6, 7-8, 9-10, 11-12), read from left to
right, represent levels of confidence that a condition exists:

00 = "Not Determined" = Algorithm did not determine the status of this
condition / "No" = This condition does not exist

01 = "Low" = Algorithm has low to no confidence that this condition exists
(0-33 percent confidence)

10 = "Medium" = Algorithm has medium confidence that this condition exists
(34-66 percent confidence)

11 = "High" = Algorithm has high confidence that this condition exists
(67-100 percent confidence
"""
double_bits = {'Not Determined': '00',
               'Low': '01',
               'Medium': '10',
               'High': '11'}

def main():

    output = options.pop('output')

    # List for user requested levels of quality conditions
    conditions = []
    for condition in options.keys():
        if options[condition]:
            conditions.append(condition)

    # Check user requested quality levels for sanity
    for condition in conditions:
        if len(options[condition].split(',')) >= 4:
            message="""All conditions for {} specified as unnacceptable, this
            will result in an empty map"""
            message = message.format(condition)
            grass.fatal(message)

    # Length and maximum integer representation of Landsat8 QA binary strings
    number_of_bits = 16
    max_int = int(''.join([str(1)] * number_of_bits), 2)

    # List for categories of unacceptable quality conditions in the QA band
    categories = []

    # Loop over integer representations of a 16-bit binary pattern
    for category in range(max_int + 1):

        # Get the binary equivalent of the integer value
        integer_string = '{0:016b}'.format(category)
        integer_length = len(integer_string)

        # Loop over the user-defined quality conditions bit-pattern filter elements
        for condition in conditions:

            binary_start, binary_length = quality_binaries[condition]  # a tuple
            binary_end = binary_start + binary_length
            integer_start = integer_length - binary_end
            integer_end = integer_length - binary_start
            quality_bits = integer_string[integer_start:integer_end]

            # User requested levels of unacceptable quality conditions
            for quality_level in options[condition].split(','):

                if binary_length == 1:
                    requested_bits = single_bits[quality_level]

                else:

                    if condition == 'radiometric_saturation':
                        requested_bits = radiometric_saturation[quality_level]

                    else:
                        requested_bits = double_bits[quality_level]

                # Collect requested quality bits for reclassification
                if requested_bits == quality_bits:

                    categories.append(str(category) + ' = NULL')
                    break

            # Avoid duplicates in reclass rules when several filter are applied
            if requested_bits == quality_bits:
                break

    # Construct rules for reclassification
    reclassification_rules = '\n'.join(categories) + '\n* = 1\n'

    # Print to stdout if no output file is specified
    if not output:
            sys.stdout.write(reclassification_rules)

    else:
        with open(output, 'w') as o:
            o.write(reclassification_rules)

if __name__ == "__main__":
    options, flags = grass.parser()
    sys.exit(main())
