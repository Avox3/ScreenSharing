import socket
import struct
import time
from Utils import Protocol
from PIL import ImageGrab, Image
sock = socket.socket()
sock.bind(("127.0.0.1", 3331))
sock.listen(1)


data = str(list(Image.open(r'C:\Users\USER\PycharmProjects\DesktopSharing\morning.jpg').getdata()))
length = len(data)
print length

conn, addr = sock.accept()
info = struct.pack('!I', length)
print info
t1 = time.time()
conn.sendall(info)
t2 = time.time()
print "wtf:", t2 - t1
conn.sendall(data)

conn.close()
sock.close()