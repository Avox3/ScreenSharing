import Tkinter
import threading
from PIL import ImageTk, Image
import socket
import select
import json
import Queue

# SEND_ID - server send an id to the client
# NORMAL_MESSAGE - client sent a normal message to all
# VIEW_USERS - client want to view the connected users
# KICK - client kick an user
# ADMIN_REQUEST - client want to be an admin
# QUIT - client quits from the server
SEND_ID, NORMAL_MESSAGE, VIEW_USERS, KICK, ADMIN_REQUEST, QUIT, IMAGE_START, IMAGE_MID, IMAGE_END = range(9)

SERVER_IP = '127.0.0.1'  # address of the server
PORT = 3337  # the port
SHIFT = 13  # the shift's code
BUFFER = 4096  # memory storage size

users = []  # users list
open_client_sockets = []  # available sockets - connections
admins = []  # admins list

save_directory = r'C:\Users\USER\Desktop\screenshot_receive.png'


class User(object):
    """ this class defines a user """
    def __init__(self, user_socket, user_id, user_name):

        self.user_socket = user_socket
        self.user_id = user_id
        self.user_name = user_name


class Gui(object):

    def __init__(self):

        self.root = Tkinter.Tk()
        self.panel = None
        self.queue = Queue.Queue()

        Server(self).start()
        self.root.after(100, self.process_queue)

    def process_queue(self):

        try:
            task = self.queue.get()

        except Queue.Empty:
            self.root.after(100, self.process_queue)

        else:
            self.root.after_idle(task)

    def set_gui(self):

        self.root = Tkinter.Tk()
        im = Image.open(save_directory)
        img = ImageTk.PhotoImage(im)
        self.panel = Tkinter.Label(self.root, image=img)
        self.panel.pack(side="bottom", fill="both", expand="yes")

        self.root.mainloop()

    def callback(self):
        print 'changing'
        im = Image.open(save_directory)
        img = ImageTk.PhotoImage(im)
        self.panel = self.panel.configure(image=img)
        self.panel.image = img


class Server(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui
        self.queue = gui.queue

    def run(self):
        self.queue.put(self.check_data)

    def check_data(self):
        # create a server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((SERVER_IP, PORT))

        streaming = False

        # while True:

        # read and write sockets lists
        # rlist - clients are sending data currently
        rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])

        for current_socket in rlist:

            receive, addr = current_socket.recvfrom(BUFFER)
            if receive != '':

                data = json.loads(receive)
                msg_type = data['Type']
                msg_sender = data['Name']
                msg_body = data['Message'].encode("ISO-8859-1")
                msg_id = int(data['UserID'])

                if msg_type == IMAGE_START:
                    if not streaming:
                        streaming = True
                        print 'starting'
                        f = open(save_directory, 'wb')

                    if msg_body:
                        f.write(msg_body.decode('base64'))

                elif msg_type == IMAGE_END:
                    print 'finish'
                    streaming = False
                    f.close()

                    if not self.gui.panel:
                        self.queue.put(self.gui.set_gui)
                    else:
                        self.queue.put(self.gui.callback)

        self.queue.put(self.check_data)

if __name__ == '__main__':
    Gui()
