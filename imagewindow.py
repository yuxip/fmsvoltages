from Tkinter import *
import tkSimpleDialog
import math
import dialog
from fms.detector import *
import calibration
import fms.cell as cell
import os
import fms.geometry as fmsgeom

class CellGraphicsInfo:
    """Stores the graphical properties of cells as drawn on the window."""
    def __init__(self, width_pixels, height_pixels):
        self.width = width_pixels
        self.height = height_pixels


class ImageWindow(Frame):
    """The graphical area on which images of the cells are drawn.
    
    Users can click on these to manaully change individual
    cell voltages and gains.
    
    """
    def get_cell_graphics_info(self, celltype):
        """Computes cell graphical properties for a type of cell.
        
        Valid celltype arguments are 'large' or 'small'.
        Returns a CellGraphicsInfo for that cell type.
        
        """
        # Compute the properties for large cells first.
        # The small cell properties are computed relative to
        # those of the large cells.
        # We want the small cells to be exaclty 2/3 the dimensions
        # of the large cells, as we need to fit 24 small cells in
        # a hole formed by the absence of 16 large cells.
        # Therefore we make sure the large cells are drawn
        # a multiple of 3 pixels in each direction.
        # Note that ncolumns() return the number PER-SUBDETECTOR,
        # so there are twice this number in total.
        width = int(self.width / 2 / fmsgeom.Large.ncolumns())
        while width % 3 != 0:
            width -= 1
        height = int(self.height / fmsgeom.Large.nrows())
        while height % 3 != 0:
            height -= 1
        # If we are calculating for a small cell, take 2/3 of the dimensions
        if celltype == 'small':
            width  = width * fmsgeom.Large.gapsize() / fmsgeom.Small.nrows()
            height = height * fmsgeom.Large.gapsize() / fmsgeom.Small.nrows()
        return CellGraphicsInfo(width, height)

    # The ImageWindow needs access to a gain table
    # so that values can be read and modified when
    # the image of that cell is clicked.
    def __init__(self, detectors, tkroot):
        Frame.__init__(self, tkroot)
        self.pack()
        # This is a dictionary associating the rectangules drawn on the
        # canvas with the corresponding cell object.
        # key - canvas object id number
        # value - actual cell object from input detectors
        self.cells = {}
        # Store a reference to the input directories.
        # This is a dictionary, keyed by NORTH_LARGE... etc
        # and storing a LargeDetector or SmallDetector for each.
        # This is how we access the cells and retrieve and update
        # their information
        self.detectors = detectors
        self.tkroot = tkroot
        # Set to true every time a cell is modified
        # Set to false when all files are saved
        self.modified = False
        
        # Find the width and height of the display from Tkinter
        # We don't want the cells occupying the whole screen,
        # so only take 90% of the screen width.
        self.height = min(tkroot.winfo_screenheight() * 0.9, 1600)
        self.width = self.height
        # This is also the total number of columns (half this
        # number in each of two sub-detectors).
        nrows_large = fmsgeom.Large.nrows()
        nrows_large_gap = fmsgeom.Large.gapsize()
        nrows_small = fmsgeom.Small.nrows()
        nrows_small_gap = fmsgeom.Small.gapsize()
        # Compute large and small cell graphical sizes.
        self.large = self.get_cell_graphics_info('large')
        self.small = self.get_cell_graphics_info('small')
        # Simple status bar
        self.status = Label(self, text='fmsvoltages', bd=1, relief='sunken',
            anchor=W)
        self.status.pack(side=BOTTOM, fill=X)
        # The total width to draw on is determined by the large cells.
        self.drawn_width = nrows_large * self.large.width
        self.drawn_height = nrows_large * self.large.height
        # Add padding around the drawn area in the window
        self.padding_width = 10 # pixels on each side
        self.padding_height = 10
        self.canvas_width = self.drawn_width + 2 * self.padding_width
        self.canvas_height = self.drawn_height + 2 * self.padding_height
        # Create the actual canvas and bind the function
        # to determine the cell corresponding to the point clicked.
        self.canvas = Canvas(self, bg='black', width=self.canvas_width, height=self.canvas_height)
        self.canvas.bind("<Button-2>", self.determine_cell)
        self.canvas.bind("<Button-3>", self.determine_cell)
        self.canvas.pack(side=TOP)
        # xoffset marks the start of the right half of the window.
        # Cells for the north detector are drawn in the right half,
        # those for the south detector are drawn in the left half.
        # yoffset is the bottom edge of the drawn area; rows are
        # drawn up from here.
        # Remember that y = 0 is the top of the window.
        self.xoffset = self.canvas_width / 2
        self.large_yoffset = self.drawn_height + self.padding_height
        self.draw_cells(detectors)
        left = self.canvas_width/2 - 20
        right = self.canvas_width/2 + 20
        top = self.canvas_height/2 - 20
        bottom = self.canvas_height/2 + 20
        middlex = self.canvas_width/2
        middley = self.canvas_height/2
        self.canvas.create_oval(left, top, right, bottom, fill='white')
        self.canvas.create_oval(middlex-2, middley-2, middlex+2, middley+2, fill='white')
        self.canvas.focus_set()
    
    def draw_cells(self, detectors):
        nrows_large = fmsgeom.Large.nrows()
        nrows_large_gap = fmsgeom.Large.gapsize()
        nrows_small = fmsgeom.Small.nrows()
        nrows_small_gap = fmsgeom.Small.gapsize()
        # Create rectangles for each large cell
        for column in range(0, nrows_large / 2):
            for row in range(0, nrows_large):
                # Skip central hole where small cells go
                if column < 8 and row > 8 and row < 25:
                    continue
                # Skip corners
                # Number bottom rows symmetrically with top rows
                # allowing easy skipping of both top & bottom
                # corners at once.
                altrow = row
                if row < 16:
                    altrow = nrows_large - 1 - row
                if column + altrow > 42:
                    continue
                x = self.xoffset + self.large.width * column
                y = self.large_yoffset - self.large.height * (nrows_large - 1 - row)
                label = str(column) + ', ' + str(row)
                # Cells for columns right of centre.
                # Column number increases left to right.
                rec1 = self.canvas.create_rectangle(x, y ,
                   x + self.large.width - 1, y - (self.large.height - 1))
                self.canvas.tag_bind(rec1, '<Enter>', self.update_status_with_current_cell)
                # Cells for columns left of centre
                x = self.xoffset - self.large.width * (1 + column)
                rec2 = self.canvas.create_rectangle(x, y,
                   x + self.large.width - 1, y - (self.large.height - 1))
                self.canvas.tag_bind(rec2, '<Enter>', self.update_status_with_current_cell)
                self.cells[rec1] = detectors[SOUTH_LARGE].get_cell(row, column)
                self.cells[rec2] = detectors[NORTH_LARGE].get_cell(row, column)
        # Create rectangles for each small cell
        small = SmallDetector(3)
        # Move up by the height of 9 large rows to get to the
        # bottom of the bottom small cell row.
        self.small_yoffset = self.large_yoffset - 9 * self.large.height
        for row in range(0, fmsgeom.Small.nrows()):
            for column in range(0, fmsgeom.Small.ncolumns()):
                if not small.cell_exists(row, column):
                    continue
                x = self.xoffset + self.small.width * column
                y = self.small_yoffset - self.small.height * (fmsgeom.Small.nrows() - 1 - row)
                label = str(column) + ', ' + str(row)
                rec1 = self.canvas.create_rectangle(x, y,
                    x + self.small.width - 1,
                    y - (self.small.height - 1))
                self.canvas.tag_bind(rec1, '<Enter>', self.update_status_with_current_cell)
                x = self.xoffset - self.small.width * (1 + column)
                rec2 = self.canvas.create_rectangle(x, y,
                    x + self.small.width - 1,
                    y - (self.small.height - 1))
                self.canvas.tag_bind(rec2, '<Enter>', self.update_status_with_current_cell)
                self.cells[rec1] = detectors[SOUTH_SMALL].get_cell(row, column)
                self.cells[rec2] = detectors[NORTH_SMALL].get_cell(row, column)
        self.canvas.create_line(0, self.canvas_height / 2+1,
                                self.canvas_width, self.canvas_height / 2+1, width=2, fill='blue')
        self.canvas.create_line(self.canvas_width / 2, 0,
                                self.canvas_width / 2, self.canvas_height, width=2, fill='blue')
        self.canvas.create_text(self.padding_width, self.padding_height, text='North', fill='white', anchor='nw')
        self.canvas.create_text(self.canvas_width - self.padding_width, self.padding_height, text='South', fill='white', anchor='ne')
        self.display_detector() # Colour cells by detector number

    def display_voltage(self):
        colours = {0: "red", 200: "green", 400: "blue", 600: "pink",
            800: "orange", 1000: "brown", 1200: "yellow", 1400: "magenta",
            1600: "cyan"}
        for id, cell in self.cells.iteritems():
            v = cell.voltage
            delta = {abs(v - i): i for i in colours.iterkeys()}
            colour = colours[delta[min(delta)]]
            self.canvas.itemconfig(id, fill=colour)
        voltagelegend = Toplevel()
        voltagelegend.resizable(FALSE, FALSE) # Prevent resizing by the user
        canvas = Canvas(voltagelegend, background='black',
            width=200, height=400)
        canvas.pack()
        for i, colour in colours.iteritems():
            # Add 1 from slot number to give range [1, N]
            # This matches Steve's output format
            Label(canvas, fg=colour, justify=LEFT, font=('Courier', '14'),
                text='{:>4} V'.format(i), background='black').grid(row=i)
        
    def display_detector(self):
        """Sets cell colours by detector number."""
        # Default options.
        options = {'col1': 'red', 'col2': 'dark red',
                   'col3': 'plum', 'col4': 'orchid'}
        # Read options from configuration file, if present.
        # Redo this every time as it means people can update options
        # while running the programme.
        try:
            useropts = {}
            with open(os.path.expanduser('~/.fms/config')) as file:
                def is_comment(line):
                    stripped = line.lstrip()
                    try:
                        if stripped[0] == '#':
                            return True
                        return False
                    except IndexError: # Blank lines are ignored.
                        return True
                lines = [line for line in file.readlines()
                         if not is_comment(line)]
                for line in lines:
                    items = line.split()
                    # Some Tk colours are multiple words e.g. "dark red"
                    # so concatenate all words after the first.
                    useropts[items[0]] = ' '.join(items[1:])
            options.update(useropts)
        except IOError:
            pass
        # Key 'col' option by detector number.
        # The colour for detector i is then options[colours[i]].
        colours = {i: 'col{}'.format(i) for i in range(1, 5)}
        for id, cell in self.cells.iteritems():
            self.canvas.itemconfig(id, fill=options[colours[cell.detector]])

    def display_qt_boards(self):
        # Colours keyed by QT board number
        colours = {0: "red",
                   1: "green",
                   2: "blue",
                   3: "pink",
                   4: "orange",
                   5: "brown",
                   6: "yellow",
                   7: "magenta",
                   8: "cyan",
                   9: "gray",
                   10: "white"}
        for id, cell in self.cells.iteritems():
            board = cell.qt.board
            self.canvas.itemconfig(id, fill=colours[board])
        self.qtboardlegend = Toplevel()
        self.qtboardlegend.resizable(FALSE, FALSE) # Prevent resizing by the user
        canvas = Canvas(self.qtboardlegend, background='black',
            width=200, height=400)
        canvas.pack()
        for i, colour in colours.iteritems():
            # Add 1 from slot number to give range [1, N]
            # This matches Steve's output format
            Label(canvas, fg=colour, justify=LEFT, font=('Courier', '14'),
                text='Board{:>3}'.format(i + 1), background='black').grid(row=i)

    def compute_row_col(self, x, y):
        """Compute the row and column number from a position in the canvas."""
        if self.is_in_small_cell_area(x, y):
            x = int(math.fabs(x - self.xoffset))
            col = x / self.small.width
            row = (self.small_yoffset - y) / self.small.height
        else:
            col = (x - self.xoffset) / self.large.width
            row = (self.large_yoffset - y) / self.large.height
        return row, col

    def compute_cell(self, x, y):
        type = None # Type of fms.cell object to create
        nrows = -1
        if self.is_in_small_cell_area(x, y):
            yoffset = self.small_yoffset
            type = Small
            width = self.small.width
            height = self.small.height
            nrows = fmsgeom.Small.nrows()
            if x > self.xoffset:
                det = SOUTH_SMALL
            else:
                det = NORTH_SMALL
        else:
            yoffset = self.large_yoffset
            type = Large
            width = self.large.width
            height = self.large.height
            nrows = fmsgeom.Large.nrows()
            if x > self.xoffset:
                det = SOUTH_LARGE
            else:
                det = NORTH_LARGE
        # Now just consider the absolute value of x from the window
        # centre, for easier calculation of column number
        x = int(math.fabs(x - self.xoffset))
        col = x / width
        row = nrows - 1 - ((yoffset - y) / height)
        cell = type(int(row), int(col))
        cell.detector = det
        return cell

    def is_in_small_cell_area(self, x, y):
        small_width = self.small.width * fmsgeom.Small.ncolumns()
        small_height = self.small.height * fmsgeom.Small.nrows()
        if x < (self.canvas_width / 2 - small_width):
            return False
        if x > (self.canvas_width / 2 + small_width):
            return False
        if y > (self.canvas_height / 2 + small_height / 2):
            return False
        if y < (self.canvas_height / 2 - small_height / 2):
            return False
        return True

    def update_status_with_current_cell(self, event):
        cell = self.compute_cell(event.x, event.y)
        if cell.row != None and cell.column != None:
            self.status.configure(text='Detector ' + str(cell.detector) + \
                                       ' channel ' + str(cell.channel) + \
                                       ' row ' + str(cell.row) + \
                                       ' column ' + str(cell.column))
    
    def determine_cell(self, event):
        if self.is_in_small_cell_area(event.x, event.y):
            self.select_small_cell(event)
        else:
            self.determine_large_cell(event)

    @classmethod
    def dialog_title(cls, cell):
         return 'Detector {} channel{:>4}'.format(cell.detector, cell.channel)

    def select_small_cell(self, event):
        """Determine which small cell was clicked and open a dialog."""
        row = (self.small_yoffset - event.y) / self.small.height
        row = fmsgeom.Small.nrows() - 1 - row
        if event.x > self.xoffset:
            column = (event.x - self.xoffset) / self.small.width
        else:
            column = (self.xoffset - event.x) / self.small.width
        detector = NORTH_SMALL
        if event.x > self.xoffset:
            detector = SOUTH_SMALL
        cell = self.detectors[detector].get_cell(row, column)
        if cell is not None:
            d = dialog.CellDialog(self.tkroot,
                    self.dialog_title(cell), cell)
            # Update the overall programme modified state.
            self.modified = d.modified or self.modified
            self.canvas.focus_set()

    def determine_large_cell(self, event):
        """Determine which large cell was clicked and open a dialog."""
        row = (self.large_yoffset - event.y) / self.large.height
        row = fmsgeom.Large.nrows() - 1 -row
        if event.x > self.xoffset:
            column = (event.x - self.xoffset) / self.large.width
        else:
            column = (self.xoffset - event.x) / self.large.width
        detector = NORTH_LARGE
        if event.x > self.xoffset:
            detector = SOUTH_LARGE
        cell = self.detectors[detector].get_cell(row, column)
        if cell is not None:
            d = dialog.CellDialog(self.tkroot,
                    self.dialog_title(cell), cell)
            self.modified = d.modified or self.modified
            self.canvas.focus_set()