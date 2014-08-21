#!/usr/bin/env python

"""Produce an fmsMap text file for the database from fmsvoltages info table."""

from argparse import ArgumentParser

def parse():
    """Parse and return command line arguments."""
    parser = ArgumentParser()
    parser.add_argument('input', help='name of fmsvoltages info table',
        default='fmsCellInfoTable.txt')
    parser.add_argument('output', help='name of output fmsMap table',
        default='fmsMap.txt')
    return parser.parse_args()

def process_info(line):
    """Parse a single line of info table input.

    Input format is:
     detector cell row column qtcrate qtslot qtdaughtercard qtdaughterchannel\\
     id1 id2 id3 id4
    Returns (detector, channel), (qtcrate, qtslot, qtchannel)
    where qtchannel = 8 * qtdaughtercard + qtdaughterchan.
    """
    words = line.split()
    # Check for invalid qtcrate
    if words[4] == '0':
        return None
    #indices = [0, 1, 4, 5, 6, 7]
    qtslot = words[5]
    #if '12' == qtslot:
    #    qtslot = '11'
    #detector, cell, qtcrate, qtslot, qtdaughtercard, qtdaughterchannel =\
    #    [int(words[i]) for i in indices]
    qtdaughtercard, qtdaughterchannel = int(words[6]), int(words[7])
    qtchannel = 8 * qtdaughtercard + qtdaughterchannel
    #return (detector, cell), (qtcrate, qtslot, qtchannel)
    # Adjust for different detector number conventions.
    # Cell info table uses [1, 4], QT map uses [8, 11].
    detector = int(words[0]) + 7
    return ' '.join([str(detector), words[1], words[4], qtslot, str(qtchannel)])

if __name__ == '__main__':
    args = parse()
    print args.input, args.output
    with open(args.input) as file:
        lines = file.read().splitlines()
    info = [process_info(line) for line in lines]
    info = [i for i in info if i is not None]
    with open(args.output, 'w') as file:
        for i in info:
            file.write(i + '\n')
