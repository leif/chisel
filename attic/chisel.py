#!/usr/bin/env python
"""
>>> from fs.memoryfs import MemoryFS
>>> c = Chisel( MemoryFS() )
>>> c.put( 'a', 0 )
>>> c.put( 'b', 2**32 - 1 )
>>> list( c.get( 255, 2**32 - 257 ) )
['a']
>>> list( c.get( 256,  2**32 - 256 ) )
['b']
>>> list( sorted( c.get( 255, 2**32 - 256 ) ) )
['a', 'b']
>>> c.put( 'c', 2**32 )
Traceback (most recent call last):
    ...
AssertionError: time out of bounds: 4294967296
>>> tuple(sorted( c._walkDirs( 0 , 2**32 )))
(u'/00/00/00', u'/ff/ff/ff')
>>> tuple(c._walkDirs( 256, 2**32 ))
(u'/ff/ff/ff',)
>>> tuple(c._walkDirs( 0 , 2**32 - 257 ))
(u'/00/00/00',)
>>> print "\\n".join( sorted( map("/".join, c.walkFiles( 0, 2**32) ) ) )
/00/00/00/ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb
/ff/ff/ff/3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d
"""

__author__    = "Leif Ryge <leif@synthesize.us>"
__copyright__ = "Public Domain, 2013"

import os
import sys
import time
import doctest
from hashlib import sha256

class Chisel(object):

    def __init__( self, fs ):
        self._fs = fs

    @classmethod
    def _hash( cls, data ): return sha256( data ).hexdigest()

    @classmethod
    def _makeDirPathFromTime( cls, timeT ):
        s = "%.8x" % (timeT,)
        return "/%s/%s/%s" % ( s[:2], s[2:4], s[4:6] )

    def _walkDirs( self, queryStart, queryEnd, depth=0, parentStart=0, prefix='' ):
        if depth == 3:
            yield prefix
        else:
            scale = 24 - depth*8
            for d in sorted( self._fs.listdir( prefix ) ):
                byte = int( d, 16 )
                assert 0 <= byte < 256
                dirStart = parentStart + (byte << scale)
                dirEnd   = dirStart + 2**scale - 1
                if dirStart <= queryStart <= dirEnd or \
                   dirStart <= queryEnd   <= dirEnd or \
                   (queryStart < dirStart and dirEnd < queryEnd):
                    for p in self._walkDirs( queryStart, queryEnd, depth+1, dirStart, "%s/%s" %(prefix, d) ):
                        yield p

    def walkFiles( self, startTime = 0, endTime = None, uniq = True ):
        seen = set()
        if endTime is None:
            endTime = time.time()
        for dirPath in self._walkDirs( startTime, endTime ):
            for filename in self._fs.listdir( dirPath ):
                if uniq:
                    if filename in seen:
                        continue
                    else:
                        seen.add( filename )
                yield ( dirPath, filename )

    def has( self, name, startTime, endTime = None ):
        for dirPath, filename in self.walkFiles( startTime, endTime ):
            if filename == name:
                return True
        return False

    def get( self, startTime = 0, endTime = None, uniq = True ):
        for dirPath, filename in self.walkFiles( startTime, endTime, uniq ):
            yield self._fs.getcontents( "%s/%s" % (dirPath, filename) )

    def put( self, data, timeT = None, span=256 ):
        if timeT is None:
            timeT = time.time()
        assert 0 <= timeT < 2**32, "time out of bounds: %d" % (timeT,)
        filename = self._hash( data )
        if not self.has( filename, timeT - span, timeT ):
            dirPath  = self._makeDirPathFromTime( timeT )
            filePath = "%s/%s" % ( dirPath, filename )
            if not self._fs.isdir( dirPath ):
                self._fs.makedir( dirPath, recursive = True )
            self._fs.setcontents( filePath, data )

    def sync( self, remote, stateFile = None ):
        "this part isn't tested yet"
        count, new = 0,0
        for dirPath, filename in remote.walkFiles():
            count += 1
            if not self.has( filename, 0 ):
                new += 1
                self.put( remote._fs.getcontents( "%s/%s" % (dirPath, filename) ) )
        print "Saw %s files; copied %s that are new" % (count, new)

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print "usage: %s [put|ls|cat|test]" % os.path.basename( sys.argv[0] )
    else:
        cmd = sys.argv[1]
        if cmd == 'test':
            print doctest.testmod( )
        else:
            from fs.opener import opener
            chisel = Chisel( opener.opendir( sys.argv[2] ) )
            if cmd == 'put':
                chisel.put( sys.stdin.read(), *map(int, sys.argv[3:]) )
            elif cmd == 'ls':
                print "\n".join( "%s/%s" % (a,b) for a,b in chisel.walkFiles( *map(int, sys.argv[3:]) ) ),
            elif cmd == 'cat':
                print "".join( chisel.get( *map(int, sys.argv[3:]) ) ),
            elif cmd == 'sync':
                chisel.sync( Chisel( opener.opendir( sys.argv[3] ) ), *map(int, sys.argv[4:]) )
            else:
                print "unknown command %s" % (cmd,)

