#!/usr/bin/env python

"""Classes for producing LeCroy controller scripts."""

import os.path
import re
import sys

TELNET_NAME = {7005: 'north_2',
               7006: 'north_1',
               7007: 'south_2',
               7008: 'south_1'}

class Channel:
    def __init__(self):
        self.telnet = -1
        self.slot = -1
        self.channel = -1

class Printer:
    """Relations between telnet numbers and controller script filenames."""
    
    def __init__(self, telnet):
        """Constructor.

        @param self   The object pointer
        @param telnet The telnet number
        
        """
        if telnet not in TELNET_NAME:
            raise ValueError(str(telnet) + ' is not a valid telnet number')
        self.telnet = telnet

    @classmethod
    def cell_to_string(cls, cell):
        """.Generate a string for output from a fms.cell.Large.

        The output format looks like this:
        echo -e "write (0,0) -1388\r"; sleep 2;
        Where (0,0) is the cell's LeCroy (slot, channel) and -1388 is voltage.
        @param cell A fms.cell.Large.
        
        """
        # Note we put the '-' sign in front of the voltage ourselves
        # as it is stored as a positive value
        'echo -e \"write ({},{}) -{}\\r\"; sleep 2;'.format(
            cell.lecroy.slot, cell.lecroy.channel, cell.voltage)

    def generate(self, detector, path='.'):
        """Generate an output file.
        
        The output file name is based on the telnet number (see TELNET_NAME)
        @param self     The object pointer
        @param detector An object inheriting from detector.Detector
        @param path     Output directory for the file.
        
        """
        name = 'fms_hv_large_{}_{}.sh'.format(
            TELNET_NAME[self.telnet], self.telnet)
        name = os.path.join(path, name)
        with open(name, 'w') as file:
            # Print the leading stuff
            self.preamble(file)
            # Loop over cells and write all those
            channels = {}
            for cell in detector.cells:
                # Skip cells with the wrong telnet
                if cell.lecroy.telnet != self.telnet:
                    continue
                # We want to sort the cells by slot and channel, so
                # don't write the output here.
                # Store (slot, channel) tuple with voltage, then sort
                channels[ (cell.lecroy.slot, cell.lecroy.channel) ] = \
                    cell.voltage
            # We have all the cells now. Sort and print them
            for (i, j), k in sorted(channels.iteritems()):
                # Note that we:
                # Remove whitespace in (slot, channel) tuple
                # Need to add the negative sign before the voltage
                line = 'echo -e \"write ({},{}) -{}\\r\"; sleep 2;\n'.format(
                    i, j, k)
                file.write(line)
            # Closing statements
            self.tail(file)
        # file automatically closes after 'with' statement

    @classmethod
    def preamble(cls, file = None):
        """Prints the mandatory file preamble to a file.
        
        @param cls  The class
        @param file A writeable file object
        
        """
        lines = [
            "#!/bin/bash\n",
            "t=`date +%Y.%h.%d-%H.%d.%S`\n",
            "(\n" ,
            "sleep 2;\n",
            "echo -e \"\\r\";\n",
            "sleep 1;\n",
            "echo -e \"read (0-15,0-15) \\r\";\n",
            "sleep 5;\n",
            "echo -e \"set voltage limit 1600 \\r\";\n",
            "echo -e \"\\r\";\n",
            "echo -e \"write (0-15,0-15) -900\\r\"; sleep 2;\n\n"
        ]
        for i in lines:
            if file: file.write(i)
            else: print i

    def tail(self, file=None):
        """Prints closing commands to a file.
        
        Does not close the file.
        @param self   The object pointer
        @param file   A writeable file object
        
        """
        lines = [
            "\nsleep 2;\n",
            "echo -e \"read (0-15,0-15)\\r\";\n",
            "sleep 10;\n",
            "echo -e \"\\r\";\n",
            "echo -e \"\\r\";\n",
            "echo -e \"^]\";\n",
            "sleep 1;\n",
            ") | telnet fms-serv.trg.bnl.local {}".format(self.telnet),
            " > ../hvlog_run11/fms_hv2_{}_$t.tex\n".format(self.telnet),
            "echo Set new HV\n",
            "cat ../hvlog_run11/fms_hv2_{}_$t.tex\n".format(self.telnet)
        ]
        for i in lines:
            file.write(i)
