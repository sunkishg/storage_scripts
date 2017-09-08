#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from math import ceil

class Cal(object):
    """
    Execute the command using matc.ceil:
    :Usage: "Cal(SI Unit,frmsize='b', tosize='g', bsize=1024)", by default converts bytes into GB
    :param siunit: SI Unit size
    :param frmsize: SI Unit source format, default 'bytes'
    :param tosize:  SI Unit target format, default 'GB'
    :return: returns converted SI Unit value, returns 0.0 if a nonnumaric value provided
    """

    def __init__(self,siunit, frmsize='b', tosize='g', bsize=1024):
        super(Cal, self).__init__()
        self.siunit = siunit.strip()
        self.frmsize = frmsize.strip()
        self.tosize = tosize.strip()
        self.bsize = bsize

    def convert_units(self):
        # convert bytes to MB, GB, TB etc.
        system_units = {'b':0, 'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}

        self.source = system_units[self.frmsize]
        self.target = system_units[self.tosize]
        self.convert_unit = self.target - self.source

        try:
            self.myunit = float(self.siunit)
        except Exception as e:
            self.myunit = 0.0
            print("SI Unit Conversion error: {0}".format(e))

        self.outsize = ceil((self.myunit / (self.bsize ** self.convert_unit)) *100) / 100
        return (self.outsize)

def main():
    print(Cal.__doc__)
    unit = input("Enter Values:")
    x = Cal(unit).convert_units()
    print(type(x))

if __name__ == '__main__':
    main()