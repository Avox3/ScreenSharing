import socket
import json
import threading
import select
from PIL import ImageGrab
from Utils import Protocol, img_to_raw_data, compare_images

# module's attributes
SERVER_IP = '127.0.0.1'  # address of the server
PORT = 3337  # the port

BUFFER = 4096  # memory storage size
SLEEP_TIME = 0.5

INITIALIZE, QUIT_REQUEST, ROW_SECTIONS_LENGTH, SENDING_SECTION = range(4)


class User(object):
    """ this class represents a user """

    def __init__(self, user_id, user_socket):

        self.protocol = Protocol(user_socket)
        self.user_id = user_id
        self.new_user = True


class TakeScreenShot(threading.Thread):
    """
    this class captures a screenshot every x seconds,
    and sends accordingly the changes from the last screenshot
    """

    def __init__(self, server):
        threading.Thread.__init__(self)
        self.pre_images = []

        self.section_x = 3
        self.section_y = 3
        self.server = server

    def get_images(self):
        """
        this func grabs a screenshot and separates it
        :return: parts of a screenshot
        :rtype: list
        """
        img = ImageGrab.grab()
        width, height = img.size

        images = {}  # parts of the screen
        end_x = width / self.section_x
        end_y = height / self.section_y
        for x in xrange(self.section_x):
            for y in xrange(self.section_y):

                start_x = x * (width / self.section_x)
                start_y = y * (height / self.section_y)

                cur_img = img.crop((start_x, start_y, start_x + end_x, start_y + end_y))
                images[x * self.section_x + y] = cur_img
        return images

    def run(self):

        while True:

            images = self.get_images()

            # check for changes
            changes = []
            if len(self.pre_images) == 0:  # first check
                changes = range(self.section_x * self.section_y)

            elif len(self.pre_images) == len(images):
                for index in images.keys():

                    if not compare_images(images[index], self.pre_images[index]):  # different
                        changes.append(index)

            print 'changes :', len(changes)
            self.pre_images = images  # update for next check
            self.server.send_data(self.pre_images, changes)  # send changes
            # time.sleep(10)


class Server(threading.Thread):
    """ this class represents server class """

    def __init__(self):
        threading.Thread.__init__(self)

        self.id_counter = 0
        self.users = []  # users list
        self.open_client_sockets = []  # available sockets - connections
        self.admins = []  # admins list

        temp = ImageGrab.grab()
        self.width, self.height = temp.size
        self.img_mode = temp.mode

        # create a server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((SERVER_IP, PORT))
        self.server_socket.listen(3)

        self.protocol = Protocol(self.server_socket)

        # start a TakeScreenShot thread
        self.screenShotThread = TakeScreenShot(self)

    def user_by_id(self, user_id):
        """
        this func returns a user object according an ID,
        if the user isn't exists returned None.
        :param user_id: the user's id
        :return: the required user object
        """
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None

    def initialize(self, user_socket):
        """
        this func handles an initialize request,
        coordinates with the client the settings,
        and appends the user to the system.
        :param user_socket: new user's socket (address)
        """

        # count the new user
        self.users.append(User(self.id_counter, user_socket))

        json_string = json.dumps({"Status": INITIALIZE,
                                  "UserID": self.id_counter,
                                  "ScreenWidth": self.width,
                                  "ScreenHeight": self.height,
                                  "ImageMode": self.img_mode,
                                  "SectionX": self.screenShotThread.section_x,
                                  "SectionY": self.screenShotThread.section_y})

        self.users[-1].protocol.send_one_message(json_string)
        # user_socket.sendall(json_string)
        self.id_counter += 1

    def send_json(self, user, status, section, **kwargs):

        msg_dict = {"Status": status, "Section": section}
        msg_dict.update(kwargs)

        json_string = json.dumps(msg_dict)
        user.protocol.send_one_message(json_string)

    def send(self, user, m_dict):
        json_string = json.dumps(m_dict)
        user.protocol.send_one_message(json_string)

    def send_image(self, user, img_bytes, section):
        """

        :param user:
        :param img_bytes:
        :param section:
        :return:
        """
        self.send(user, {"Status": SENDING_SECTION, "Section": section})
        user.protocol.send_one_message(str(img_bytes))

    def send_data(self, images, changes):
        """
        this func sends each client his requested parts
        :param images: all parts of the screenshot
        :param changes: new parts from previous screenshot
        """

        # converts `PIL.Image.Image` list to a raw_data list
        images = {index: img_to_raw_data(images[index]) for index in images}

        for user in self.users:
            if user.new_user:

                # TODO - send settings about this row of images
                self.send_json(user, ROW_SECTIONS_LENGTH, -1, SectionsLength=len(images))

                for index in images:
                    self.send_image(user, images[index], index)
                    user.new_user = False

            else:
                for index in changes:
                    self.send_image(user, images[index], index)

    def close_client(self, user_id):
        for user in self.users:
            if user.user_id == user_id:
                user.user_socket.close()
                self.users.remove(user)

    def run(self):

        while True:

            # read and write sockets lists
            # rlist - clients are sending data currently
            rlist, wlist, xlist = select.select([self.server_socket] + self.open_client_sockets,
                                                self.open_client_sockets, [])

            for current_socket in rlist:

                if current_socket is self.server_socket:  # new connection

                    new_socket, address = self.server_socket.accept()
                    self.open_client_sockets.append(new_socket)  # add socket
                    print 'Got new connection'
                else:  # input from existing socket

                    prcl = Protocol(current_socket)
                    data = prcl.recv_one_message()

                    if data != '':

                        data = json.loads(data)
                        msg_status = int(data['Status'])
                        user_id = int(data['UserID'])
                        curr_user = self.user_by_id(user_id)

                        if msg_status == INITIALIZE:
                            print 'user', user_id, 'initialized'
                            self.initialize(current_socket)

                            if len(self.users) == 1:
                                self.screenShotThread.start()

                        elif not curr_user:
                            continue

                        elif msg_status == QUIT_REQUEST:
                            self.close_client(user_id)

if __name__ == '__main__':
    Server().start()
