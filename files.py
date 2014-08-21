import os

"""Handling of input files.

For historical reasons, there are a number of files needed as input
for the programme. These fall into two categories: static "library"
files providing information about the FMS layout, which should not
be modified; and input files with gains and QT bit-shifts, which
may be modified by the user and written as output.

The full list of library files is as follows:
    fmsCellInfoTable.txt
    large_gaincurve_par.txt
    small_gaincurve_par.txt
    leCroyMappingTable.txt

The modifiable files are:
    largeCellGains.txt
    smallCellGains.txt
    qt1_tac.dat
    qt2_tac.dat
    qt3_tac.dat
    qt4_tac.dat
"""

## The names of all the files we write as output
OUTPUT_NAMES = [
    'largeCellGains.txt',   # Voltages, gains
    'smallCellGains.txt',
    'qt1_tac.dat',          # QT bitshifts, pedestals
    'qt2_tac.dat',
    'qt3_tac.dat',
    'qt4_tac.dat',
    'fms_hv_large_north_2_7005.sh', # Script for setting large cell voltages
    'fms_hv_large_north_1_7006.sh',
    'fms_hv_large_south_2_7007.sh',
    'fms_hv_large_south_1_7008.sh',
    'setVoltages.txt'               # Script for setting small cell voltages
]

# Types and names of library files i.e. those not modified by the user
LIB_NAMES = {'CURVE_LARGE' : 'large_gaincurve_par.txt',
             'CURVE_SMALL' : 'small_gaincurve_par.txt',
             'INFO'        : 'fmsCellInfoTable.txt'}

# Types and default names of input files i.e. those modified by the user
INPUT_NAMES = {'GAIN_LARGE' : 'largeCellGains.txt',
               'GAIN_SMALL' : 'smallCellGains.txt',
               'QT1'        : 'qt1_tac.dat',
               'QT2'        : 'qt2_tac.dat',
               'QT3'        : 'qt3_tac.dat',
               'QT4'        : 'qt4_tac.dat'}

class Files:
    """
    Collects full path of all input files required to run the application.
    
    Note the files themselves are not automatically opened.
    use open_file() to open a specific file.
    """
    def __init__(self):
        """Stores the directory paths searched for files.
        
        Paths are listed in order of priority, i.e. a file in more
        than one location will be taken from the directory nearest
        the start of the list.
        
        """
        self.set_paths()
        self.names = {}
        foundall, missing = self.locate_library()
        if not foundall:
            message = 'Could not locate all library files:'
            for i in missing:
                message += ('\n - ' + i + ' not found')
            raise IOError(message)

    def __getitem__(self, filetype):
        """Return the name of the file indexed by 'filetype'."""
        return self.names[filetype]

    def speak(self):
        """Prints each file type and the full path to the file of that type."""
        width = max(len(i) for i in self.names.iterkeys()) + 1
        for i, j in sorted(self.names.iteritems()):
            print i.ljust(width), j
        
    def set_paths(self):
        """Determine the directories to search for input.
        
        The following locations are looked for, in this order:
         - The current directory.
         - <user home>/.fms
         - The directory named via the FMSVOLTAGES environment variable.
        Stores the valid directories as strings in self.paths.
        Therefore the first entry is the directory that should be used.
        
        """
        # Construct the directory names in the order to be searched.
        names = [os.curdir, os.path.expanduser('~/.fms')]
        # If the FMSVOLTAGES environment variable is set add
        # that top directory as well.
        if 'FMSVOLTAGES' in os.environ:
            names.append(os.environ['FMSVOLTAGES'])
        # Check for the existence of each of these are store only those
        # that exist in self.paths.
        self.paths = [path for path in names if os.path.exists(path)]

    def locate(self, name, userpath=None):
        """Returns the full path to the named file.
        
        Searches all possible directories in order of preference.
        Returns the first matching filepath found, otherwise returns None.
        
        """
        # Search only the user-provided path if given, otherwise
        # use the default paths.
        if userpath:
            paths = [userpath]
        else:
            paths = self.paths
        # Expand the full name of the file including path for each search path.
        fullpaths = [os.path.join(path, name) for path in paths]
        # Eliminate non-existant paths.
        exist = [path for path in fullpaths if os.path.exists(path)]
        try:
            # Return the first extant path
            return exist[0]
        except IndexError:
            # In case of an empty list
            return None

    def locate_library(self, path=None):
        """Attempt to locate all the static library files.
        
        If all files are found returns (True, []) and updates self.names.
        Otherwise returns (False, [missing files]) and leaves self.names
        unmodified.
        
        """
        # Determine full paths to all file types
        full = {filetype: self.locate(name, path) for
                filetype, name in LIB_NAMES.iteritems()}
        # Determine which files we found and which file types are absent
        exist = {filetype: name for filetype, name in full.iteritems() if name}
        missing = [filetype for filetype in full.iterkeys()
                   if filetype not in exist]
        if missing:
            return False, missing
        else:
            # Update name dictionary with found paths.
            self.names.update(exist)
            return True, []

    def locate_input(self, path=None):
        """Attempt to locate all the input files.
        
        If all files are found returns (True, []) and updates self.names.
        Otherwise returns (False, [missing files]) and leaves self.names
        unmodified.
        
        """
        # Determine full paths to all file types
        full = {filetype: self.locate(name, path) for
                filetype, name in INPUT_NAMES.iteritems()}
        # Determine which files we found and which file types are absent
        exist = {filetype: name for filetype, name in full.iteritems() if name}
        missing = [filename for filetype, filename in INPUT_NAMES.iteritems()
                   if filetype not in exist]
        if missing:
            return False, missing
        else:
            # Update name dictionary with found paths.
            self.names.update(exist)
            return True, []

    def open_file(self, filetype):
        """Returns a read-only file corresponding to the input file type.
        
        Returns None if the file type is invalid or the file corresponding to
        that type could not be located.
        
        """
        try:
            return open(self[filetype], 'r')
        except IOError as error:
            return None