import re
import struct
import socket
import json
from PIL import Image, ImageChops


SIGN = '!I'


class Protocol(object):
    def __init__(self, sock):
        self.sock = sock
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def send_one_message(self, data):

        length = len(data)
        info = struct.pack(SIGN, length)
        self.sock.sendall(info)

        self.sock.sendall(data)

    def recv_one_message(self):
        length_buf = self.sock.recv(4)
        if not length_buf:
            return None
        length = struct.unpack(SIGN, length_buf)[0]
        return self.recvall(length)

    def recvall(self, count):
        buf = b''
        while count > 0:
            new_buf = self.sock.recv(count)
            if not new_buf:
                return None
            buf += new_buf
            count -= len(new_buf)
        return buf

    def send_json(self, status, **kwargs):
        """
        This function sends a json message,
        concluding message's status and another arguments(optional).
        :param status: what type of message is it
        :type status: int
        :param kwargs: another arguments
        """

        msg_dict = {"Status": status}
        msg_dict.update(kwargs)

        json_string = json.dumps(msg_dict)
        self.send_one_message(json_string)

    def send_image(self, img_raw_data, section, message_mode):
        """
        This function sends image's raw data to the user.

        :param img_raw_data: image's row data
        :type img_raw_data: list of tuples
        :param section: which part of the screenshot is dispatched
        :param message_mode: the message's mode
        """

        # notify user about upcoming image's raw data
        self.send_json(message_mode, Section=section)

        # send image's raw data
        self.send_one_message(str(img_raw_data))


def string_to_raw(data_list):
    """ This func convert image data to list of tuples - raw data. """
    data = re.findall(r'(?:\d+,\s){2}\d+', data_list)
    return [tuple([int(y) for y in x.split(', ')]) for x in data]


def raw_data_to_img(raw_list, width, height, mode='RGB'):
    """
    This function converts the given raw list to an image,
    using the size and the mode.
    :param raw_list:
    :param width: The width of the intended image.
    :param height: The height of the intended image.
    :param mode: The mode to use for the new image.
    :return: PIL.Image.Image object.
    """
    img = Image.new(mode, (width, height))
    img.putdata(raw_list)
    return img


def img_to_raw_data(img):
    """
    This func coverts PIL.Image object to raw data.
    """
    return list(img.getdata())


def compare_images(im1, im2):
    """
    This function compares between 2 images.
    It return True if they are similar, otherwise False.
    :rtype: boolean
    """

    """Calculate the root-mean-square difference between two images"""

    return ImageChops.difference(im1, im2).getbbox() is None

    # calculate rms
    # return math.sqrt(reduce(operator.add, map(lambda h, i: h*(i**2), h, range(256))) /
    #                  (float(im1.size[0]) * im1.size[1])) <= 10