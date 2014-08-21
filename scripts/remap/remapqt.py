#!/usr/bin/env python

from argparse import ArgumentParser
from collections import namedtuple
import os

QtChannel = namedtuple('QtChannel', 'slot channel')
QtInfo = namedtuple('QtInfo', 'pedestal bitshift')

class QtCrate:
    """All the channels and pedestals/bitshift in a single QT crate."""
    def __init__(self, filename=''):
        def parse(string):
            """Parse a string containing 'slot channel pedestal bitshift.'
            
            Return (slot, channel), (pedestal, bitshift)
            """
            values = [int(i) for i in string.split()]
            return (QtChannel(*values[:2]), QtInfo(*values[2:]))
        if filename:
            with open(filename) as file:
                self.channels = dict(parse(line)
                                     for line in file.read().splitlines())
    @classmethod
    def from_detector(cls, detector, crate):
        """Create from a Detector object."""
        cells = [i for i in detector.cells.itervalues() if i.qtcrate == crate]
        qt = cls()
        # Populate with all channels required by the qt_tac.dat file as the input
        # detector won't contain entries for every QT channel.
        qt.channels = {QtChannel(slot, channel): QtInfo(-1, 0)
                       for slot in range(11) for channel in range(32)}
        for cell in cells:
            qt.channels[cell.qtchannel] = cell.qtinfo
        return qt
    def write(self, filename):
        with open(filename, 'w') as file:
            for channel, info in sorted(self.channels.iteritems()):
                # Note the explicit inclusion of the sign for positive bit-shift.
                # Have to treat 0 separately to avoid "+0".
                if 0 == info.bitshift:
                    layout = '{} {:>2} {} {:>2}\n'
                else:
                    layout = '{} {:>2} {} {:>+2}\n'
                string = layout.format(channel.slot, channel.channel,
                                       info.pedestal, info.bitshift)
                file.write(string)

class QtSystem:
    """A collection of QT crates."""
    def __init__(self, directory='.'):
        """Populate from a series of text files."""
        def filename(number):
            return os.path.join(directory, 'qt{}_tac.dat'.format(number))
        if directory:
            self.crates = {i: QtCrate(filename(i)) for i in range(1, 5)}
    @classmethod
    def from_detector(cls, detector):
        """Create from a Detector object."""
        system = cls('')
        system.crates = {i: QtCrate.from_detector(detector, i) for i in range(1, 5)}
        return system
    def write(self, directory):
        for i, crate in self.crates.iteritems():
            crate.write(os.path.join(directory, 'qt{}_tac.dat'.format(i)))

class Cell:
    """Detector-to-QT information for a single cell."""
    def __init__(self, string, qt=None):
        """Constructor.

        string should have this format:
            detector channel qtcrate qtslot qtchannel.
        If qt is a QtSystem attempt to set the channel's QT pedestal and
        bitshift.
        """
        values = string.split()
        # 2-tuple for (detector, channel)
        self.channel = int(values[0]), int(values[1])
        self.qtcrate = int(values[2])
        # 2-tuple for QT (slot, channel)
        # Need to adjust slot number as input here is [1, 11] but QT files
        # are [0, 10].
        qtslot = int(values[3]) - 1
        self.qtchannel = QtChannel(slot=qtslot, channel=int(values[4]))
        # Set default QT pedestal and bitshift.
        self.qtinfo = QtInfo(pedestal=-1, bitshift=-999)
        # Set true QT pedestal and bitshift if QT information is provided.
        if isinstance(qt, QtSystem):
            self.qtinfo = qt.crates[self.qtcrate].channels[self.qtchannel]

class Detector:
    """A collection of cells."""
    def __init__(self, filename, qt=None):
        def channel(line):
            "Returns (detector, channel)."""
            return tuple(int(i) for i in line.split()[:2])
        with open(filename) as file:
            self.cells = {channel(line): Cell(line, qt)
                          for line in file.read().splitlines()}

def parse():
    parser = ArgumentParser()
    parser.add_argument('map1', help='old channel-to-QT mapping')
    parser.add_argument('map2', help='new channel-to-QT mapping')
    parser.add_argument('qtdir',
        help='directory containing old qt#_tac.dat files')
    parser.add_argument('newdir',
        help='output directory for new qt#_tac.dat files')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse()
    # Original QT pedestals and bitshifts.
    # These stay the same for each channel.
    oldqt = QtSystem(args.qtdir)
    # Detector/channel and QT slot/channel (+pedestal/bitshift) under the old
    # detector-to-QT mapping.
    oldmap = Detector(args.map1, oldqt)
    # Read the new mapping. Don't include QT information (pedestal/bitshift)
    # as we will get this from the old map.
    newmap = Detector(args.map2)
    # Update each cell with the new QT mapping.
    for cell in oldmap.cells.itervalues():
        cell.qtchannel = newmap.cells[cell.channel].qtchannel
    # Write the pedestal/bitshifts under the new mapping.
    newqt = QtSystem.from_detector(oldmap)
    newqt.write(args.newdir)
