#!/usr/bin/env python

"""Converts Steve's format for gains corrections to one based on row and
column number.

Steve uses these 4 columns:
 eastOrWest detector channel correction
whereas I use these 4:
 detector row column correction.

The first argument should be the input file from Steve.
"""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys

def process(line):
    """Process a single line from an input file.
    
    Line format is:
        side detector channel gain
    side is east or west and detector is 1 or 2 for large, 3 or 4 for small.
    
    Returns (detector, channel), correction
    """
    side, detector, channel, correction = line.split()
    return (int(detector), int(channel)), float(correction)

if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('infile', help='correction file in Steve\'s format')
    parser.add_argument('outfile', help='correction file in row/column format')
    args = parser.parse_args()
    with open(args.infile) as file:
        # Remove lines with 1 at the start, as those are for the FPD
        input = [line for line in file.read().splitlines()
                 if not line.startswith('1')]
    # Accumulate gains for all large and small channels.
    # Key by (detector, channel number).
    channels = dict(process(line) for line in input)
    # There are 17 columns per row for large detectors and
    # 12 columns per row for small detectors.
    nColumns = {1: 17, 2: 17, 3: 12, 4: 12}
    outFile = open(args.outfile, 'w')
    for (detector, channel), correction in sorted(channels.iteritems()):
        # Channel is in range [1, N] and column in range [0, n).
        column = (channel - 1) % nColumns[detector]
        row = (channel - 1) / nColumns[detector]
        string = "{} {} {} {}\n".format(detector, row, column, str(correction))
        outFile.write(string)
    outFile.close()