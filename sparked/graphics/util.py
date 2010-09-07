# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Utility functions for graphics.
"""

def parseColor(x):
    """
    Given a string in hexadecimal RGB notation, return a (r,g,b) triplet where r,g,b in 0 >= x > 256
    """
    if len(x) not in [3,4,6,7]:
        return False
    if x[0] == "#":
        x = x[1:]
    if len(x) == 3:
        x = x[0]+x[0]+x[1]+x[1]+x[2]+x[2]

    col = []
    for i in range(3):
        col.append(int(x[i*2:i*2+2], 16)/256)
    return tuple(col)
