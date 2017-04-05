from PIL import Image, ImageGrab
from Client import TkinterFrame
import threading


def print_num():

    while 1:
        print 'check gui!'

img = ImageGrab.grab()
print len(list(img.getdata()))
width, height = img.size
mode = img.mode

images = {}  # parts of the screen
for x in xrange(5):
    for y in xrange(5):

        start_x = x * (width / 5)
        start_y = y * (height / 5)
        end_x = width / 5
        end_y = height / 5

        cur_img = list(img.crop((start_x, start_y, start_x + end_x, start_y + end_y)).getdata())
        images[x * 5 + y] = str(cur_img)


new_img = Image.new(mode, (width, height))

end_x = width / 5
end_y = height / 5

for x in xrange(5):
    for y in xrange(5):

        start_x = x * (width / 5)
        start_y = y * (height / 5)

        section_img = Image.new(mode, (width / 5, height / 5))
        section_img.putdata(images[x * 5 + y])
        new_img.paste(section_img,
                      (start_x, start_y, start_x + end_x, start_y + end_y))

new_img.save("TEst.jpg")
# exam = TkinterFrame(width, height)
# exam.update_image(new_img)
#
#
# thread = threading.Thread(target=print_num)
# thread.start()