
import socket
import sys
import pygame
import json

SERVER_IP = '127.0.0.1'  # address of the server
PORT = 3337  # the port
BUFFER = 508  # memory storage size
ID_REQUEST, QUIT_REQUEST = xrange(2)

save_directory = r'C:\Users\USER\Desktop\screenshot_receive.png'


white = (255, 255, 255)
w = 640
h = 480
running = 1


class Gui(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((w, h))
        self.screen.fill(white)

    def update(self):

        img = pygame.image.load(save_directory)
        self.screen.fill(white)
        self.screen.blit(img, (0, 0))
        pygame.display.flip()


class User(object):

    def __init__(self):

        # create socket and connect to server
        self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.conn_socket.connect((SERVER_IP, PORT))
        self.addr = (SERVER_IP, PORT)
        self.user_id = -1

    def send(self, msg_type):
        json_string = json.dumps({"Type": msg_type, "UserID": self.user_id})
        self.conn_socket.sendto(json_string, self.addr)

    def receive(self):
        pass

    def close(self):
        """ quit from the chat and close socket & program """
        self.send(QUIT_REQUEST)
        self.conn_socket.close()  # close socket
        sys.exit(0)  # quit program

    def send_image(self):
        pass

if __name__ == '__main__':
    pass
