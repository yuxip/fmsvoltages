#!/usr/bin/env python

"""Compare the contents of two voltage-gain files."""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys

def detector(line):
    return int(line[0])

def voltage(line):
    if detector(line) < 3:
        base = 10
    else:
        base = 16
    return int(line.split()[4], base)

def gain(line):
    return float(line.split()[5])

def parse():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('file1')
    parser.add_argument('file2')
    parser.add_argument('--deltav', type=int, default=0,
        help='minimum difference in voltage')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse()
    with open(args.file1) as file:
        lines1 = file.read().splitlines()
    with open(args.file2) as file:
        lines2 = file.read().splitlines()
    if len(lines1) != len(lines2):
        print 'different numbers of lines'
        quit()
    for line1, line2 in zip(lines1, lines2):
        differ = False
        if abs(voltage(line1) - voltage(line2)) > args.deltav:
            print 'different voltages:'
            differ = True
        if gain(line1) != gain(line2):
            print 'different gains:'
            differ = True
        if differ: print line1, 'vs.', line2
