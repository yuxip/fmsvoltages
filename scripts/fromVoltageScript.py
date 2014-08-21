#!/usr/bin/env python

"""Convert voltage scripts to voltage/gain files.

For large cells, where there are multiple scripts, the names
of all the scripts should be passed as command line arguments
to properly access values for all cells.
"""

import os
import re
import sys

import cellinfo
import fms.detector

DETECTORS = {
    1: fms.detector.LargeDetector(1),
    2: fms.detector.LargeDetector(2),
    3: fms.detector.SmallDetector(3),
    4: fms.detector.SmallDetector(4)
}

INFOTABLE = cellinfo.Table(os.path.join(os.getenv('FMSVOLTAGES'), 'fmsCellInfoTable.txt'))

# Regular expression pattern to look for a pattern like this:
# (slot,channel)<whitespace>[-]voltage
# Requires slot and channel to be 1 or 2 digits, voltage to be
# no more than 4.
RE_PATTERN = '\(([0-9]{1,2}),([0-9]{1,2})\)[ \t]*([\-]?[0-9]{1,4})'

def get_lecroy_from_voltage_script(line):
    """Returns lecroy slot and channel and the voltage
    
    The input line should be formatted like
       echo -e "write (0,0) -1373\r"; sleep 2;
    where the slot and channel are in (slot, channel) and voltage
    is the negative number following that.
    Returns None for all values if the input is invalid.
    """
    try:
        match = re.search(RE_PATTERN, line)
        slot, channel, voltage = [int(i) for i in match.groups()]
        return slot, channel, voltage
    except:
        return None, None, None

def telnet_from_filename(filename):
    """Extract telnet number from voltage script name.
    
    Filename format is fms_hv_large_north_1_7006.sh.
    Telnet numbers are 7005 to 7008.
    Returns None if the input is invalid.
    """
    try:
        return int(re.search('(700[5-8]{1})', filename).group(0))
    except:
        return None

def process_large(filename):
    """Processes a single file with large cell information."""
    with open(filename) as file:
        lines = [line for line in file.read().splitlines() if 'write (' in line]
    for line in lines:
        slot, channel, voltage = get_lecroy_from_voltage_script(line)
        if None in [slot, channel, voltage]:
            continue
        cell = fms.cell.Large()
        cell.lecroy.telnet = telnet_from_filename(filename)
        cell.lecroy.slot, cell.lecroy.channel = slot, channel
        info = INFOTABLE.from_address(cell)
        if not info:
            print filename, cell.detector, cell.channel, cell.lecroy.telnet, cell.lecroy.slot, cell.lecroy.channel
        cell = DETECTORS[info.detector].get_cell(info.row, info.column)
        cell.voltage = abs(voltage)
        cell.gain = 1.

def process_small(filename):
    # Detector number keyed by 'device number'.
    # Small detector 3 is device 1, detector 4 is device 0.
    detector = {1: 3, 0: 4}
    # We need to process the lines one-by-one so we can track
    # when the device, chip or channel change.
    # Construct a Small cell to use to search the info table.
    searchcell = fms.cell.Small()
    with open(filename) as file:
        lines = file.read().splitlines()
    for line in lines:
        # Change in device is done by a line like
        # !SETdevice 0
        if '!SETdevice' in line:
            searchcell.device = int(line.split()[1])
        # Change in chip/channel is done by a line like
        # !setctrl 0 0
        elif '!setctrl' in line:
            words = line.split()
            searchcell.chip = int(words[1])
            searchcell.channel = int(words[2])
        # Setting channel voltage is done by a line like
        # !rdac EA 0x66
        elif '!rdac' in line:
            words = line.split()
            searchcell.address = int(words[1], 16)
            searchcell.voltage = int(words[2], 16)
            info = INFOTABLE.from_address(searchcell)
            if info is None:
                print 'Failed to locate channel:'
                print searchcell.device, searchcell.chip, searchcell.channel, hex(searchcell.address)
            # The info lets us get the detector, row and column
            # for the cell with this device/chip/channel/address
            else:
                cell = DETECTORS[info.detector].get_cell(info.row, info.column)
                cell.voltage = searchcell.voltage
                cell.gain = 1.

def process(filename):
    if 'fms_hv_large_' in filename:
        process_large(filename)
        return 'large'
    elif 'setVoltages' in filename:
        process_small(filename)
        return 'small'
    return None

if __name__ == '__main__':
    processed = [process(filename) for filename in sys.argv[1:]]
    if 'large' in processed:
        with open('largeCellGains.txt', 'w') as file:
            DETECTORS[1].write_gain_table(file)
        with open('largeCellGains.txt', 'a') as file:
            DETECTORS[2].write_gain_table(file)
    if 'small' in processed:
        with open('smallCellGains.txt', 'w') as file:
            DETECTORS[3].write_gain_table(file)
        with open('smallCellGains.txt', 'a') as file:
            DETECTORS[4].write_gain_table(file)
