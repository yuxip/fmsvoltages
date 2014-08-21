"""Cell summary information."""

from Tkinter import *

import calibration
import fms.cell

class Cell:
    # Voltage number base keyed by detector.
    # Large cells have decimal values, small cells have hexadecimal values.
    base = {1: 10, 2: 10, 3: 16, 4: 16}
    """Contains static information for a single FMS cell.
    
    The contents of this table are never modified after being read, and
    are never written as output. They are purely used for reference when
    setting up other object tables e.g. QT, gains etc.
    """
    def __init__(self, str=None):
        """Constructor.
        
        Optionally initialise values from a string.
        See set_from_string() for the expected string format.
        """
        # Detector geometry, initialised to dummy values.
        self.detector, self.channel, self.row, self.column = 4 * [-1]
        # QT information, initialised to dummy values.
        # QT slot is also known as QT board in detector.Cell.
        # The QT channel number in detector.Cell equals
        # 8 * QT daughter card + QT daughter channel here
        self.qtcrate, self.qtslot, self.qtchannel, \
        self.qtdaughtercard, self.qtdaughterchannel = 5 * [-1]
        # Miscellaneous IDs.
        # These have different meanings for small and large cells.
        self.id1, self.id2, self.id3, self.id4 = 4 * [-1]
        # Calibration information
        # This is later set to either an ChannelSmall() or ChannelLarge()
        # depending on which detector is specified.
        self.calibration = calibration.Channel()
        if str:
            self.set_from_string(str)

    def set_from_string(self, str):
        """Set gain and voltage attributes.
        
        String format: "detector channel row column qtcrate qtslot
        qtdaughtercard qtdaughterchannel id1 id2 id3 id4"

        """
        words = str.split()
        # Unpack the first 11 words and convert to integers.
        self.detector, self.channel, self.row, self.column, self.qtcrate,\
        self.qtslot, self.qtdaughtercard, self.qtdaughterchannel,\
        self.id1, self.id2, self.id3 = [int(i) for i in words[:11]]
        # Compute the overall QT channel from the daughter card information.
        self.qtchannel = 8 * self.qtdaughtercard + self.qtdaughterchannel
        # Need special processing of the last value.
        self.id4 = int(words[11], Cell.base[self.detector])
        # Info table stores QT slot in the range [1, 11], whereas other
        # code (e.g. qtsystem) defines it in the range [0, 10].
        # For consistency with that, we store it internally here as [0, 10].
        self.qtslot -= 1

    def to_string(self):
        # Print the last entry as a hexadecimal if this is a small cell.
        id4 = self.id4
        if self.detector > 2:
            id4 = hex(self.id4).lstrip('0x').upper()
        items = [self.detector, self.channel, self.row, self.column,\
        self.qtcrate, self.qtslot, self.qtdaughtercard, self.qtdaughterchannel,\
        self.id1, self.id2, self.id3, id4] + self.calibration.p
        return ''.join(len(items) * ['{:>8}']).format(*items)
        return line


class Table:
    """Create a table reading values from a file."""
    def __init__(self, filename='fmsCellInfoTable.txt'):
        with open(filename) as file:
            self.entries = [Cell(line) for line in file.readlines()]

    def from_address(self, obj):
        """Locate a cell via address information.
        
        Finds Small cells via device/chip/channel/address.
        Finds Large cells via lecroy telnet/slot/channel.
        """
        if isinstance(obj, fms.cell.Large):
            for entry in self.entries:
                if entry.id1 == obj.lecroy.telnet and \
                   entry.id3 == obj.lecroy.slot and \
                   entry.id4 == obj.lecroy.channel:
                    return entry
        elif isinstance(obj, fms.cell.Small):
            for entry in self.entries:
                # Note offset of 1 between id1 stored in table and device
                if entry.id1 == (1 + obj.device) and entry.id2 == obj.chip and \
                   entry.id3 == obj.channel and entry.id4 == obj.address:
                    return entry
        return None

    def view(self, root=None):
        """Create a window containing table contents."""
        if root == None:
            root = Tk()
        scrollbar = Scrollbar(root)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox = Listbox(root, yscrollcommand=scrollbar.set,
            height=30, width=120,
            font=('Courier', '14'))
        for entry in self.entries:
            listbox.insert(END, entry.to_string())
        listbox.pack(side=TOP, fill=NONE)
        scrollbar.config(command=listbox.yview)
        mainloop()
