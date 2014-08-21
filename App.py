#!/usr/bin/env python

"""Contains the main appliation for the fmsvoltages programme.

fmsvoltages is a Python programme using the Tk GUI toolkit
to provide a graphical interface for calculating new FMS
voltage and gain settings.

Total pieces of information needed:

Geometry:
- Detector/channel/row/column --> QT crate/board/slot/channel
Calibration:
- Detector/channel --> voltage, nominal gain
- QT crate/board/slot/channel --> QT pedestal/bitshift
- Detector/channel --> calibration curve p0/p1/p2
Output scripts:
- Large cells: detector/channel --> lecroy telnet/slot/channel
- Small cells: detector/channel --> device/chip/channel/address

"""

import copy
import os

from Tkinter import *
import tkMessageBox
import tkSimpleDialog
import tkFileDialog
import tkColorChooser

import maketree
from fms.detector import * # NORTH_LARGE etc
import dialog
from menus import Menus
from imagewindow import ImageWindow
import calibration
import qt
import files
import lecroytools
import smallcellscript
import postscript

class App(Tk):
    """Main fmsvoltages application class."""
    def __init__(self):
        """App constructor."""
        # Tk is an old-style class, can't use super() here.
        Tk.__init__(self)
        self.title("fmsvoltages")
        self.protocol("WM_TAKE_FOCUS", self.focus)
        self.protocol("WM_DELETE_WINDOW", self.exit)
        # Create our detector objects.
        # This is the main level of organising all the FMS data.
        self.detectors = {
            NORTH_LARGE: LargeDetector(NORTH_LARGE),
            SOUTH_LARGE: LargeDetector(SOUTH_LARGE),
            NORTH_SMALL: SmallDetector(NORTH_SMALL),
            SOUTH_SMALL: SmallDetector(SOUTH_SMALL)
        }
        # Create the graphics windows and menus.
        self.image_window = ImageWindow(self.detectors, self)
        self.menus = Menus(self)
        # Read library information.
        self.read_library()
        # We need to read input after creating the ImageWindow as we populate
        # the cells on the ImageWindow with the read parameters.
        self.read_input()

    def focus(self):
        """Sets focus on the main image window."""
        self.image_window.focus_set()

    def read_library(self):
        """Read library files.
        
        These contain geometrical and calibration information that
        isn't modified by the user.
        """
        # Create a new file set and populate it with all the library files.
        self.files = files.Files()
        try:
            openfile = self.files.open_file
            # Initialise miscellaneous cell info
            with openfile('INFO') as file:
                info = file.readlines()
                for detector in self.detectors.itervalues():
                    detector.set_info(info)
            # Open calibration information
            with openfile('CURVE_LARGE') as l, openfile('CURVE_SMALL') as s:
                    cal = calibration.Table(l, s)
                    for detector in self.detectors.itervalues():
                        detector.set_calibration(cal)
        except IOError as err:
            tkMessageBox.askyesno('I/O error', str(err))
            self.image_window.canvas.focus_set()

    def read_input(self):
        """Prompt the user for the input file directory.
        
        Read modifiable input files from that directory.
        See files.Files for list of files and their meanings.
        """
        try:
            path = tkFileDialog.askdirectory()
            if not path: # User the cancelled dialog box so bug out
                return False
            # Search the user-provided path for all the input files.
            foundall, missing = self.files.locate_input(path)
            # If any are missing show the user and error message
            # with the missing files listed.
            if not foundall:
                # Give indentation and numbered bullets to the missing names
                missing = [' {}) {}'.format(i, name)
                           for i, name in enumerate(sorted(missing), 1)]
                missing.insert(0, 'The following files were not found:')
                missing.append('Nothing was modified')
                tkMessageBox.showerror('Error', '\n'.join(missing))
                return False
            # Files were successfully located.
            # Read contents of gain/voltage files.
            # This must come first, as it also sets the row and column numbers.
            with self.files.open_file('GAIN_LARGE') as file:
                largegains = file.readlines()
                for x in NORTH_LARGE, SOUTH_LARGE:
                    self.detectors[x].set_voltages(largegains)
            with self.files.open_file('GAIN_SMALL') as file:
                smallgains = file.readlines()
                for x in NORTH_SMALL, SOUTH_SMALL:
                    self.detectors[x].set_voltages(smallgains)
            # Set QT information
            qtdirname = os.path.dirname(self.files['QT1'])
            self.qt = qt.System(qtdirname)
            for det in self.detectors.itervalues():
                det.set_qt(self.qt)
            # Now that the detector information is complete,
            # let's keep a copy of the initial detector state.
            # This is required for when we make a ROOT
            # tree with initial and final information.
            self.initial = copy.deepcopy(self.detectors)
        except IOError as err:
            tkMessageBox.askyesno('I/O error', str(err))
            self.image_window.canvas.focus_set()

    def apply_corrections_from_file(self):
        """Read gain corrections from a file and apply them."""
        with self.open_file() as file:
            lines = file.readlines()
        for detector in self.detectors.itervalues():
            nchanged = detector.apply_gain_corrections(lines)
            # Set a modified state if any channels were changed
            self.image_window.modified = nchanged > 0

    def save_root(self, filename=None):
        """Populate and write a ROOT file."""
        if not filename:
            filename = tkFileDialog.asksaveasfilename()
        if filename:
            maketree.populate(self.initial.itervalues(),
                              self.detectors.itervalues())
            maketree.write(filename)

    def save_postscript(self, filename=None):
        """Create a PostSript file."""
        if not filename:
            filename = tkFileDialog.asksaveasfilename()
        maketree.populate(self.initial.itervalues(),
                          self.detectors.itervalues())
        postscript.generate(maketree.tree(), filename)
        
    def save_all(self):
        """Save all files to an output directory
        
        Returns True if the programme is in a state where it can be allowed
        to quit, or False if it should not be allowed to quit.
        
        """
        outdir = tkFileDialog.askdirectory()
        # If they cancelled, there is no outdir set and we didn't save.
        # Return False to indicate "don't quit".
        if not outdir:
            return False
        # Get the full output file names
        fullpaths = [os.path.join(outdir, name)
                     for name in files.INPUT_NAMES.itervalues()]
        # See if any of those files already exist
        exists = [os.path.exists(x) for x in fullpaths]
        # If a file exists and the user says not to overwrite, return True
        # to indicate we can quit.
        # If they say yes, we overwrite everything - there's currently no
        # mechanism for selective overwriting.
        if True in exists and not tkMessageBox.askyesno('Files exist',
            'Do you wish to replace the existing files?'):
            return False
        # Write updated gain/voltage files for large cells
        filename = os.path.join(outdir, 'largeCellGains.txt')
        with open(filename, 'w') as file:
            self.detectors[NORTH_LARGE].write_gain_table(file)
        with open(filename, 'a') as file:
            self.detectors[SOUTH_LARGE].write_gain_table(file)
        # ... and for small cells
        filename = os.path.join(outdir, 'smallCellGains.txt')
        with open(filename, 'w') as file:
            self.detectors[NORTH_SMALL].write_gain_table(file)
        with open(filename, 'a') as file:
            self.detectors[SOUTH_SMALL].write_gain_table(file)
        self.qt.write(outdir)
        # Write the LeCroy scripts for large cells
        for i in [7005, 7006]:
            printer = lecroytools.Printer(i)
            printer.generate(self.detectors[NORTH_LARGE], outdir)
        for i in [7007, 7008]:
            printer = lecroytools.Printer(i)
            printer.generate(self.detectors[SOUTH_LARGE], outdir)
        # Write script for small cells
        smallcellscript.generate(self.detectors[NORTH_SMALL],
                                 self.detectors[SOUTH_SMALL],
                                 outdir)
        self.save_root(os.path.join(outdir, 'tree.root'))
        # Reset the modified flag so we don't prompt the user to save again
        self.image_window.modified = False
        # We saved, it's OK to quit now
        return True

    def exit(self):
        """Prompt user to confirm exit command."""
        can_quit = True
        if self.image_window.modified:
            if tkMessageBox.askyesno(title='Save changes?',
                    message='Do you wish to save changes before quitting?',
                    default='yes'):
                can_quit = self.save_all()
            # If they answered no, can_quit remains True
        if can_quit:
            self.quit()

    def open_file(self):
        """Prompt the user for a file to open."""
        try:
            filename = tkFileDialog.askopenfilename()
            file = open(filename)
            self.image_window.status.config(text='Opened: ' + filename)
            return file
        except:
            self.status.config(text='You fool!')
            tkMessageBox.showwarning("Open file",
                                     "Cannot open file " + filename)
            return None

    def set_window_colour(self, event):
        """Prompt the user to elect a new window colour."""
        rgb_triplet, rgb_string = tkColorChooser.askcolor()
        self.canvas.config(bg = rgb_string)


if __name__ == '__main__':
    try:
        # Initialise the application
        app = App()
        # Enter the main loop, opening the window.
        # We continue until the user quits/closes the window.
        app.mainloop()
    except IOError as err:
        tkMessageBox.showerror('I/O error', str(err))
    except Exception as err:
        tkMessageBox.showerror('Unknown derp', str(err))
