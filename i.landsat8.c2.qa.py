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

#%flag
#%  key: i
#%  description: Invert output of user requested quality assessment flags
#%  guisection: Input
#%end

#%option G_OPT_F_OUTPUT
#% description: Output file with reclass rules
#% required: no
#%end

#%option
#% key: fill
#% key_desc: string
#% type: string
#% description: Fill data (Yes) or Image data (No) (bit 0)
#% options: Fill, Image
#% multiple: No
#% required : no
#%end

#%option
#% key: dilated_cloud
#% key_desc: string
#% type: string
#% description: Dilated clouds (bit 1)
#% options: No, Yes
#% multiple: No
#% required : no
#%end

#%option
#% key: cirrus
#% key_desc: string
#% type: string
#% description: High confidence cirrus (bit 2)
#% options: No, Yes
#% multiple: yes
#% required : no
#%end

#%option
#% key: cloud
#% key_desc: string
#% type: string
#% description: High confidence cloud (bit 3)
#% options: No, Yes
#% multiple: yes
#% required : no
#%end

#%option
#% key: cloud_shadow
#% key_desc: string
#% type: string
#% description: High confidence cloud shadow (bit 4)
#% options: No, Yes
#% multiple: yes
#% required : no
#%end

#%option
#% key: snow
#% key_desc: string
#% type: string
#% description: High confidence snow (bit 5)
#% options: No, Yes
#% multiple: yes
#% required : no
#%end

#%option
#% key: clear
#% key_desc: string
#% type: string
#% description: No cloud or dilated cloud (bit 6)
#% options: No, Yes
#% multiple: yes
#% required : no
#%end

#%option
#% key: water
#% key_desc: string
#% type: string
#% description: Water (bit 7)
#% options: No, Yes
#% multiple: yes
#% required : no
#%end

#%option
#% key: cloud_confidence
#% key_desc: string
#% type: string
#% descriptions: No confidence level set, Low confidence, Medium confidence, High confidence
##% descriptions: No;No confidence level set;Low;Low confidence;Medium;Medium confidence;High;High confidence;
#% description: Cloud Confidence (bits 8-9)
#% options: No, Low, Medium, High
#% multiple: yes
#% required : no
#%end

#%option
#% key: cloud_shadow_confidence
#% key_desc: string
#% type: string
#% descriptions: No confidence level set, Low confidence, Reserved, High confidence
##% descriptions: No;No confidence level set;Low;Low confidence;Reserved;Reserved;High;High confidence;
#% description: Cloud Confidence (bits 10-11)
#% options: No, Low, Reserved, High
#% multiple: yes
#% required : no
#%end

#%option
#% key: snow_ice_confidence
#% key_desc: string
#% type: string
#% descriptions: No confidence level set, Low confidence, Medium confidence, High confidence
##% descriptions: No;No confidence level set;Low;Low confidence;Medium;Medium confidence;High;High confidence;
#% description: Unacceptable conditions for Snow/Ice Confidence (bits 12-13)
#% options: No, Low, Medium, High
#% multiple: yes
#% required : no
#%end

#%option
#% key: cirrus_confidence
#% key_desc: string
#% type: string
#% descriptions: No confidence level set, Low confidence, Medium confidence, High confidence
##% descriptions: No;No confidence level set;Low;Low confidence;Medium;Medium confidence;High;High confidence;
#% description: Unacceptable conditions for Cirrus Confidence (bits 14-15)
#% options: No, Low, Medium, High
#% multiple: yes
#% required : no
#%end

#%rules
#% required: fill,dilated_cloud,cirrus,cloud,cloud_shadow,snow,clear,water,cloud_confidence,cloud_shadow_confidence,snow_ice_confidence,cirrus_confidence
#%end

import os
import sys
import grass.script as grass

if "GISBASE" not in os.environ:
    print('You must be in GRASS GIS to run this program.')
    sys.exit(1)


"""
Collection 2 Level 1/2 Band Quality attributes
- https://www.usgs.gov/media/files/landsat-8-9-olitirs-level-1-data-format-control-book
- https://www.usgs.gov/media/files/landsat-8-collection-2-level-2-data-format-control-book

Bit     Flag Description
0       Fill
1       Dilated Cloud
2       Cirrus
3       Cloud
4       Cloud Shadow
5       Snow
6       Clear
7       Water
8-9     Cloud Confidence
10-11   Cloud Shadow Confidence
12-13   Snow/Ice Confidence
14-15   Cirrus Confidence
"""

# Binary start positions and length (single or double bits)
quality_binaries = {
        'fill': (0,1),
        'dilated_cloud': (1,1),
        'cirrus': (2,1),
        'cloud': (3,1),
        'cloud_shadow': (4,1),
        'snow': (5,1),
        'clear': (6,1),
        'water': (7,1),
        'cloud_confidence': (8,2),
        'cloud_shadow_confidence': (10,2),
        'snow_ice_confidence': (12,2),
        'cirrus_confidence': (14,2)
}

"""
For the single bits (1, 7):
    0 = "No" = This condition does not exist
    1 = "Yes" = This condition exists
"""
single_bits = {'No': '0',
               'Yes': '1'}

"""
For the single bits (1, 7):
    Image = Image data
    Fill = Fill data
"""
single_bit_fill = {
        'Image': '0',
        'Fill': '1'
        }

single_bit_dilated_cloud = {
        'Cloud not dilated or no cloud': '0',
        'Cloud dilation': '1'
        }

single_bit_cirrus = {
        'No or low confidence': '0',
        'High confidence': '1'
        }

single_bit_cloud = {
        'Not high confidence': '0',
        'High confidence': '1'
        }

single_bit_cloud_shadow = {
        'Not high confidence': '0',
        'High confidence': '1'
        }

single_bit_snow = {
        'Not high confidence': '0',
        'High confidence': '1'
        }

single_bit_clear = {
        'Cloud or dilated cloud': '0',
        'No cloud, no dilated cloud': '1'
        }

single_bit_water = {
        'Land or Cloud': '0',
        'Water': '1'
        }

"""
Double bits (8-9), read from left to right, represent levels of confidence that
a condition exists:

00 = "No confidence level set"
01 = "Low confidence"
10 = "Medium confidence"
11 = "High confidence"
"""

double_bits = {'No confidence': '00',
               'Low': '01',
               'Medium': '10',
               'High': '11'}


"""
Double bits (10-11, 12-13, 14-15), read from left to right, represent levels of
confidence that a condition exists:

00 = "No confidence level set"
01 = "Low confidence"
10 = "Reserved"
11 = "High confidence"
"""

double_bits_cloud_shadow_confidence = {'No confidence': '00',
               'Low': '01',
               'Reserved': '10',
               'High': '11'}

def main():

    invert = flags['i']
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

    # List for categories of unacceptable quality flags in the QA_PIXEL band
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

                    if condition == 'fill':
                        requested_bits = single_bit_fill[quality_level]

                    else:
                        requested_bits = single_bits[quality_level]

                else:

                    if condition == 'cloud_shadow_confidence':
                        requested_bits = double_bits_cloud_shadow_confidence[quality_level]

                    else:
                        requested_bits = double_bits[quality_level]

                # Collect requested quality bits for reclassification
                if not invert:
                    if requested_bits == quality_bits:
                        categories.append(str(category) + ' = NULL')
                        break
                else:
                    if requested_bits != quality_bits:
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
