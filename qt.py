"""A collection of classes describing the FMS QT system."""

import os

# Compose the expected file name for each QT crate
FILENAMES = {i: 'qt{}_tac.dat'.format(i) for i in range(1, 5)}

# A list containing all valid bitshifts, [-5, 5]
VALID_BITSHIFTS = range(-5, 6)

class Channel:
    """Describes the pedestal and bit shift state of a single QT channel."""
    def __init__(self, crate=-1, board=-1, channel=-1, pedestal=-1, bitshift=0):
        """Initialise the channel.
        
        Valid board numbers are 0 to 11.
        Valid channel numbers are 0 to 31.
        Valid pedestal values are 0 to 4096. A pedestal of < 0 is ignored.
        Valid bit shifts are -5 to +5.
        
        """
        self.crate = crate
        self.board = board
        self.number = channel
        self.pedestal = pedestal
        self.bitshift = bitshift

    def match(self, crate, board, number):
        """Compares board and channel numbers."""
        return crate == self.crate and board == self.board and \
               number == self.number
        
    def set_info(self, cell):
        """Set miscellaneous information from cellinfo.Cell.
        
        Sets QT crate, slot and channel numbers.
        
        """
        self.crate = cell.qtcrate
        self.board = cell.qtslot
        self.number = 8 * cell.qtdaughtercard + cell.qtdaughterchannel

    @classmethod
    def from_string(cls, string, crate=-1):
        """Returns a Channel initialised from a string.
        
        The string provides board, channel, pedestal and bitshift
        but not the crate number, for historical reasons related to
        the data format used by the FMS group. i.e.
        "board channel pedestal bitshift".
        The crate number can optionally be specified via the last argument.
        
        """
        # The argument string provides "board channel pedestal bitshift",
        # which we split, convert to [int] and unpack to pass as arguments
        # to the constructor.
        return cls(crate, *[int(i) for i in string.split()])
    
    def to_string(self):
        """Convert the entry's contents to a string.
        
        The format is "board channel pedestal bit-shift".
        
        """
        # Note the explicit inclusion of the sign for positive bit-shift.
        # Have to treat 0 separately to avoid "+0".
        if 0 == self.bitshift:
            layout = '{} {:>2} {} {:>2}'
        else:
            layout = '{} {:>2} {} {:>+2}'
        return layout.format(self.board, self.number,
                             self.pedestal, self.bitshift)

    def daughter_channel(self):
        """Channel number on QT daughter card.
        
        Each QT board contains 4 daughter cards each with 8 channels.
        
        """
        return self.number % 8

    def daughter_card(self):
        """Number of the QT daughter card.
        
        Each QT board contains 4 daughter cards each with 8 channels.
        
        """
        return (self.number - self.daughter_channel()) / 8


class Crate:
    """Organises QT channels at the crate level."""
    def __init__(self, filename, number):
        """Populate the crate from an input file and crate number."""
        # Ensure valid QT crate number.
        if number < 1 or number > 4:
            raise ValueError('Invalid QT crate number {}'.format(number))
        self.number = number
        # Construct channel list from the input file.
        with open(filename) as file:
            lines = file.readlines()
            self.entries = [Channel.from_string(line, number) for line in lines]

    def write(self, filename):
        """Write all the entries to a file.
        
        Replaces existing file contents.
        
        """
        with open(filename, 'w') as file:
            for entry in self.entries:
                file.write(entry.to_string() + '\n')

    def get_entry(self, board, channel):
        """Returns a QT channel by board and channel numbers.
        
        Returns the first matching channel in the crate, or None
        if the channel is not present in the crate.
        \todo Reorganise self.entries as a dictionary
        """
        matches = [i for i in self.entries
                   if i.match(self.number, board, channel)]
        if matches:
            return matches[0]
        else:
            return None


class System:
    """Describes the entire QT system of four crates.
    
    Handles I/O of QT information for all crates from/to files in a single
    directory.
    
    """
    def __init__(self, dir):
        """Initialise the system from four text files (one per crate).
        
        The text files should be named "qt#_tac.dat", where # is
        the QT crate number (1 to 4).
        Read files from the specified directory.
        
        """
        # A dictionary of Crate objects keyed by crate number
        self.crates = {qt: Crate(os.path.join(dir, file), qt)
                       for qt, file in FILENAMES.iteritems()}

    def write(self, dir):
        """Write all files to a directory."""
        for qt, crate in self.crates.iteritems():
            crate.write(os.path.join(dir, FILENAMES[qt]))

    def get_channel(self, test):
        """Returns a QT channel.
        
        Input argument is a Channel() object.
        Returns None if the channel is not present in the system.
        
        """
        if test.crate in self.crates:
            return self.crates[test.crate].get_entry(test.board, test.number)
        else:
            return None