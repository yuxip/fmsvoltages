#!/usr/bin/env python

"""Script to combine voltages from one file with gains from another.

Read in two voltage/gain files (smallCellGains.txt or largeCellGains.txt)
and print out a new file with the voltages from the first file and the
gains from the second.
Useful if you want to redefine what the expected gain is for all the
cells, while maintaining the current voltages.
"""

import argparse
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('volt', help='file from which to take voltages')
    parser.add_argument('gain', help='file from which to take gains')
    parser.add_argument('--out', default='newgains.txt',
        help='output file name')
    args = parser.parse_args()
    print 'Reading voltages from', args.volt
    print 'Reading gains    from', args.gain
    print 'Writing to           ', args.out
    with open(args.volt) as file:
        volts = file.read().splitlines()
    with open(args.gain) as file:
        gains = file.read().splitlines()
    with open(args.out, 'w') as file:
        for i, j in zip(volts, gains):
            # line format is e.g. 1  1  0  0  -1461 3.30161
            # detector channel row column voltage gain
            v = i.split()
            g = j.split()
            out = "{} {} {} {} {} {}\n".format(
                v[0], v[1], v[2], v[3], v[4], g[5]) 
            file.write(out)
