import struct
import time
import socket


class Protocol(object):
    def __init__(self, sock):
        self.sock = sock

    def send_one_message(self, data, print_time=False):
        length = len(data)
        info = struct.pack('!I', length)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.sendall(info)

        t1 = time.time()
        self.sock.sendall(data)
        t2 = time.time()
        if print_time:
            print 'wtf:', t2 - t1


        #
        # split_length = 1000000
        # while length:
        #     if length < split_length:
        #         self.sock.sendall(data)
        #         length = 0
        #     else:
        #         self.sock.sendall(data[:split_length])
        #         data = data[split_length:]
        #         length -= split_length

    def recv_one_message(self):
        length_buf = self.sock.recv(4)
        if not length_buf:
            return None
        length = struct.unpack('!I', length_buf)[0]
        return self.recvall(length)

    def recvall(self, count):
        buf = b''
        while count:
            new_buf = self.sock.recv(count)
            if not new_buf:
                return None
            buf += new_buf
            count -= len(new_buf)
        return buf
