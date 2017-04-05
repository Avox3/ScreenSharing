
import ImageTk
import Tkinter
from PIL import Image


class ShowImage:
    def __init__(self, path, status, function, *args):

        root = Tkinter.Tk()
        img = ImageTk.PhotoImage(Image.open(path))
        self.label = Tkinter.Label(root, image=img)
        self.label.pack()

        self.path = path
        self.root = root
        tkimg = [None]
        delay = 1000   # in milliseconds

        def loopCapture():

            boolean = function(*args)
            if boolean:
                try:
                    tkimg[0] = ImageTk.PhotoImage(Image.open(path))
                    self.label.config(image=tkimg[0])
                    root.update_idletasks()
                except IOError:
                    root.after(delay, loopCapture)
                root.after(delay, loopCapture)

        if status == 'live':
            loopCapture()
        root.mainloop()


