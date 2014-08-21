#!/usr/bin/env python

"""PostScript file generation utilities."""

from collections import namedtuple
import sys

import tkFileDialog

try:
    import ROOT
    # Only operate ROOT in batch mode to avoid some crashes I experienced on
    # RCF when using the programme over ssh.
    #ROOT.gROOT.SetBatch(True)
    # May give to speed up on ROOT calls.
    ROOT.SetSignalPolicy(ROOT.kSignalFast)
except ImportError:
    print 'Unable to locate ROOT'

DETECTORS = range(1, 5)

# Describes uniform histogram binning in a single dimension.
Bins = namedtuple('Bins', 'n min max')

class BinsLarge:
    """Collection of binning for large-cell detectors."""
    volt = Bins(40, 0., 1600.)
    row = Bins(34, 0., 34.)
    column = Bins(17, 0., 17.)

class BinsSmall:
    """Collection of binning for small-cell detectors."""
    volt = Bins(32, 0., 256.)
    row = Bins(24, 0., 24.)
    column = Bins(12, 0., 12.)

BINS = {1: BinsLarge, 2: BinsLarge, 3: BinsSmall, 4: BinsSmall}

class BySubsystem:
    """Collection of histograms, one for each subsystem."""
    def __init__(self, generator, basename, title, fill, select):
        """Constructor.
        
        The generator is a function with the signature like map2d.
        
        """
        self.histograms = {i: generator(i, basename + str(i), title, fill)
                           for i in DETECTORS}
        # Apply selection cuts to each histogram.
        for n, h in self.histograms.iteritems():
            detector = 'detector=={}'.format(n)
            if select:
                selection = '({})*({})'.format(detector, select)
            else:
                selection = detector
            h.select = selection

    def project(self, tree):
        for h in self.histograms.itervalues():
            tree.Project(h.GetName(), h.fill, h.select)

    def draw(self, pad):
        pad.Clear()
        pad.Divide(2, 2)
        for n, h in sorted(self.histograms.iteritems()):
            pad.cd(n)
            h.Draw('colz')
            
def map2d(detector, name, title, fill):
    """2D map of detector channels (row x column)."""
    bins = BINS[detector]
    column = bins.column
    row = bins.row
    thistitle = '{} detector {}'.format(title, detector)
    histogram = ROOT.TH2D(name, thistitle, column.n, column.min, column.max,
        row.n, row.min, row.max)
    histogram.fill = fill
    return histogram

def generate(tree, name):
    """Generate PostScript output from a ROOT tree."""
    ROOT.gStyle.SetOptStat(False)
    # Suppress ROOT's TCanvas.Print() messages
    error_level = ROOT.gErrorIgnoreLevel
    ROOT.gErrorIgnoreLevel = ROOT.kError
    # Large cell voltage histograms.
    # Small cell voltage histograms.
    # 2D voltage maps.
    # 2D bitshift maps.
    # 2D gain maps.
    # 2D voltage change maps.
    # 2D bitshift change maps.
    # 2D gain change maps.
    canvas = ROOT.TCanvas('canvas', '', 1, 1, 800, 800)
    canvas.Print(name + '[')
    histograms = [
        BySubsystem(map2d, 'vmap', 'New voltage',
                    'row:column', 'newVoltage'),
        BySubsystem(map2d, 'gmap', 'New gain',
                    'row:column', 'newGain'),
        BySubsystem(map2d, 'bmap', 'New bitshift',
                    'row:column', 'newBitshift'),
        BySubsystem(map2d, 'vChangeMap', 'Voltage change',
                    'row:column', 'newVoltage-oldVoltage'),
        BySubsystem(map2d, 'gChangeMap', 'Gain change (new/old)',
                    'row:column', 'newGain/oldGain'),
        BySubsystem(map2d, 'bChangeMap', 'Bitshift change',
                    'row:column', 'newBitshift-oldBitshift')
    ]
    for i in histograms:
        i.project(tree)
        i.draw(canvas)
        canvas.Print(name)
    canvas.Print(name + ']')
    ROOT.gErrorIgnoreLevel = error_level # Restore original error message level

if __name__ == '__main__':
    filename = sys.argv[1]
    file = ROOT.TFile(filename, 'read')
    tree = file.Get('cells')
    generate(tree, 'test.ps')