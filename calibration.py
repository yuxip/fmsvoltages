"""Classes describing gain calibration curves."""

import math # For isnan, isinfo, floor...

# I encountered the WEIRDEST bug importing from ROOT.
# The programme worked fine on my Mac, and generally fine on a remote Linux
# computer, to which I ssh'd. However, if I used Cmd-tab to move away from
# the X11 window displaying the programme from the remove machine, when I
# returned the window was completely unresponsive.
# After much head-scratching, I found this was remedied by replacing all
#   from ROOT import <something>
# with just
#   import ROOT
# No idea why it should interfere with X11, but it does, at least for me.
import ROOT
# Only operate ROOT in batch mode to avoid some crashes I experienced on
# RCF when using the programme over ssh.
ROOT.gROOT.SetBatch(True)
# May give to speed up on ROOT calls.
ROOT.SetSignalPolicy(ROOT.kSignalFast)

import qt

class Channel(object):
    """Base class for gain calibration curves.
    
    The calibration curve describes the ADC vs. voltage behaviour of
    a single channel.
    
    """
    def __init__(self, string=''):
        """Constructor.
        
        The ADC vs. voltage calibration curve is defined via three parameters,
        p0, p1 and p2, where the ADC is given by ADC = exp(p0 + p1*V * p2*V^2)
        where V is the (magnitude of) voltage.
        If the string is not empty, attempt to set all attributes from it.
        See set() for the string format.
        
        """
        # Channel location
        self.detector, self.row, self.column = -1, -1, -1
        # Calibration curve parameters.
        self.p = 3 * [0.]
        if string:
            self.set(string)
        self.function = None

    def set(self, string):
        """Sets all attributes via a string.
        
        The input format should be 'detector row column p0 p1 p2'.
        Returns true if the values can be set from the string, False if not.
        
        """
        values = string.split()
        try:
            # Set channel location from the first three elements
            self.detector, self.row, self.column = [int(i) for i in values[:3]]
            # Set calibration curve parameters from the last three elements
            self.p = [float(i) for i in values[3:6]]
            self.function = None
            return True
        except IndexError:
            print 'calibration.Channel passed improperly formatted string:'
            print string

    @classmethod
    def min_voltage(cls, bitshift=0):
        """Returns the minimum voltage for the parameterisation curve."""
        return

    @classmethod
    def max_voltage(cls, bitshift=0):
        """Returns the maximum voltage for the parameterisation curve."""
        return

    def get_function(self):
        """Returns the function object, creating it if it is not yet present.
        
        Uses lazy initialisation.
        If you need to access the function directly do it via this method.
        
        """
        if not self.function:
            self.function = ROOT.TF1('', 'exp([0]+[1]*x+[2]*x*x)',
                                     float(self.min_voltage()),
                                     float(self.max_voltage()))
            self.function.SetParameters(*self.p)
        return self.function

    def get_adc(self, voltage):
        """Evaluates the ADC value at the input voltage.
        
        Returns None if the input voltage cannot be evaluated for some reason.
        
        """
        # Large cells store negative voltage values, but the calibration
        # curves are always stored in terms of positive voltages.
        voltage = abs(voltage)
        adc = self.get_function().Eval(voltage)
        # Check for error values
        if adc < 0. or math.isnan(adc) or math.isinf(adc):
            adc = None
        return adc

    def get_voltage_for_adc(self, adc):
        """Returns the voltage required to obtain the requested ADC value.
        
        This is based on extrapolation from the current voltage and ADC
        using the calibration curve for this cell.
        If the voltage is outside the valid range for the cell, or if the
        ADC cannot be evaluated for some reason, returns None.
        Otherwise returns the ADC value as an integer.
        
        """
        # Find the minimum and maximum ADCs achievable by the cell
        minadc = self.get_adc(self.min_voltage())
        maxadc = self.get_adc(self.max_voltage())
        if not minadc < adc < maxadc:
            return None
        v = self.get_function().GetX(adc)
        if math.isnan(v) or math.isinf(v):
            return None
        # GetX() returns a float, so round to the nearest integer value
        return int(round(v))


class ChannelSmall(Channel):
    """Calibration information for small cells.
    
    Implements min_voltage() and max_voltage() from Channel.
    
    """
    @classmethod
    def min_voltage(cls, bitshift=0):
        """Returns the minimum voltage for the parameterisation curve."""
        return 0

    @classmethod
    def max_voltage(cls, bitshift=0):
        """Returns the maximum voltage for the parameterisation curve."""
        return 0xFF


class ChannelLarge(Channel):
    """Calibration information for large cells.
    
    Implements min_voltage() and max_voltage() from Channel.
    
    """
    @classmethod
    def min_voltage(cls, bitshift=0):
        """Returns the minimum voltage for the parameterisation curve."""
        return 0

    @classmethod
    def max_voltage(cls, bitshift=0):
        """Returns the maximum voltage for the parameterisation curve."""
        return 1600


class Table:
    """Collection of calibration curves.
    
    Stores all calibration curves, for both large and small cells,
    and provides lookup.
    
    """
    def __init__(self, large_file=None, small_file=None):
        """Constructor.
        
        Parameters for small and large cell calibration curves are stored
        in separate files, but it is more convenient to store them in
        memory in a single table.
        
        """
        # Dictionary of calibration curves keyed by (detector, row, column)
        self.entries = {}
        if large_file:
            entries = [ChannelLarge(line) for line in large_file.readlines()]
            self.entries.update({(e.detector, e.row, e.column): e
                                for e in entries})
        if small_file:
            entries = [ChannelSmall(line) for line in small_file.readlines()]
            self.entries.update({(e.detector, e.row, e.column): e
                                for e in entries})
        
    def find(self, detector, row, column):
        """Returns the calibration curve for a detector channel.
        
        Returns None if no channel for the specified detector, row and
        column can be located.
        
        """
        try:
            return self.entries[detector, row, column]
        except KeyError:
            return None

    def find_cell(self, cell):
        """Returns the calibration curve corresponding to the input Cell."""
        return self.find(cell.detector, cell.row, cell.column)

# A list of locked bitshifts.
# Input cells with any of these bitshifts will not be modified by optimise().
LOCKED_BITSHIFTS = [-5]

def optimise(cell, newgain):
    """Returns the optimal voltage and bitshift that give the desired gain.
    
    If the gain can be achieved with multiple voltage/bitshift
    combinations, return the one with the smallest magnitude of bitshift.
    Returns two integers: the voltage and the bitshift.
    If no combination exists that can achieve the gain, returns None for
    both values.
    
    """
    # First, skip the cell if it has a locked bitshift.
    if cell.qt.bitshift in LOCKED_BITSHIFTS:
        # Return existing values.
        return cell.voltage, cell.qt.bitshift, cell.gain
    calibration = cell.calibration
    # Gain = normalisation * ADC * 2^bitshift
    # The normalisation is determined by the current gain/ADC of the cell.
    norm = cell.gain / calibration.get_adc(cell.voltage)
    # Collect the bitshift/voltage combinations that allow us to
    # achieve the desired gain
    valid = []
    for shift in qt.VALID_BITSHIFTS:
        # Find the ADC required to give the desired gain at each bitshift,
        # accounting for the change in bitshift
        try:
            adc = newgain / norm / math.pow(2., shift - cell.qt.bitshift)
            v = calibration.get_voltage_for_adc(adc)
            if not cell.is_valid_voltage(v, shift):
                continue;
            valid.append((v, shift))
        except ZeroDivisionError:
            print 'cell', cell.detector, cell.channel, cell.row, cell.column, cell.voltage
            print 'newgain', newgain, 'norm', norm, 'shift', shift, 'cell.qt.bitshift', cell.qt.bitshift
    v, shift, gain = None, None, newgain
    # Sort (voltage, bitshift) pairs by absolute value of bitshift.
    # Bitshifts become ordered sush that for example [-2, -1, 0, 1, 2]
    # would become [0, -1, 1, -2, 2].
    valid.sort(key=lambda x: abs(x[1]))
    if valid:
        v = valid[0][0]
        shift = valid[0][1]
    else:
        # If we didn't find a valid voltage, the gain was either too high
        # or low to be achieved. Set both the voltage and bitshift to
        # their limits (either high or low) to get as close as we can.
        oldshift = cell.qt.bitshift
        if newgain < cell.gain:
            # We want a reduced gain, set voltage and bitshift to min.
            shift = qt.VALID_BITSHIFTS[0]
            v = cell.min_voltage(shift)
        else:
            # We want an increased gain, set voltage and bitshift to max.
            shift = qt.VALID_BITSHIFTS[-1]
            v = cell.max_voltage(shift)
        gain = norm * calibration.get_adc(v) * math.pow(2., shift - oldshift)
    return v, shift, gain