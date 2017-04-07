# -*- coding: utf-8 -*-
import Tkinter as tk
from PIL import ImageTk
import socket
from PIL import Image
import json
import threading
from Utils import Protocol, raw_data_to_img, string_to_raw


SERVER_IP = '127.0.0.1'  # address of the server
PORT = 3337  # the port
BUFFER = 8196  # memory storage size
# message modes
INITIALIZE, QUIT_REQUEST, ROW_SECTIONS_LENGTH, SENDING_IMAGE = range(4)


class TkinterFrame(threading.Thread):
    def __init__(self, width, height):
        threading.Thread.__init__(self)

        self.width = width
        self.height = height
        self.status = True
        self.root = tk.Tk()
        self.root.title('DesktopSharing')
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        # make the root window the size of the image
        self.root.geometry("%dx%d+%d+%d" % (width, height, 0, 0))

        self.canvas = tk.Canvas(self.root, width=self.root.winfo_width(), height=self.root.winfo_height())
        self.photo = None
        # self.canvas.bind('<Configure>', self.resize)
        self.canvas.pack(fill=tk.BOTH, expand=1)

        # root has no image argument, so use a label as a panel
        self.start()

    def resize(self):
        width, height = self.root.winfo_width(), self.root.winfo_height()
        self.canvas.config(width=width, height=height)

    def callback(self):
        self.root.quit()

    def run(self):
        self.root.mainloop()

    def update_image(self):

        if self.photo:
            self.canvas.create_image(400, 400, image=self.photo)


class User(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(self)
        # create socket and connect to server
        self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_socket.connect((SERVER_IP, PORT))
        self.protocol = Protocol(self.conn_socket)

        self.user_id = -1
        self.__width = -1
        self.__height = -1
        self.__section_x = -1
        self.__section_y = -1
        self.img_mode = -1

        self.curr_section = -1
        self.canvas_data = None
        self.gui = None
        self.sections = []
        self.sections_length = -1

        self.initialize()

    def send(self, msg_type):
        json_string = json.dumps({"UserID": self.user_id, "Status": msg_type})
        self.protocol.send_one_message(json_string)

    def initialize(self):
        self.send(INITIALIZE)

    def valid_receivied_msg(self, data):
        """

        :param data:
        :return:
        """

        if data:  # not empty string
            try:
                data = json.loads(data)
                return data  # data is jsonable
            except ValueError:
                return None  # data isn't jsonable
        else:
            return None

    def run(self):
        while True:
            data = self.protocol.recv_one_message()
            data = self.valid_receivied_msg(data)

            if not data:
                continue

            self.data_handling(data)

    def data_handling(self, data):

        msg_status = int(data['Status'])
        section = data.get('Section')

        if msg_status == INITIALIZE:
            print 'Initialized'
            self.user_id = data["UserID"]
            self.__width = data["ScreenWidth"]
            self.__height = data["ScreenHeight"]
            self.__section_x = data["SectionX"]
            self.__section_y = data["SectionY"]
            self.img_mode = data["ImageMode"]
            self.gui = TkinterFrame(self.__width, self.__height)
            self.sections = [None] * (self.__section_x * self.__section_y)

        elif msg_status == QUIT_REQUEST:
            self.close()
            return

        elif msg_status == ROW_SECTIONS_LENGTH:
            self.sections_length = int(data['SectionsLength'])

        elif msg_status == SENDING_IMAGE:
            self.curr_section = section
            self.sections[section] = raw_data_to_img(string_to_raw(self.protocol.recv_one_message()),
                                                     self.__width / self.__section_x, self.__height / self.__section_y)

            self.sections_length -= 1

            if self.sections_length == 0:
                self.create_img()
                self.sections_length = -1

    def create_img(self):

        new_img = Image.new(self.img_mode, (self.__width, self.__height))

        end_x = self.__width / self.__section_x
        end_y = self.__height / self.__section_y

        for x in xrange(self.__section_x):
            for y in xrange(self.__section_y):

                start_x = x * (self.__width / self.__section_x)
                start_y = y * (self.__height / self.__section_y)
                new_img.paste(self.sections[x * self.__section_x + y],
                              (start_x, start_y, start_x + end_x, start_y + end_y))
        self.gui.photo = ImageTk.PhotoImage(new_img)
        self.gui.update_image()

    def close(self):
        """ Quit from the connection - close the socket. """
        self.conn_socket.close()  # close socket

if __name__ == '__main__':
    User().start()
