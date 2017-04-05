# -*- coding: utf-8 -*-
import re
import Tkinter as tk
from PIL import ImageTk
import socket
import sys
from PIL import Image
import pygame
import json
import threading
from Utils import Protocol


SERVER_IP = '127.0.0.1'  # address of the server
PORT = 3337  # the port
BUFFER = 8196  # memory storage size
# message modes
INITIALIZE, QUIT_REQUEST, CUR_IMG_OPEN_BUILDING, CUR_IMG_DONE_BUILDING, LAST_IMG_DONE, CUR_IMG_MID_BUILDING = range(6)
STOP_IMAGE_LOOP = 'STOP PLEASE'


def string_to_raw(data_list):
    """ this func convert image data to list of tuples - raw data """
    data = re.findall(r'(?:\d+,\s){2}\d+', data_list)
    return [tuple([int(y) for y in x.split(', ')]) for x in data]


class Gui(threading.Thread):
    def __init__(self, screen_width, screen_height):
        threading.Thread.__init__(self)

        self.white = (255, 255, 255)
        self.img = None

        # initialize screen
        pygame.init()
        pygame.display.set_caption('Basic Screen Sharing Program')

        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.screen.fill(self.white)
        self.clock = pygame.time.Clock()
        pygame.display.flip()

        self.running = True

    def run(self):
        while self.running:
            self.screen.fill(self.white)
            if self.img:
                self.screen.blit(self.img, (0, 0))

            pygame.event.get()
            pygame.display.flip()
            self.clock.tick(60)

    def update(self, img):

        mode = img.mode
        size = img.size
        data = img.tobytes()

        self.img = pygame.image.fromstring(data, size, mode)


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

    def resize(self, event):
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
        self.counter = 0
        self.canvas_data = None
        self.gui = None
        self.sections = []
        self.last_section = -1

        self.initialize()

    def send(self, msg_type):
        json_string = json.dumps({"UserID": self.user_id, "Status": msg_type})
        self.protocol.send_one_message(json_string)

    def initialize(self):
        self.send(INITIALIZE)

    def run(self):
        self.counter = 0
        while True:
            data = self.protocol.recv_one_message()
            self.counter += 1
            loop_image = self.data_handling(data)
            if loop_image:
                data = self.protocol.recv_one_message()

                new_img = Image.new(self.img_mode, (self.__width / self.__section_x,
                                                    self.__height / self.__section_y))
                new_img.putdata(string_to_raw(data))
                self.sections[self.curr_section] = new_img
                if self.curr_section == self.last_section:
                    self.create_img()
                self.curr_section = -1

    def data_handling(self, data):
        if not data:
            return None
        print data[:50]
        data = json.loads(data)
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
            self.sections = [''] * (self.__section_x * self.__section_y)

        elif msg_status == QUIT_REQUEST:
            # TODO - complete
            pass

        # extracting data
        elif msg_status == CUR_IMG_OPEN_BUILDING:
            self.curr_section = section
            self.sections[section] = ''
            self.last_section = data.get('Section')
            return True

        elif msg_status == LAST_IMG_DONE:
            print "last count:", self.counter
            self.create_img()

    def create_img(self):

        new_img = Image.new(self.img_mode, (self.__width, self.__height))

        end_x = self.__width / self.__section_x
        end_y = self.__height / self.__section_y

        for x in xrange(self.__section_x):
            for y in xrange(self.__section_y):

                start_x = x * (self.__width / self.__section_x)
                start_y = y * (self.__height / self.__section_y)
                new_img.paste(self.sections[x * self.__section_x + y].getdata(),
                              (start_x, start_y, start_x + end_x, start_y + end_y))
        self.gui.photo = ImageTk.PhotoImage(new_img)
        self.gui.update_image()

    def close(self):
        """ quit from the chat and close socket & program """
        self.send(QUIT_REQUEST)
        self.conn_socket.close()  # close socket
        sys.exit(0)  # quit program

if __name__ == '__main__':
    User().start()

#
#
# try:
#     data = self.conn_socket.recv(100000000)
# except socket.timeout:  # connection is lost
#     sys.exit(-1)
#
# else:  # data is ok
#     parts = re.findall(r'{"Status": \d, "Section": \d}', data)
#     if len(parts) > 0:
#         index = data.find(parts[0])
#         if index != -1 and self.cur_section != -1:
#             self.sections[self.cur_section] += data[:index]
#
#         for part in parts:
#             self.data_handling(part)
#     elif 'NewID' in data:
#         self.data_handling(data)
#     else:
#         try:
#             self.sections[self.cur_section] += data
#         except:
#             self.data_handling(data)
# if loop_image:
#     image_data = ''
#     while True:
#         data = self.conn_socket.recv(4096)
#         if not data:
#             break
#         elif STOP_IMAGE_LOOP in data:
#             image_data += data[:data.index(STOP_IMAGE_LOOP)]
#             data = data[data.index(STOP_IMAGE_LOOP):]
#             print data[:-50]
#             parts = re.findall(r'{"Status": \d, "Section": \d}', data)
#             [self.data_handling(part) for part in parts]
#
#             break
#         else:
#             image_data += data
