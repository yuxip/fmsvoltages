"""ROOT tree generation utilities."""

import ROOT
# Only operate ROOT in batch mode to avoid some crashes I experienced on
# RCF when using the programme over ssh.
ROOT.gROOT.SetBatch(True)
# May give to speed up on ROOT calls.
ROOT.SetSignalPolicy(ROOT.kSignalFast)

# We only want one tree to be in existence, so keep it as a module-level
# variable to create a sort-of-singleton.
__tree = None
__entry = None

def create():
    """Creates and initialises a ROOT tree with voltage information."""
    # Run user logon script if it can be identified.
    logon = ROOT.gEnv.GetValue('Rint.Logon', '')
    if logon:
        ROOT.gROOT.Macro(logon)
    global __tree, __entry
    # We need to do some ROOT-shenanigans to be able to make a tree in Python.
    # Define a C struct with the branches we want to store in the tree
    # and process it with ROOT.
    ROOT.gROOT.ProcessLine(\
        "struct MyFmsVoltagesStruct {\
        Double_t eta;\
        Double_t oldGain;\
        Double_t newGain;\
        Double_t askedChange;\
        Double_t p0;\
        Double_t p1;\
        Double_t p2;\
        Int_t detector;\
        Int_t channel;\
        Int_t row;\
        Int_t column;\
        Int_t oldVoltage;\
        Int_t newVoltage;\
        Int_t oldBitshift;\
        Int_t newBitshift;\
        Int_t qtCrate;\
        Int_t qtBoard;\
        Int_t qtChannel;\
        };"\
    )
    __entry = ROOT.MyFmsVoltagesStruct()
    __tree = ROOT.TTree('cells', 'cells')
    # Explicitly make the tree memory-resident.
    __tree.SetDirectory(0)
    # TTree.Branch() needs a "leaflist" with all variable names.
    # The leaflist needs to have the type appended after each element name:
    # "/I" for integers and "/D" for doubles. Create them separately for all the
    # doubles and all the integers then concatenate for TTree::Branch().
    # Note that order is important here!
    doubles = ['eta', 'oldGain', 'newGain', 'askedChange', 'p0', 'p1', 'p2']
    integers = ['detector', 'channel', 'row', 'column', 'oldVoltage',
                'newVoltage', 'oldBitshift', 'newBitshift', 'qtCrate',
                'qtBoard', 'qtChannel']
    doubles_list = ':'.join([i + '/D' for i in doubles])
    integers_list = ':'.join([i + '/I' for i in integers])
    __tree.Branch('eta', ROOT.AddressOf(__entry, 'eta'),
                ':'.join([doubles_list, integers_list]))
    
def populate(before, after):
    """Populate the tree from two sets of detectors.
    
    The 'before' set represent the detector before modifications and
    the 'after' set represent the detector after modifications.
    
    """
    if not __tree: # On the first call create the tree
        create()
    __tree.Reset() # Clear contents from previous call to populate()
    # Loop over detectors
    for old, new in zip(before, after):
        # Loop over cells in this detector
        for i, j in zip(old.cells, new.cells):
            # Set each value.
            __entry.detector = i.detector
            __entry.channel  = i.channel
            __entry.row      = i.row
            __entry.column   = i.column
            __entry.eta      = i.pseudorapidity()
            __entry.oldGain  = i.gain
            __entry.newGain  = j.gain
            __entry.oldVoltage = i.voltage
            __entry.newVoltage  = j.voltage
            __entry.oldBitshift = i.qt.bitshift
            __entry.newBitshift = j.qt.bitshift
            __entry.qtCrate = j.qt.crate
            __entry.qtBoard = j.qt.board
            __entry.qtChannel = j.qt.number
            __entry.p0, __entry.p1, __entry.p2 = j.calibration.p
            # The cell may have had a "requested_correction" set somewhere.
            if hasattr(j, 'requested_correction'):
                __entry.askedChange = j.requested_correction
            else:
                __entry.askedChange = 0.
            __tree.Fill()

def tree():
    """Returns the current tree."""
    global __tree
    return __tree

def write(name):
    """Create a ROOT tree with 'before' and 'after' cell properties.
    
    Write the tree with name 'cells' to a named ROOT file.
    @param name   The name of the ROOT file to create.
    @param before A list of detector.Detector objects before changes
    @param after  A list of detector.Detector objects after changes
    There should be a one-to-one correspondence between elements in before and
    after.
    
    """
    if __tree:
        file = ROOT.TFile(name, 'RECREATE')
        __tree.Write()
