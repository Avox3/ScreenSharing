
from threading import Thread
from utils import Utils


class Send(Thread):
    """ This class is a send thread """
    def __init__(self, socket_obj, server_socket):
        Thread.__init__(self)

        self.socket_obj = socket_obj
        self.server_socket = server_socket
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

    def __init__(self, socket_obj, server_socket):
        Thread.__init__(self)

        self.socket_obj = socket_obj
        self.server_socket = server_socket
        self.utils = Utils()
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):

        while self.is_running:

            self.utils.receive_action(self.socket_obj)


def main():
    import socket

    # create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('10.0.0.3', 8200))

    # get connection
    server_socket.listen(1)
    (conn, add) = server_socket.accept()
    # after get connection , start receive and start threads
    receive_thread = Recv(conn, server_socket)
    send_thread = Send(conn, server_socket)

    try:
        receive_thread.start()
        send_thread.start()
    except Exception, e:
        if str(e) == 'close connection':

            receive_thread.stop()
            send_thread.stop()

            conn.close()
            server_socket.close()

            print str(e)
            exit(0)

if __name__ == "__main__":
    main()
