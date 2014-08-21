#!/usr/bin/env python

'''
1   1  0  0 3 11 2 6 7005 -1 14  6
'''
import sys

class InfoLine:
    def __init__(self, string):
        self.det, self.ch, self.row, self.col, self.qtcr, self.qtslot,\
        self.qtcard, self.qtch, self.id1, self.id2, self.id3, self.id4\
        = [i for i in string.split()]
        self.det, self.ch = int(self.det), int(self.ch) #For sorting
        self.qtslot = int(self.qtslot)
        if self.qtslot == 12:
            self.qtslot = 11

    def to_string(self):
        return '{}{:>4}{:>3}{:>3}{:>2}{:>3}{:>2}{:>2}{:>5}{:>3}{:>3}{:>3}'.format(
        self.det, self.ch, self.row, self.col,
        self.qtcr, self.qtslot, self.qtcard, self.qtch,
        self.id1, self.id2, self.id3,
        self.id4)


class MapLine:
    def __init__(self, string):
        self.det, self.ch, self.qtcr, self.qtslot, self.qtch = [i for i in string.split()]
        self.det, self.ch = int(self.det), int(self.ch) #For sorting
        self.det -= 7
        self.qtslot = int(self.qtslot)
        if self.qtslot == 12:
            self.qtslot = 11

    '''11 288 2  3 31'''
    def to_string(self):
        return '{:>2}{:>4}{:>2}{:>3}{:>3}'.format(self.det, self.ch,
            self.qtcr, self.qtslot, self.qtch)

if __name__ == '__main__':
    with open(sys.argv[1]) as file:
        text = file.read().splitlines()
    lines = [InfoLine(l) for l in text]
    linedict = {(l.det, l.ch): l for l in lines}
    with open(sys.argv[2]) as file:
        text = file.read().splitlines()
    lines = [MapLine(l) for l in text]
    mapdict = {(l.det, l.ch): l for l in lines}
    # substitute
    for ch, info in mapdict.iteritems():
        try:
            print ch
            channel = linedict[ch]
            channel.qtcr = info.qtcr
            channel.qtslot = info.qtslot
            qtch = int(info.qtch)
            channel.qtcard = qtch / 8
            channel.qtch = qtch % 8
        except KeyError:
            #print 'key error for detector', ch[0], 'channel', ch[1]
            pass
    with open(sys.argv[3], 'w') as file:
        for n, l in sorted(linedict.iteritems()):
            file.write(l.to_string() + '\n')
