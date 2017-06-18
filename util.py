from struct import pack, unpack_from, calcsize

class DataBuffer(object):

    def __init__(self, data=bytes(), offset=0):
        self._data = data
        self._offset = offset

    @property
    def data(self):
        return self._data

    @property
    def offset(self):
        return self._offset

    @property
    def remaining(self):
        return self._data[self._offset:]

    def write(self, data):
        if not len(data):
            return

        self._data += data

    def writeTo(self, fmt, *args):
        self.write(pack('!%s' % fmt, *args))

    def read(self, length):
        data = self._data[self._offset:][:length]
        self._offset += length
        return data

    def clear(self):
        self._data = bytes()
        self._offset = 0

    def readFrom(self, fmt):
        data = unpack_from('!%s' % fmt, self._data, self._offset)
        self._offset += calcsize('!%s' % fmt)
        return data

    def readByte(self):
        return self.readFrom('B')[0]

    def writeByte(self, value):
        self.writeTo('B', int(value))

    def readSByte(self):
        return self.readFrom('b')[0]

    def writeSByte(self, value):
        self.writeTo('b', int(value))

    def readShort(self):
        return self.readFrom('h')[0]

    def writeShort(self, value):
        self.writeTo('h', int(value))

PACKET_REQUEST_SPAWN = 0x00
PACKET_SPAWN = 0x01
PACKET_DESPAWN = 0x02
PACKET_POSITION_UPDATE = 0x03

# a list of random chosen spawn points around the map
spawn_positions = [
    [100, 100],
    [200, 200],
    [300, 300],
    [400, 400]
]
