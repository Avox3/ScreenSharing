
from threading import Thread
from utils import Utils


class Send(Thread):
    """ This class is a send thread """

    def __init__(self, socket_obj):
        Thread.__init__(self)

        self.socket_obj = socket_obj
        self.utils = Utils()
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):

        # user always can to send data

        while self.is_running:

            self.utils.send_action(self.socket_obj)


class Recv(Thread):
    """ This class is a receive thread """

    def __init__(self, socket_obj):
        Thread.__init__(self)

        self.socket_obj = socket_obj
        self.utils = Utils()
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):

        # Ready to receive data every time
        while self.is_running:

            self.utils.receive_action(self.socket_obj)


def main():
    import socket

    # create socket and connect to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 8200))

    receive_thread = Recv(s)
    send_thread = Send(s)

    # start receive and send threads
    try:

        receive_thread.start()
        send_thread.start()

    except Exception, e:
        if str(e) == 'close connection':

            send_thread.stop()
            receive_thread.stop()

            s.close()

            print str(e)
            exit(0)

if __name__ == "__main__":
    main()

