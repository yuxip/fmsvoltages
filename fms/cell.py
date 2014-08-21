"""
This module provides classes describing FMS cells.
There is a base class (Base) and
two inheriting classes, Large and Small.
"""

from decimal import Decimal as Decimal
import math

import calibration
import fms.geometry
import lecroytools
import qt

## FMS cell base class.
#  Stores all information relating to a single cell.
#  Stores cell position (row, column),
#  IDs (channel, QT channel, QT board)
#  and geometry (width, height).
#  Because the required information is strewn across several files,
#  there are various set_...() methods to set portions of the attributes.
#
#  In summary:
#   1 detector, channel, row, column, gain, voltage -
#     from small/largeCellGains.txt
#     this should be set first to set the detector & channel, by which
#     the cells are subsequently uniquely identified.
#   2 qt crate, board, channel, id1-4 (meanings differ for small and large) -
#     from fmsCellInfoTable.txt
#   3 qt bitshift and pedestal -
#     from qt1/2/3/4_tac.dat
#   4 gain calibration curve parameters -
#     from small/large_gaincurve_par.txt
#
#  The order in which these are set should follow the above order, as each
#  stage generally provides information necessary for the next stage to
#  identify the correct cell. e.g. the qt bitshift/pedestal file (3) does
#  not store row and column numbers, only qt crate, board and channel,
#  therefore (2) is needed to set the crate/board/channel for each cell
#  before the bitshifts/pedestals can be set.
class Base(object):
    """FMS cell base class.
    
    Stores all information relating to a single cell.
    Because the required information is strewn across several files,
    there are various set_...() methods to set portions of the attributes.
    In summary:
     1 detector, channel, row, column, gain, voltage -
       from small/largeCellGains.txt
       this should be set first to set the detector & channel, by which
       the cells are subsequently uniquely identified.
     2 qt crate, board, channel, other IDs (differ for small and large) -
       from fmsCellInfoTable.txt
     3 qt bitshift and pedestal -
       from qt1/2/3/4_tac.dat
     4 gain calibration curve parameters -
       from small/large_gaincurve_par.txt
       
    The order in which these are set should follow the above order, as each
    stage generally provides information necessary for the next stage to
    identify the correct cell. e.g. the qt bitshift/pedestal file (3) does
    not store row and column numbers, only qt crate, board and channel,
    therefore (2) is needed to set the crate/board/channel for each cell
    before the bitshifts/pedestals can be set.
    """
    # Geometry information for this cell type
    geometry = None

    def __init__(self, row=-1, col=-1):
        """Constructor.
        
        Optionally initialise with row and column numbers.
        
        """
        # Don't initialise anything to None by default or it will interfere
        # with creating a Dialog if the user doesn't open a file.
        # Geometrical information
        self.detector, self.channel = -1, -1
        self.row, self.column = row, col
        # Voltage (integer), gain (float) information
        self.voltage, self.gain = 0, 0.
        # QT system information
        self.qt = qt.Channel()
        # Gain calibration curve information
        self.calibration = calibration.Channel()

    def set_from_string(self, str):
        """Set values from a string.
        
        The string format is 'detector channel row column voltage gain'.
        All these attributes are set; others remain unchanged.
        
        """
        values = str.split()
        if len(values) != 6:
            print 'Format of argument to Cell.set_from_string is incorrect'
            return

        self.detector = int(values[0])
        self.channel = int(values[1])
        self.row = int(values[2])
        self.column = int(values[3])
        
        # Large cell voltages are stored as decimal values.
        # Small cell voltages are stored as hexadecimal values.
        # Large = detectors 1, 2. Small = detectors 3, 4.
        base = 10
        if self.detector == 3 or self.detector == 4:
            base = 16
        self.voltage = abs(int(values[4], base))
        
        self.gain = float(values[5])


    ## Returns an appropriately formatted string representation of a voltage.
    #  @param [in] input The voltage, an integer
    @classmethod
    def voltage_int_to_str(cls, input):
        """Returns a string with appropriately formatted voltage value."""
        return str(input)


    ## Returns an integer from an appropriately formatted voltage string.
    #  @param [in] input The voltage, a string
    @classmethod
    def voltage_str_to_int(cls, input):
        """Returns an integer from an appropriately formatted voltage string.
        """
        return int(input)


    ## Returns a string suitable for writing to a gain file.
    #  See set_from_string() for the format of the returned string.
    def get_gain_file_string(self):
        """Returns a string suitable for writing to a gain file.
        
        See set_from_string() for the format of the returned string."""

        # Large cell voltages should be given as decimal values.
        # Small cell voltages should be given as hexadecimal values.
        # Large = detectors 1, 2. Small = detectors 3, 4.

        # Force the gain to have exactly five decimal places:
        fivedp = Decimal(10) ** -5 # Equivalent to Decimal('0.00001')
        gain = Decimal(str(self.gain)).quantize(fivedp)
        
        return \
            str(self.detector) + ' ' + \
            str(self.channel) + ' ' + \
            str(self.row) + ' ' + \
            str(self.column) + ' ' + \
            self.voltage_int_to_str(self.voltage) + ' ' + \
            str(gain)


    ##########################################################################
    def speak(self):
        """Print the Cell contents to the screen.
        
        Only the values set via set_from_string() printed.
        """

        print self.get_gain_file_string()


    ##########################################################################
    def set_info(self, cell):
        """Set miscellaneous information from fmsCellInfoTable.
        
        cell should be a cellinfo.Cell object.
        """
        
        self.qt.set_info(cell)

    @classmethod
    def min_voltage(cls, bitshift=0):
        """Returns the minimum voltage to which the cell should be set.
        
        This can in principle depend on the cell's bitshift, hence the
        argument.
        """
        pass

    @classmethod
    def max_voltage(cls, bitshift=0):
        """Returns the maximum voltage for the parameterisation curve.
        """
        pass

    @classmethod
    def is_valid_voltage(cls, voltage, shift=0):
        """Returns the maximum voltage for the parameterisation curve.
        
        Will return False for a voltage of None.
        """
        return cls.min_voltage(shift) <= voltage <= cls.max_voltage(shift)

    def compute_gain(self, voltage=None, bitshift=None):
        """Returns the gain of this cell at the requested voltage and bitshift.
        
        Does not modify the gain stored the Cell itself.
        This is the effective gain, once both the voltage and bitshift
        are accounted for.
        If the bitshift argument is None, the current bitshift of the cell
        is used.
        If the voltage argument is None, the current voltage is used.
        """
        gain = self.gain
        # Evaluate ADC at the current and requested voltages so we can find
        # the relative change in ADC (and hence gain) due to voltage change.
        if voltage:
            function = self.calibration.get_function()
            oldadc = function.Eval(self.voltage)
            newadc = function.Eval(voltage)
            gain *= newadc / oldadc
        # If the bitshift changes, apply another factor of 2^change
        if bitshift is not None:
            gain *= math.pow(2., bitshift - self.qt.bitshift)
        return gain

    def pseudorapidity(self):
        return self.geometry.pseudorapidity(self.row, self.column)


##############################################################################
#
# Small FMS cell
#
##############################################################################
class Small(Base):


    geometry = fms.geometry.Small


    ##########################################################################
    def __init__(self, row = -1, col = -1):

        # Call the base class constructor
        super(Small, self).__init__(row, col)
        
        # Compute the channel number, assuming row and column
        # are both valid.
        if self.row < 0 or \
           self.column < 0 or \
           self.row >= self.geometry.nrows() or \
           self.column >= self.geometry.ncolumns():
            self.channel = -1
        else:
            self.channel = row * self.geometry.ncolumns() + col + 1

        self.device = -1
        self.chip = -1
        self.chan = -1
        self.address = -1


    ##########################################################################
    def set_info(self, cell):
        """Set miscellaneous information from fmsCellInfoTable.
        
        cell should be a cellinfo.Cell object.
        """
        
        super(Small, self).set_info(cell)
        
        # Protect against accidentally using large cell input
        if cell.id1 >= 7005:
            return
        
        # Note offset of 1 between device number in input table and the
        # values required for output, which we correct here.
        self.device = cell.id1 - 1
        self.chip = cell.id2
        self.chan = cell.id3
        self.address = cell.id4


    ##########################################################################
    @classmethod
    def voltage_int_to_str(cls, input):
        """Returns a string with appropriately formatted voltage value.
        
        Small cell voltages are always printed as hexadecimal values,
        without a leading '0x', and letters in upper case.
        e.g. E2 not 0xE2 or 0xe2 or e2.
        """
        
        return hex(input).replace('0x', '', 2).upper()


    ##########################################################################
    @classmethod
    def voltage_str_to_int(cls, input):
        """Returns an integer from an appropriately formatted voltage string.
        """
        return int(input, 16)


    ##########################################################################
    @classmethod
    def width(cls):
        """Returns the cell width in cm
        """
        return 3.822


    ##########################################################################
    @classmethod
    def height(cls):
        """Returns the cell height in cm."""
        return 3.875
    
    ##########################################################################
    @classmethod
    def min_voltage(self, bitshift = 0):
        """Returns the minimum voltage for the parameterisation curve."""
        return 0

    ##########################################################################
    @classmethod
    def max_voltage(self, bitshift = 0):
        """Returns the maximum voltage for the parameterisation curve."""
        return 0xFF

##############################################################################
#
# Large FMS cell
# Add LeCroy information (telnet number, slot and channel).
# Telnet numbers are 7005-7008, slot and channel in the range [0, 15].
#
##############################################################################
class Large(Base):


    geometry = fms.geometry.Large


    ##########################################################################
    def __init__(self, row = -1, col = -1):

        # Call the base class constructor
        super(Large, self).__init__(row, col)

        # Compute the channel number, assuming row and column
        # are both valid.
        if self.row < 0 or \
           self.column < 0 or \
           self.row >= self.geometry.nrows() or \
           self.column >= self.geometry.ncolumns():
            self.channel = -1
        else:
            self.channel = row * self.geometry.ncolumns() + col + 1

        self.lecroy = lecroytools.Channel()


    ##########################################################################
    def set_info(self, cell):
        """Set miscellaneous information from fmsCellInfoTable.
        
        cell should be a cellinfo.Cell object.
        """
        
        super(Large, self).set_info(cell)
        
        # Protect against accidentally using small cell input
        if cell.id1 < 7005:
            return
        
        self.lecroy = lecroytools.Channel()
        self.lecroy.telnet = cell.id1
        self.lecroy.slot = cell.id3
        self.lecroy.channel = cell.id4

    ##########################################################################
    def get_gain_file_string(self):
        """Returns a string suitable for writing to a gain file.
        
        The values set via set_from_string() are printed.
        """

        # Large cell voltages should be given as decimal values.
        # Small cell voltages should be given as hexadecimal values.
        # Large = detectors 1, 2. Small = detectors 3, 4.

        # With the current format, we read and write gains without the
        # factors of 2 from bitshift
        gain = self.gain
        
        # Force the gain to have exactly five decimal places:
        fivedp = Decimal(10) ** -5 # Equivalent to Decimal('0.00001')
        gain = Decimal(str(gain)).quantize(fivedp)
        
        return \
            str(self.detector) + ' ' + \
            str(self.channel) + ' ' + \
            str(self.row) + ' ' + \
            str(self.column) + ' ' + \
            str(-self.voltage) + ' ' + \
            str(gain)


    ##########################################################################
    @classmethod
    def width(cls):
        """Returns the cell width in cm
        """
        return 5.812


    ##########################################################################
    @classmethod
    def height(cls):
        """Returns the cell height in cm
        """
        return 5.812
    
    
    ##########################################################################
    @classmethod
    def min_voltage(self, bitshift = 0):
        """Returns the minimum voltage for the parameterisation curve.
        """
        return 0


    ##########################################################################
    @classmethod
    def max_voltage(self, bitshift = 0):
        """Returns the maximum voltage for the parameterisation curve.
        """
        if bitshift > 1:
            return 1500
        return 1600
