import ImageTk
from PIL import ImageGrab
from Tkinter import *


class ImageTransfer:

    def __init__(self, socket_obj):
        self.socket_obj = socket_obj

    def screenshot(self, path):
        im = ImageGrab.grab()
        im.save(path)
        return path

    def receive_image(self, path):

        image = open(path, 'wb+')

        while True:

            data = self.socket_obj.recv(1024)
            if data:
                image.write(data)
            else:
                # Image successfully transferred
                print 'work'
                image.close()
                break

    def send_image(self, path):

        image = open(self.screenshot(path), 'rb')
        data = image.read()
        image.close()

        self.socket_obj.sendall(data)
        self.socket_obj.close()


def main():
    from PIL import Image
    import socket

    server_socket = socket.socket()
    server_socket.bind(('127.0.0.1', 8200))

    server_socket.listen(1)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 8200))

    (conn, add) = server_socket.accept()

    ImageTransfer(s).send_image(r'C:\Users\USER\Desktop\to_send_screenshot.png')
    ImageTransfer(conn).receive_image(r'C:\Users\USER\Desktop\to_recv_screenshot.png')

    s.close()
    conn.close()
    server_socket.close()

    root = Tk()
    img = ImageTk.PhotoImage(Image.open(r'C:\Users\USER\Desktop\to_recv_screenshot.png'))
    panel = Label(root, image=img)
    panel.pack()
    root.mainloop()
main()
