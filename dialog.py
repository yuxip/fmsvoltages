import copy
import decimal
import math
import os

from Tkinter import *
import tkMessageBox

from fms.cell import Large, Small
import calibration
import qt

LABEL_FONT = ('Courier', '14')

class Dialog(Toplevel):
    """Dialog base class with basic functionality.
    
    I got this from a tutorial page, I don't really understand how it all works!
    
    """
    def __init__(self, parent, title, cell=None):
        Toplevel.__init__(self, parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        # Position this window relative to its parent.
        self.geometry("+{}+{}".format(
            parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        self.transient(parent) # Associate this window with its parent
        self.title(title)
        self.resizable(FALSE, FALSE) # Prevent resizing by the user
        self.parent = parent # So we can return focus to the parent later.
        self.modified = False # Tracks modifications by the user
        self.cell = cell
        # Record the initial settings of the cell so we can track which of
        # them change.
        self.initial = copy.deepcopy(cell)
        self.frame = Frame(self)
        self.initial_focus = self.body()
        self.frame.pack(padx=5, pady=5)
        self.buttonbox()
        # Prevent other dialogs being opened until this one is closed.
        # Need a little trick to get around this error on Linux:
        # TclError: grab failed: window not viewable
        # Thank you to this guy here!
        # http://www.python-forum.org/pythonforum/viewtopic.php?f=4&t=5120
        while True:
            try:
                self.grab_set()
            except TclError:
                pass
            else:
                break
        if not self.initial_focus:
            self.initial_focus = self
        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self):
        """Create dialog body.
        
        Return widget that should have initial focus.
        This method should be overridden.
        
        """
        pass

    def buttonbox(self):
        """Add standard button box."""     
        box = Frame(self)
        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("&lt;Return>", self.ok)
        self.bind("&lt;Escape>", self.cancel)
        box.pack()

    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # Return focus to the parent window
        self.parent.focus_set()
        self.destroy()

    def validate(self):
        return True # override

    def apply(self):
        pass # override


class CellDialog(Dialog):
    def enable_gain_change(self):
        """Enables setting of gain Entry by user."""
        self.bitshiftscale.config(state=DISABLED)
        self.entry_volt.config(state=DISABLED)
        self.entry_gain.config(state=NORMAL)
        
    def enable_voltage_change(self):
        """Enables setting of voltage Entry by user."""
        self.bitshiftscale.config(state=NORMAL)
        self.entry_volt.config(state=NORMAL)
        self.entry_gain.config(state=DISABLED)

    def make_radio(self, gridrow):
        """Create the voltage/gain radio buttons"""
        # Radio buttons to allow either voltage/bitshift or gain change
        self.radio = StringVar()
        self.radio.set('Voltage')
        choose_voltage = Radiobutton(self.frame, variable=self.radio,
            text='Voltage', value='Voltage', font=LABEL_FONT,
            command=self.enable_voltage_change)
        choose_voltage.grid(row=gridrow, column=0)
        choose_gain = Radiobutton(self.frame, variable=self.radio,
            text='Gain', value='Gain', font=LABEL_FONT,
            command=self.enable_gain_change)
        choose_gain.grid(row=gridrow, column=1)

    def reset(self):
        """Sets the user-modifiable elements to initial values.
        
        Internal stored values are also reset.
        
        """
        # Enable all inputs so the values can be changed
        self.bitshiftscale.config(state=NORMAL)
        self.entry_volt.config(state=NORMAL)
        self.entry_gain.config(state=NORMAL)
        # Insert initial cell properties
        self.entry_volt.delete(0, END)
        self.entry_volt.insert(0, self.cell.voltage_int_to_str(
            self.cell.voltage))
        self.entry_gain.delete(0, END)
        gain = round(self.cell.gain, 3)
        self.entry_gain.insert(0, gain)
        # Return Radiobutton, Entry, Scale to default state
        self.enable_voltage_change()
        self.radio.set('Voltage')
        self.bitshift.set(self.cell.qt.bitshift)
        # Cache the initial gain separately because of the effect of rounding
        self.initialgain = float(gain)
        # Reset cached values
        self.changes = [] # Lists the types of changes made
        self.inputvolt = self.cell.voltage
        self.inputgain = self.cell.gain

    def labels(self, values, titles, startrow, ncolumns):
        """"""
        layout = '{:<9}{:>5}' # text and value e.g. "Detector   4"
        labels = [Label(self.frame, text=layout.format(title, value),
                        font=LABEL_FONT, justify=LEFT)
                  for title, value in zip(titles, values)]
        # Define grid for the labels.
        for n, label in enumerate(labels):
            row = startrow + n / ncolumns
            column = n % ncolumns
            label.grid(row=row, column=column)
        # Return the new row number.
        return startrow + int(math.ceil(len(labels) / float(ncolumns)))

    def body(self):
        """Construct the dialog contents"""
        cell = self.cell
        if not cell:
            return
        gridrow = 0
        # Create radio buttons to switch between modifying voltages or gains.
        self.make_radio(gridrow)
        gridrow += 1
        # Label and entry box for voltage.
        self.entry_volt = Entry(self.frame, font=LABEL_FONT, width=10)
        self.entry_volt.grid(row=gridrow, column=1)
        Label(self.frame, text="Voltage", font=LABEL_FONT, justify=LEFT).grid(
            row=gridrow, column=0)
        gridrow += 1
        # Label and entry box for gain.
        self.entry_gain = Entry(self.frame, font=LABEL_FONT, width=10)
        self.entry_gain.grid(row=gridrow, column=1)
        Label(self.frame, text="Gain", font=LABEL_FONT, justify=LEFT).grid(
            row=gridrow, column=0)
        gridrow += 1
        # Standard cell information.
        gridrow = self.labels(
            [cell.detector, cell.channel, cell.row, cell.column],
            ['Detector', 'Channel', 'Row', 'Column'], gridrow, 2)
        # Large- and small-cell-specific information.
        # We have to handle Small and Large differently
        # because of differing variables
        if isinstance(cell, Small):
            address = cell.voltage_int_to_str(cell.address)
            gridrow = self.labels(
                [cell.device, cell.chip, cell.chan, address],
                ['Device', 'Chip', 'Channel', 'Address'], gridrow, 2)
        if isinstance(cell, Large):
            gridrow = self.labels(
                [cell.lecroy.telnet, cell.lecroy.slot, cell.lecroy.channel],
                ['Telnet', 'Slot', 'Channel'], gridrow, 2)
        # Now we do all the QT stuff, starting with a line to
        # delimit the previous information.
        Label(self.frame, text='QT information', relief=RAISED,
              font=LABEL_FONT).grid(row=gridrow)
        gridrow += 1
        gridrow = self.labels([cell.qt.crate, cell.qt.board + 1,
                               cell.qt.number, cell.qt.pedestal],
            ['Crate', 'Slot', 'Channel', 'Pedestal'], gridrow, 2)
        # Provide a scale to set the bitshift
        self.bitshift = IntVar()
        self.bitshift.set(cell.qt.bitshift)
        Label(self.frame, text='Bitshift', font=LABEL_FONT).grid(
            row=gridrow, column=0)
        self.bitshiftscale = Scale(self.frame, orient=HORIZONTAL,
            from_=qt.VALID_BITSHIFTS[0], to=qt.VALID_BITSHIFTS[-1],
            tickinterval=5, variable=self.bitshift, font=LABEL_FONT)
        self.bitshiftscale.grid(row=gridrow, column=1)
        # Initialise all entries
        self.reset()
        return self.entry_volt # initial focus

    def validate(self):
        """Check that user input was valid"""
        # Each Entry stores the input as a string, so we have to convert.
        # Small and large cells use different formats (hex vs. dec) so
        # use the voltage_str_to_int() classmethod to convert.
        volt = self.cell.voltage_str_to_int(self.entry_volt.get())
        gain = float(self.entry_gain.get())
        self.changes = []
        error = False
        # Validate the voltage and/or bitshift change
        if not self.cell.is_valid_voltage(volt, self.bitshift.get()):
            vmin = self.cell.min_voltage(shift)
            vmax = self.cell.max_voltage(shift)
            tkMessageBox.showerror('WTF?!',
                'Voltage must be between {} and {} for bitshift {}'.format(
                    vmin, vmax, self.bitshift.get()))
            error = True
        # Validate the gain change
        if not gain or gain < 0. or math.isinf(gain) or math.isnan(gain):
            tkMessageBox.showerror('Are you having a laugh?', 'Invalid gain')
            error = True
        # Cache which things changed so apply() can change the correct things
        if volt != self.initial.voltage:
            self.changes.append('volt')
        if gain != self.initialgain:
            self.changes.append('gain')
        if self.bitshift.get() != self.initial.qt.bitshift:
            self.changes.append('shift')
        # Things get broken if gain AND voltage/bitshift change at the
        # same time, so forbid it.
        if ('volt' in self.changes or 'shift' in self.changes)\
            and 'gain' in self.changes:
            tkMessageBox.showerror('Why I oughta...',
                'Gain cannot be manually changed at the same time ' +
                'as voltage or bitshift')
            error = True
        # If we hit an error reset the dialog so the user can try again.
        # If we're OK, cache the input voltage and gain so we can apply().
        if error:
            self.reset()
        else:
            self.inputvolt = volt
            self.inputgain = gain
        return not error

    def apply(self):
        """Apply the changes from user input to the cell.
        
        The cell attribute is modified according to the user's input,
        which should already have been verified by validate().
        
        """
        # Apply gain change if that was the selected option
        if 'gain' in self.changes:
            volt, shift, gain = calibration.optimise(self.cell, self.inputgain)
            if self.cell.is_valid_voltage(volt) and shift in qt.VALID_BITSHIFTS:
                self.cell.gain = gain
                self.cell.voltage = volt
                self.cell.qt.bitshift = shift
            else:
                self.changes.remove('gain')
        # Apply voltage/bitshift change if that was the selected option
        elif 'volt' in self.changes or 'shift' in self.changes:
            gain = self.cell.compute_gain(self.inputvolt, self.bitshift.get())
            self.cell.gain = gain
            self.cell.voltage = self.inputvolt
            self.cell.qt.bitshift = self.bitshift.get()
        self.modified = any(self.changes)