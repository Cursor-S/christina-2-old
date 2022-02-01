import socket
import struct
import ujson
import time
from dns import resolver

class StatusPing:
    def __init__(self, host="localhost", timeout=5):
        if ":" in host:
            self._host = host.split(":")[0]
            self._port = int(host.split(":")[1])
        else:
            ans = resolver.resolve(f"_minecraft._tcp.{host}", "SRV")
            for i in ans.response.answer:
                ans = str(i).split(" ")
            self._host = ans[-1].rstrip(".")
            self._port = int(ans[-2])
        self._timeout = timeout

    def unpack_varint(self, sock):
        data = 0
        for i in range(5):
            ordinal = sock.recv(1)
            if len(ordinal) == 0:
                break
            byte = ord(ordinal)
            data |= (byte & 0x7F) << 7 * i
            if not byte & 0x80:
                break
        return data

    def pack_varint(self, data):
        ordinal = b""
        while True:
            byte = data & 0x7F
            data >>= 7
            ordinal += struct.pack("B", byte | (0x80 if data > 0 else 0))
            if data == 0:
                break
        return ordinal

    def pack_data(self, data):
        if type(data) is str:
            data = data.encode("utf8")
            return self.pack_varint(len(data)) + data
        elif type(data) is int:
            return struct.pack("H", data)
        elif type(data) is float:
            return struct.pack("Q", int(data))
        else:
            return data

    def send_data(self, connection, *args):
        data = b""
        for arg in args:
            data += self.pack_data(arg)

        connection.send(self.pack_varint(len(data)) + data)

    def read_fully(self, connection, extra_varint=False):
        packet_length = self.unpack_varint(connection)
        packet_id = self.unpack_varint(connection)
        byte = b""
        if extra_varint:
            if packet_id > packet_length:
                self.unpack_varint(connection)
            extra_length = self.unpack_varint(connection)
            while len(byte) < extra_length:
                byte += connection.recv(extra_length)
        else:
            byte = connection.recv(packet_length)
        return byte

    def get_status(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.settimeout(self._timeout)
            connection.connect((self._host, self._port))
            self.send_data(connection, b"\x00\x00",
                            self._host, self._port, b"\x01")
            self.send_data(connection, b"\x00")
            data = self.read_fully(connection, extra_varint=True)
            self.send_data(connection, b"\x01", time.time() * 1000)
            tstamp = self.read_fully(connection)

        resp = ujson.loads(data.decode("utf8"))
        resp["ping"] = int(time.time() * 1000) - \
            struct.unpack("Q", tstamp)[0]

        return resp
