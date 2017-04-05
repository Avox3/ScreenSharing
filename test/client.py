import socket
import struct
from Utils import Protocol
from PIL import ImageGrab, Image
from Client import string_to_raw
sock = socket.socket()
sock.connect(("127.0.0.1", 3331))

length_buf = sock.recv(4)
length, = struct.unpack('!I', length_buf)

sock.recv(length)
# img = Image.new('RGB', (1920, 1200))
# img.putdata(string_to_raw(img_data))
# img.save("YEsh.jpeg")
sock.close()
