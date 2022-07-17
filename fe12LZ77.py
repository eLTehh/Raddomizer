'''Modified from: https://github.com/magical/nlzss/blob/master/lzss3.py'''

import sys
from sys import stdin, stdout, stderr, exit
from os import SEEK_SET, SEEK_CUR, SEEK_END
from errno import EPIPE
from struct import pack, unpack


from collections import defaultdict
from operator import itemgetter



__all__ = ('decompress', 'decompress_file', 'decompress_bytes',
           'decompress_overlay', 'DecompressionError')

class DecompressionError(ValueError):
    pass

def bits(byte):
    return ((byte >> 7) & 1,
            (byte >> 6) & 1,
            (byte >> 5) & 1,
            (byte >> 4) & 1,
            (byte >> 3) & 1,
            (byte >> 2) & 1,
            (byte >> 1) & 1,
            (byte) & 1)

def decompress_raw_lzss10(indata, decompressed_size, _overlay=False):
    """Decompress LZSS-compressed bytes. Returns a bytearray."""
    data = bytearray()

    it = iter(indata)

    if _overlay:
        disp_extra = 3
    else:
        disp_extra = 1

    def writebyte(b):
        data.append(b)
    def readbyte():
        return next(it)
    def readshort():
        # big-endian
        a = next(it)
        b = next(it)
        return (a << 8) | b
    def copybyte():
        data.append(next(it))

    while len(data) < decompressed_size:
        b = readbyte()
        flags = bits(b)
        for flag in flags:
            if flag == 0:
                copybyte()
            elif flag == 1:
                sh = readshort()
                count = (sh >> 0xc) + 3
                disp = (sh & 0xfff) + disp_extra

                for _ in range(count):
                    writebyte(data[-disp])
            else:
                raise ValueError(flag)

            if decompressed_size <= len(data):
                break

    if len(data) != decompressed_size:
        raise DecompressionError("decompressed size does not match the expected size")

    return data

def decompress_raw_lzss11(indata, decompressed_size):
    """Decompress LZSS-compressed bytes. Returns a bytearray."""
    data = bytearray()

    it = iter(indata)

    def writebyte(b):
        data.append(b)
    def readbyte():
        return next(it)
    def copybyte():
        data.append(next(it))

    while len(data) < decompressed_size:
        b = readbyte()
        flags = bits(b)
        for flag in flags:
            if flag == 0:
                copybyte()
            elif flag == 1:
                b = readbyte()
                indicator = b >> 4

                if indicator == 0:
                    # 8 bit count, 12 bit disp
                    # indicator is 0, don't need to mask b
                    count = (b << 4)
                    b = readbyte()
                    count += b >> 4
                    count += 0x11
                elif indicator == 1:
                    # 16 bit count, 12 bit disp
                    count = ((b & 0xf) << 12) + (readbyte() << 4)
                    b = readbyte()
                    count += b >> 4
                    count += 0x111
                else:
                    # indicator is count (4 bits), 12 bit disp
                    count = indicator
                    count += 1

                disp = ((b & 0xf) << 8) + readbyte()
                disp += 1

                try:
                    for _ in range(count):
                        writebyte(data[-disp])
                except IndexError:
                    raise Exception(count, disp, len(data), sum(1 for x in it) )
            else:
                raise ValueError(flag)

            if decompressed_size <= len(data):
                break

    if len(data) != decompressed_size:
        raise DecompressionError("decompressed size does not match the expected size")

    return data


def decompress_overlay(f, out):
    # the compression header is at the end of the file
    f.seek(-8, SEEK_END)
    header = f.read(8)

    # decompression goes backwards.
    # end < here < start

    # end_delta == here - decompression end address
    # start_delta == decompression start address - here
    end_delta, start_delta = unpack("<LL", header)

    filelen = f.tell()

    padding = end_delta >> 0x18
    end_delta &= 0xFFFFFF
    decompressed_size = start_delta + end_delta

    f.seek(-end_delta, SEEK_END)

    data = bytearray()
    data.extend(f.read(end_delta - padding))
    data.reverse()

    #stdout.write(data.tostring())

    uncompressed_data = decompress_raw_lzss10(data, decompressed_size,
                                              _overlay=True)
    uncompressed_data.reverse()

    # first we write up to the portion of the file which was "overwritten" by
    # the decompressed data, then the decompressed data itself.
    # i wonder if it's possible for decompression to overtake the compressed
    # data, so that the decompression code is reading its own output...
    f.seek(0, SEEK_SET)
    out.write(f.read(filelen - end_delta))
    out.write(uncompressed_data)

def decompress(obj):
    """Decompress LZSS-compressed bytes or a file-like object.
    Shells out to decompress_file() or decompress_bytes() depending on
    whether or not the passed-in object has a 'read' attribute or not.
    Returns a bytearray."""
    if hasattr(obj, 'read'):
        return decompress_file(obj)
    else:
        return decompress_bytes(obj)

def decompress_bytes(data):
    """Decompress LZSS-compressed bytes. Returns a bytearray."""
    header = data[:4]
    if header[0] == 0x10:
        decompress_raw = decompress_raw_lzss10
    elif header[0] == 0x11:
        decompress_raw = decompress_raw_lzss11
    else:
        raise DecompressionError("not as lzss-compressed file")

    decompressed_size, = unpack("<L", header[1:] + b'\x00')

    data = data[4:]
    return decompress_raw(data, decompressed_size)

def decompress_file(input, outputpath = None):
    """Decompress an LZSS-compressed file. Returns a bytearray.
    This isn't any more efficient than decompress_bytes, as it reads
    the entire file into memory. It is offered as a convenience.
    """
    #header = f.read(4)
    header = input[0:4]
    if header[0] == 0x10:
        decompress_raw = decompress_raw_lzss10
    elif header[0] == 0x11:
        decompress_raw = decompress_raw_lzss11
    else:
        raise DecompressionError("not as lzss-compressed file")

    decompressed_size, = unpack("<L", header[1:] + b'\x00')

    data = input[4:]

    decompOutput = decompress_raw(data, decompressed_size)

    if outputpath:
        toWrite = open(outputpath, "wb")
        toWrite.write(decompOutput)

    return decompOutput


class SlidingWindow:
    # The size of the sliding window
    size = 4096

    # The minimum displacement.
    disp_min = 2

    # The hard minimum — a disp less than this can't be represented in the
    # compressed stream.
    disp_start = 1

    # The minimum length for a successful match in the window
    match_min = 1

    # The maximum length of a successful match, inclusive.
    match_max = None

    def __init__(self, buf):
        self.data = buf
        self.hash = defaultdict(list)
        self.full = False

        self.start = 0
        self.stop = 0
        #self.index = self.disp_min - 1
        self.index = 0

        assert self.match_max is not None

    def next(self):
        if self.index < self.disp_start - 1:
            self.index += 1
            return

        if self.full:
            olditem = self.data[self.start]
            assert self.hash[olditem][0] == self.start
            self.hash[olditem].pop(0)

        item = self.data[self.stop]
        self.hash[item].append(self.stop)
        self.stop += 1
        self.index += 1

        if self.full:
            self.start += 1
        else:
            if self.size <= self.stop:
                self.full = True

    def advance(self, n=1):
        """Advance the window by n bytes"""
        for _ in range(n):
            self.next()

    def search(self):
        match_max = self.match_max
        match_min = self.match_min

        counts = []
        indices = self.hash[self.data[self.index]]
        for i in indices:
            matchlen = self.match(i, self.index)
            if matchlen >= match_min:
                disp = self.index - i
                #assert self.index - disp >= 0
                #assert self.disp_min <= disp < self.size + self.disp_min
                if self.disp_min <= disp:
                    counts.append((matchlen, -disp))
                    if matchlen >= match_max:
                        #assert matchlen == match_max
                        return counts[-1]

        if counts:
            match = max(counts, key=itemgetter(0))
            return match

        return None

    def match(self, start, bufstart):
        size = self.index - start

        if size == 0:
            return 0

        matchlen = 0
        it = range(min(len(self.data) - bufstart, self.match_max))
        for i in it:
            if self.data[start + (i % size)] == self.data[bufstart + i]:
                matchlen += 1
            else:
                break
        return matchlen

class NLZ10Window(SlidingWindow):
    size = 4096

    match_min = 3
    match_max = 3 + 0xf

class NLZ11Window(SlidingWindow):
    size = 4096

    match_min = 3
    match_max = 0x111 + 0xFFFF

class NOverlayWindow(NLZ10Window):
    disp_min = 3

def _compress(input, windowclass=NLZ10Window):
    """Generates a stream of tokens. Either a byte (int) or a tuple of (count,
    displacement)."""

    window = windowclass(input)

    i = 0
    while True:
        if len(input) <= i:
            break
        match = window.search()
        if match:
            yield match
            #if match[1] == -283:
            #    raise Exception(match, i)
            window.advance(match[0])
            i += match[0]
        else:
            yield input[i]
            window.next()
            i += 1

def packflags(flags):
    n = 0
    for i in range(8):
        n <<= 1
        try:
            if flags[i]:
                n |= 1
        except IndexError:
            pass
    return n

def chunkit(it, n):
    buf = []
    for x in it:
        buf.append(x)
        if n <= len(buf):
            yield buf
            buf = []
    if buf:
        yield buf

def compress(input, out):
    # header
    out.write(pack("<L", (len(input) << 8) + 0x10))

    # body
    length = 0
    for tokens in chunkit(_compress(input), 8):
        flags = [type(t) == tuple for t in tokens]
        out.write(pack(">B", packflags(flags)))

        for t in tokens:
            if type(t) == tuple:
                count, disp = t
                count -= 3
                disp = (-disp) - 1
                assert 0 <= disp < 4096
                sh = (count << 12) | disp
                out.write(pack(">H", sh))
            else:
                out.write(pack(">B", t))

        length += 1
        length += sum(2 if f else 1 for f in flags)

    # padding
    padding = 4 - (length % 4 or 4)
    if padding:
        out.write(b'\xff' * padding)

def compress_nlz11(input, out):
    # header
    out.write(pack("<L", (len(input) << 8) + 0x11))

    # body
    length = 0
    for tokens in chunkit(_compress(input, windowclass=NLZ11Window), 8):
        flags = [type(t) == tuple for t in tokens]
        out.write(pack(">B", packflags(flags)))
        length += 1

        for t in tokens:
            if type(t) == tuple:
                count, disp = t
                disp = (-disp) - 1
                #if disp == 282:
                #    raise Exception
                assert 0 <= disp <= 0xFFF
                if count <= 1 + 0xF:
                    count -= 1
                    assert 2 <= count <= 0xF
                    sh = (count << 12) | disp
                    out.write(pack(">H", sh))
                    length += 2
                elif count <= 0x11 + 0xFF:
                    count -= 0x11
                    assert 0 <= count <= 0xFF
                    b = count >> 4
                    sh = ((count & 0xF) << 12) | disp
                    out.write(pack(">BH", b, sh))
                    length += 3
                elif count <= 0x111 + 0xFFFF:
                    count -= 0x111
                    assert 0 <= count <= 0xFFFF
                    l = (1 << 28) | (count << 12) | disp
                    out.write(pack(">L", l))
                    length += 4
                else:
                    raise ValueError(count)
            else:
                out.write(pack(">B", t))
                length += 1

    # padding
    padding = 4 - (length % 4 or 4)
    if padding:
        out.write(b'\xff' * padding)

def dump_compress_nlz11(input, out):
    # body
    length = 0
    def dump():
        for t in _compress(input, windowclass=NLZ11Window):
            if type(t) == tuple:
                yield t
    from pprint import pprint
    pprint(list(dump()))


#def stripHeader(input_path):
#    input_file = bytearray(open(input_path, 'rb').read())
#    return (input_file[0:4],input_file[4:])

def fe12_compress(input_path, output_path):
    compress(open(input_path, 'rb').read(), open(output_path, 'wb'))

def fe12_decompress(input_path, output_path):
    decompress_file(open(input_path, 'rb').read(), output_path)



#Example
'''
#Strip header, keep this data for later
#Index 0 is the header, 1 is the data
headerData = stripHeader("C:\\Users\\lt123\\stoof\\coding\\awakening randomizer\\static.bin.lz")

#Decompress file using LZ11 algorithm
decompress_file(headerData[1], "C:\\Users\\lt123\\stoof\\coding\\awakening randomizer\\static.bin.lz.awakening")

#Compress file back with decompressed file!
awakening_compress(headerData[0], 
"C:\\Users\\lt123\\stoof\\coding\\awakening randomizer\\static.bin.lz.awakening", 
"C:\\Users\\lt123\\stoof\\coding\\awakening randomizer\\static.bin.lz")
'''

