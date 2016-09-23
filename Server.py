import socket
import select
import json

SERVER_IP = '127.0.0.1'  # address of the server
PORT = 3337  # the port
BUFFER = 508  # memory storage size
ID_REQUEST, QUIT_REQUEST = xrange(2)

save_directory = r'C:\Users\USER\Desktop\screenshot_send.png'
id_counter = 0

users = []  # users list
open_client_sockets = []  # available sockets - connections
admins = []  # admins list


class User(object):
    """ this class defines a user """
    def __init__(self, addr, user_id):

        self.user_id = user_id
        self.addr = addr
        global id_counter
        id_counter += 1


class Server(object):
    def __init__(self):

        # create a server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((SERVER_IP, PORT))

        while True:

            # read and write sockets lists
            # rlist - clients are sending data currently
            rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])

            for current_socket in rlist:

                receive, addr = current_socket.recvfrom(BUFFER)

                if receive != '':

                    data = json.loads(receive)
                    msg_type = data['Type']
                    user_id = int(data['UserID'])

                    if msg_type == ID_REQUEST:
                        users.append(User(id_counter, addr))

                    if msg_type == QUIT_REQUEST:
                        self.close_client(user_id)

    def close_client(self, user_id):
        for user in users:
            if user.user_id == user_id:
                users.remove(user)

if __name__ == '__main__':
    # asd
    pass



# def take_screenshot():
#     ImageGrab.grab(bbox=(1, 1, 100, 100)).save(self.user.save_directory)
#     f = open(self.user.save_directory, 'rb')
#     string = base64.b64encode(f.read())
#     image_bytes = bytearray(string)
#
#     while len(image_bytes) > 0:
#     self.user.send(IMAGE_START, image_bytes[:508 if len(image_bytes) >= 508 else len(image_bytes)])
#     image_bytes = image_bytes[508 if len(image_bytes) >= 508 else len(image_bytes):]
#
#     self.user.send(IMAGE_END, 'end !')
#     f.close()
#     print 'finish'
#
# white = (255, 64, 64)
# w = 640
# h = 480
