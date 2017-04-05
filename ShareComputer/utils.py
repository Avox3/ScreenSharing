
from PIL import ImageGrab, Image
from Repeat import Repeat


class Utils:
    """ This class gives utilities """

    def check_readable(self, path):
        try:
            im=Image.open(path)
            return True

        except IOError:
            return False

    def screen(self, path):
         """
         takes a screenshot
         :param path - location of the screenshot image
         """
         im = ImageGrab.grab()
         im.save(path)
         return path

    def send_screen(self, path, socket_obj):
        """
        send screenshot
        :param path - location of the screenshot image
        :param socket_obj - required for sending screenshot
        """

        image = open(self.screen(path), 'rb')
        data = image.read()
        image.close()

        socket_obj.send('screenshot')
        socket_obj.send(data)

    def receive_image(self, path, socket_obj):
        """
        receive image
        :param path - where the image will be saved
        :param socket_obj - required for receiving data
        """

        # image file
        image = open(path, 'wb+')

        # get data
        data = socket_obj.recv(1024)

        # if data continues to arrive
        while data:

            if not data:
                # Image successfully transferred
                break
            if not data == 'screenshot':
                image.write(data)

            # if data not continues to arrive
            # except calling and break
            socket_obj.settimeout(1.5)
            try:
                data = socket_obj.recv(1024)
            except:
                break

        image.close()
        return self.check_readable(path)

        # ShowImage(path, 'image')

    def send_action(self, socket_obj):
        # get input
        data = raw_input('Enter message:\n')

        print 'you :', data

        # send input
        socket_obj.send(data)

        # translation input to actions

        if data == 'exit':

            print 'disconnected...'
            raise Exception("close connection")

        elif data == 'screenshot':

            self.send_screen(r'C:\Users\USER\Documents\send_screenshot.png', socket_obj)

        elif data == 'live':

             # screenshot that updates every X seconds
             # It auto-starts, no need of rt.start()

            Repeat(1, self.send_screen, r'C:\Users\USER\Documents\send_screenshot.png', socket_obj)

    def receive_action(self, socket_obj):
        # reset timeout
        socket_obj.settimeout(None)

        # receive data
        # recv blocking till data is sent
        data = socket_obj.recv(1024)

        # Identifying information sent
        if data == 'exit':
            # close connection
            print 'disconnected...'
            raise Exception('close connection')

        elif data == 'screenshot':
            # get screenshot
            print 'screenshot is receiving to you'
            self.receive_image(r'C:\Users\USER\Documents\receive_screenshot.png', socket_obj)
        else:
            # else - > normal data , we just have to print him
            print 'other guy :', data

# Utils().screen(r'C:\Users\USER\Documents\receive_screenshot.jpg')
