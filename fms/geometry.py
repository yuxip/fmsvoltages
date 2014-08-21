import math

"""Definitions of FMS geometrical information for
small and large cells and detectors.
class Base is a base class for Small and Large, which
define small- and large-cell detector geometry information
respectively.
"""

## Base class defining geometry interface
class Base(object):

    """Base class for geometrical information.
    """

    @classmethod
    def nrows(cls):
        pass


    @classmethod
    def ncolumns(cls):
        pass


    @classmethod
    def ncells(cls):
        pass


    @classmethod
    def gapsize(cls):
        pass


    @classmethod
    def cellwidth(cls):
        pass


    @classmethod
    def cellheight(cls):
        pass


    @classmethod
    def zposition(cls):
        pass


    @classmethod
    def hascell(cls, row, column):
        """Returns True if a detector of this type has a cell at position
        (row, column) or False if it does not.
        @param row The row in the range [0, nrows)
        @param column The column in the range [0, ncolumns)
        """
        pass


    @classmethod
    def pseudorapidity(cls, row, column):
        """Returns the pseudorapidity of the cell at (row, column).
        The value returned is at the cell centre.
        Returns None if there is no cell at (row, column)
        """
        if not cls.hascell(row, column):
            print 'no such cell'
            return None

        # Compute the coordinates of the centre
        x = (column + 0.5) * cls.cellheight()
        y = (cls.nrows() / 2 - row - 0.5) * cls.cellwidth()
        r = math.sqrt(math.pow(x, 2.) + math.pow(y, 2.))
        # eta = -log(tan(theta/2))
        theta = math.atan(r / cls.zposition())
        return -(math.log(math.tan(theta / 2.)))


## Defines geometry of small cells and small-cell detectors
class Small(Base):

    """Small-cell detector geometrical information.
    """

    @classmethod
    def nrows(cls):
        """Returns the number of rows of cells per sub-detector"""
        return 24


    @classmethod
    def ncolumns(cls):
        """Returns the number of columns of cells per sub-detector"""
        return cls.nrows() / 2


    @classmethod
    def ncells(cls):
        return 238


    @classmethod
    def gapsize(cls):
        return 10


    @classmethod
    def cellwidth(cls):
        """Returns the width of a cell in cm"""
        return 3.822


    @classmethod
    def cellheight(cls):
        """Returns the height of a cell in cm"""
        return 3.875


    @classmethod
    def hascell(cls, row, column):
        """Returns True if a detector of this type has a cell at position
        (row, column) or False if it does not.
        @param row The row in the range [0, nrows)
        @param column The column in the range [0, ncolumns)
        """

        # Check the row and column are in a sensible range
        if row < 0 or row >= cls.nrows() or \
           column < 0 or column >= cls.ncolumns():
            return False

        # Exclude the central hole
        if column < 5 and row > 6 and row < 17:
            return False

        return True


    @classmethod
    def zposition(cls):
        """Returns the z position of the detector surface
        facing the beam in the STAR coordinates, in cm"""
        return 729.7


## Defines geometry of large cells and large-cell detectors
class Large(Base):

    """Large-cell detector geometrical information.
    """

    @classmethod
    def nrows(cls):
        """Returns the number of rows of cells per sub-detector"""
        return 34


    @classmethod
    def ncolumns(cls):
        """Returns the number of columns of cells per sub-detector"""
        return cls.nrows() / 2


    @classmethod
    def ncells(cls):
        return 394


    @classmethod
    def gapsize(cls):
        return 16


    @classmethod
    def cellwidth(cls):
        """Returns the width of a cell in cm"""
        return 5.812


    @classmethod
    def cellheight(cls):
        """Returns the height of a cell in cm"""
        return cls.cellwidth()


    @classmethod
    def hascell(cls, row, column):
        """Returns True if a detector of this type has a cell at position
        (row, column) or False if it does not.
        @param row The row in the range [0, nrows)
        @param column The column in the range [0, ncolumns)
        e.g.
        >>> Large.hascell(0, 0)
        True
        >>> Large.hascell(9, 3)
        False
        """

        # Check the row and column are in a sensible range
        if row < 0 or row >= cls.nrows() or \
           column < 0 or column >= cls.ncolumns():
            return False

        # Exclude the central hole
        if column < 8 and row > 8 and row < 25:
            return False

        # Exclude corners
        # If rows are in the bottom half, recalculate the row number counting
        # down from the top. This is just a trick so we can use the same
        # simple relation for excluding the cell.
        if row < cls.nrows() / 2 - 1:
            row = cls.nrows() - 1 - row

        if column + row > 42:
            return False

        return True


    @classmethod
    def zposition(cls):
        """Returns the z position of the detector surface
        facing the beam in the STAR coordinates, in cm"""
        return 734.1
