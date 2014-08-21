#\todo split into separate files?

import math
import copy

import calibration
from fms.cell import Base, Small, Large
import cellinfo
import fms.geometry as fmsgeom # Want to call the Cell attribute geometry

NORTH_LARGE = 1
SOUTH_LARGE = 2
NORTH_SMALL = 3
SOUTH_SMALL = 4

class Detector(object):
    """Base class for detector systems.
    
    Organises populating and modifying cells, setting their attributes from
    the many different input sources, and writing the necessary output in
    the required formats.
    """
    def __init__(self, number):
        """Constructor."""
        # The detector ID number
        self.number = number
        # The array contains a list-of-lists of cells, so a specific
        # cell can be looked up via array[row][column].
        # Cells that don't exist due to holes in the
        # detector store None in that entry instead of a cell.
        # The array is filled in the constructors of the inheriting classes.
        self.array = []
        # This list contains all the cells, placed in a single list for
        # ease of iteration.
        # Non-existent cells (i.e. those with None in self.array)
        # do not appear here. Aside from that, the contents are the same
        # as the array.
        self.cells = []
        
    def set_voltages(self, lines):
        """Set all channel voltages and gains from a list of strings.
        
        See Cell.set_from_string() for the required format.
        """
        for line in lines:
            # Check the detector number of the input and skip it
            # if it doesn't match this detector's number.
            tmpcell = Base()
            tmpcell.set_from_string(line)
            # Entries for both sub-detectors are typically stored in
            # the same file, so skip entries for the wrong sub-detector.
            if tmpcell.detector != self.number:
                continue
            found = self.get_cell(tmpcell.row, tmpcell.column)
            if found is not None:
                found.set_from_string(line)

    def set_info(self, lines):
        """Read and set miscellaneous cell info for all cells.
        
        set_voltages() must be called before this method in order to
        set the detector, channel, row and column attributes.
        """
        if len(self.cells) == 0:
            return
        for line in lines:
            info = cellinfo.Cell(line)
            if info.detector != self.number:
                continue
            cell = self.get_cell(info.row, info.column)
            if cell == None:
                continue
            cell.set_info(info)

    def set_qt(self, qtinfo):
        """Sets QT information for all cells.
        
        qtinfo should be an object of type qt.System().
        set_info() must be called first to set the QT crate,
        board and channel of each cell.
        Note that the Detector references the qt.Channel objects in the
        qt.System - it does not copy them. Therefore any changes made to
        the QT information in either Detector or qt.System update both.
        """
        # Loop over the detector cells and look for the matching
        # QT channel entry.
        # If found, use the QT entry to set bitshift and pedestal.
        for cell in self.cells:        
            qt = qtinfo.get_channel(cell.qt)
            if qt:
                cell.qt = qt
                #cell.qt.bitshift = qt.bitshift
                #cell.qt.pedestal = qt.pedestal


    ##########################################################################
    def set_calibration(self, calib):
        """Set the calibration curve for each cell.
        
        The input calib should be an object of type calibration.Table()."""

        for cell in self.cells:
            c = calib.find_cell(cell)
            if c != None:
                cell.calibration = c


    ##########################################################################
    def write_gain_table(self, file):
        """Write the detector contents in the format used for gain files.
        
        This involves writing the result of get_gain_file_string() for
        each cell. The second argument can be 'write' to write the contents
        to a new file or 'append' to append to an existing file.
        """
        # Need to deal with failure to open the file
        for c in self.cells:
            file.write(c.get_gain_file_string() + '\n')


    ##########################################################################
    # Returns a reference to the requested cell if it exists.
    # If not, returns None.
    def get_cell(self, row, column):
        """Return the cell at (row, column), or None if there is no cell"""
        if len(self.array) == 0:
            return None
        try:
            return self.array[row][column]
        except IndexError:
            return None


    ##########################################################################
    def cell_exists(self, row, column):
        """Returns true if there is a cell at (row, column), false if not"""
        return self.get_cell(row, column) != None


    ##########################################################################
    def speak(self):
        """Print information about all cells to standard output"""
        print len(self.cells)
        for c in self.cells:
            c.speak()


    ##########################################################################
    def apply_gain_corrections(self, file):
        """Compute new voltages from a list of gain modification factors.
        
        The input file should contain lines with the following format:
        detector row column change
        where 'change' is a factor by which to multiply the gain.
        The voltage of each cell is changed so as to change the gain by
        this factor, using the calibration curve for that cell to
        compute the required voltage change.
        Returns the number of modified cells.
        
        Adds another field to the cell, 'requested_correction' which stores
        the gain factor asked for (not necessarily delivered).
        """
        
        modified = 0 # Count the number of cells that change
        # Object performing gain/voltage change calculations
        for line in file:
            # Split the line up into its constituent parts, namely
            # detector, row, column and correction
            values = line.split()
            detector = int(values[0])
            if detector != self.number:
                continue
            correction = float(values[3])
            if correction == 1.:
                continue
            row = int(values[1])
            column = int(values[2])
            if not self.cell_exists(row, column):
                continue
            cell = self.get_cell(row, column)
            cell.requested_correction = correction
            newgain = cell.gain * correction
            v, s, g = calibration.optimise(cell, newgain)
            if newgain is None or v is None or s is None:
                continue
            cell.voltage = v
            cell.gain = g
            cell.qt.bitshift = s
            modified += 1

        return modified


##############################################################################
#
# A small-cell detector
#
##############################################################################
class SmallDetector(Detector):


    geometry = fmsgeom.Small
    celltype = Small


    ##########################################################################
    # Constructor
    def __init__(self, number):
        
        super(SmallDetector, self).__init__(number)

        # Populate the Cell list
        for row in range(0, self.geometry.nrows()):
            # Fill a list of cells for all columns in this row
            li = []
            for column in range(0, self.geometry.ncolumns()):
                # Skip the hole around the beam pipe
                if row > 6 and row < 17 and column < 5:
                    li.append(None)
                else:
                    thecell = Small(row, column)
                    thecell.detector = self.number
                    li.append(thecell)
                    self.cells.append(thecell)
            # Add the columns for this row
            self.array.append(li)


##############################################################################
#
# A large-cell detector
#
##############################################################################
class LargeDetector(Detector):


    geometry = fmsgeom.Large


    ##########################################################################
    # Constructor
    def __init__(self, number):

        super(LargeDetector, self).__init__(number)

        # Populate the Cell list
        for row in range(0, self.geometry.nrows()):
            li = []
            for column in range(0, self.geometry.ncolumns()):
                # Skip the hole around the beam pipe
                absent = False
                if row > 8 and row < 25 and column < 8:
                    absent = True
                # This is a bit funny-looking, but it just skips
                # the cells at the corners
                altrow = row
                if row < 16:
                    altrow = self.geometry.nrows() - 1 - row
                if column + altrow > 42:
                    absent = True
                # Add the cell if it exists
                if absent:
                    li.append(None)
                else:
                    thecell = Large(row, column)
                    thecell.detector = self.number
                    li.append(thecell)
                    self.cells.append(thecell)
            # Add the columns for this row
            self.array.append(li)


    ##########################################################################
    # For testing.
    # Returns the number of cells in this detector.
    def get_size(self, switch=False):
        size = 0

        if switch == False:
            for row in self.array:
                size += len(row)
        else:
            for row in range(0, self.geometry.nrows()):
                for col in range(0, self.geometry.ncolumns()):
                    if self.cell_exists(row, col):
                        size += 1
        return size
