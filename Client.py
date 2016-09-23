
from PIL import ImageGrab
import tkSimpleDialog
from Tkinter import END, Scrollbar, Tk, Text, Button
import socket
import json
import re
import sys
import base64
import threading
import time

# RECEIVE_ID - client notify server he need an id - (and on the other hand for receiving the id)
# NORMAL_MESSAGE - client sends a normal message to all
# VIEW_USERS - client want to view the connected users
# KICK - client kick an user
# ADMIN_REQUEST - client want to be an admin
# QUIT - client quits from the server
# HIDDEN - hidden message (not showing for the user)
RECEIVE_ID, NORMAL_MESSAGE, VIEW_USERS, KICK, ADMIN_REQUEST, QUIT, IMAGE_START, IMAGE_MID, IMAGE_END, HIDDEN = range(10)


SERVER_IP = '127.0.0.1'  # address of the server
PORT = 3337  # the port
SHIFT = 13  # the shift's code
BUFFER = 4096  # memory storage size


def valid(text):
    """
    check if text is transferable
    :param text: text to check
    """
    return not text.isspace() and text != '' and all(ord(c) < 256 for c in text)


class SendImage(threading.Thread):

    def __init__(self, event):
        threading.Thread.__init__(self)
        self.user = User()
        self.stopped = event

    def run(self):
        while not self.stopped.wait(5):

            ImageGrab.grab(bbox=(1, 1, 100, 100)).save(self.user.save_directory)

            # streaming = True
            # l = f.read(1024)
            # while l:
            #     self.send(IMAGE_MID, l)
            #     l = f.read(1024)

            f = open(self.user.save_directory, 'rb')
            string = base64.b64encode(f.read())
            image_bytes = bytearray(string)

            while len(image_bytes) > 0:
                self.user.send(IMAGE_START, image_bytes[:508 if len(image_bytes) >= 508 else len(image_bytes)])
                image_bytes = image_bytes[508 if len(image_bytes) >= 508 else len(image_bytes):]

            self.user.send(IMAGE_END, 'end !')
            f.close()
            print 'finish'


class User(object):

    def __init__(self):

        # create socket and connect to server
        self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.conn_socket.connect((SERVER_IP, PORT))
        self.save_directory = r'C:\Users\USER\Desktop\screenshot_send.png'

        self.streaming = False
        self.user_id = -1
        self.is_running = True
        self.name = ""

        # chat components
        self.chat_log = None
        self.entry_box = None

        # start receiving thread
        # receiving can interrupt sending, they can't run at the same time on the same thread
        # therefore they must be in different threads
        # receive_thread = Thread(target=self.receive_function)
        # receive_thread.start()
        # self.gui()  # open chat user interface

    def close(self):
        """ quit from the chat and close socket & program """

        self.is_running = False  # prevent any interaction
        self.conn_socket.close()  # close socket
        sys.exit(0)  # quit program

    def send_image(self):
        time.sleep(5)

        ImageGrab.grab(bbox=(1, 1, 50, 50)).save(self.save_directory)

        # streaming = True
        f = open(self.save_directory, 'rb')
        # l = f.read(1024)
        # while l:
        #     self.send(IMAGE_MID, l)
        #     l = f.read(1024)

        string = base64.b64encode(f.read())
        f.close()

        self.send(IMAGE_MID, string)
        self.send(IMAGE_END, "")
        print 'finish'

    def gui(self):

        # Create a window
        base = Tk()
        base.title("Chat")
        base.geometry("400x460")
        base.resizable(width=False, height=False)

        self.name = tkSimpleDialog.askstring("Enter your name", "Enter your name")

        # Create a Chat window
        self.chat_log = Text(base, bd=0, bg="#E1F5FE", height="8", width="50", font="Arial")
        self.add_chat_message("Hello {}.\n".format(self.name))
        self.add_chat_message("You had connected to the server ({}/{})\n\n\n".format(SERVER_IP, PORT))
        self.chat_log.place(x=6, y=6, height=386, width=370)

        # Bind a scrollbar to the Chat window
        scrollbar = Scrollbar(base, command=self.chat_log.yview, cursor="heart")
        scrollbar.place(x=376, y=6, height=386)
        self.chat_log['yscrollcommand'] = scrollbar.set

        # Create the Button to send message
        send_button = Button(base, font=30, text="Send", width="12", height=5, bd=0,
                             bg="#E6EE9C", activebackground="#BCAAA4", command=self.send_function)

        base.bind('<Return>', lambda e: self.send_function())  # keyboard event - Enter -> send message
        base.bind('<Shift-Return>', lambda e: self.add_chat_message(''))  # keyboard event - Shift + Enter -> new line

        send_button.place(x=6, y=401, height=50)

        # Create the box to enter message
        self.entry_box = Text(base, bd=0, bg="#C5E1A5", width="29", height="5", font="Arial")
        self.entry_box.place(x=128, y=401, height=50, width=265)

        base.after(200, self.send(HIDDEN, ''))  # user registration
        base.mainloop()

    def add_chat_message(self, message):
        """
        add the message to the chat log
        :param message: text to add
        """
        self.chat_log.configure(state="normal")  # able to insert
        self.chat_log.insert(END, str(message) + '\n')
        self.chat_log.configure(state="disabled")  # disabled
        self.chat_log.see(END)  # scroll down automatically

    def send(self, msg_type, msg_body):
        """
        this function sending data to the server
        :param msg_type: type of the message
        :param msg_body: the message
        """

        # the data sent in json format
        json_string = json.dumps({"Type": msg_type, "UserID": self.user_id, "Name": self.name,
                                  "Message": msg_body.decode("ISO-8859-1")})

        # send encrypted data to the server
        if msg_body == HIDDEN:  # not for client

            self.conn_socket.sendto(json_string, (SERVER_IP, PORT))

        # elif valid(msg_body):
        else:
            self.conn_socket.sendto(json_string, (SERVER_IP, PORT))

    def send_function(self):
        """
        this function responsible for sending at client side
        """

        # user's message
        data = self.entry_box.get("0.0", END)
        # clean entry box
        self.entry_box.delete("0.0", END)

        # filter
        if data.replace('\n', '') == 'quit':  # quit from chat
            self.send(QUIT, data)
            self.close()

        elif data.lower().replace('\n', '') in {"view", "users", "view users"}:  # view users
            self.send(VIEW_USERS, data)

        elif re.search("kick\s.+\s\d+", data):  # kick [user name] [user id] , example : kick david 31
            self.send(KICK, "{} {}".format(*data.split(' ')[1:]))

        elif data.replace('\n', '') == 'ADMIN':  # Admin request
            self.send(ADMIN_REQUEST, data)

        elif data != '':  # normal message
            self.send(NORMAL_MESSAGE, data)

        else:  # unknown message
            self.close()

    def receive_function(self):
        """ this function responsible for receiving at client side """

        # ready to receive data every time
        while self.is_running:

            # receive encrypted data in json format
            receive, addr = self.conn_socket.recvfrom(BUFFER)

            # check if data is ok
            if receive == '':
                # empty string means that the connection lost
                self.close()

            elif receive:  # json string is ok

                # converting json string to dictionary
                data = json.loads(receive)
                # extracting data
                msg_type = data['Type']
                msg_body = data['Message']

                # filter by type
                if msg_type == RECEIVE_ID:
                    # the server added the user and gave him an id
                    self.user_id = int(msg_body)

                elif msg_type == NORMAL_MESSAGE:  # normal chat message
                    self.add_chat_message(msg_body)

                elif msg_type == VIEW_USERS:  # view users

                    self.add_chat_message(str(msg_body).encode('utf-8'))

                elif msg_type == QUIT:  # user kicked

                    self.add_chat_message('You had been kicked')
                    self.close()

if __name__ == '__main__':
    SendImage(threading.Event()).start()
