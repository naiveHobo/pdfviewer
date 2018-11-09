from tkinter import *
from PIL import ImageTk, Image
from pdfviewer.config import *


class MenuBox(Frame):

    def __init__(self, master=None, image_path=None, **kw):
        Frame.__init__(self, master, **kw)

        self.menu_button = Menubutton(self, width=50, height=50, bg=BACKGROUND_COLOR, bd=0,
                                      highlightthickness=0, activebackground=HIGHLIGHT_COLOR)

        if image_path:
            self.image = ImageTk.PhotoImage(Image.open(image_path))
            self.menu_button.configure(image=self.image)

        self.menu = Menu(self.menu_button, tearoff=False, bg='#404040',
                         fg='white', bd=2, activebackground=HIGHLIGHT_COLOR)

        self.menu_button.config(menu=self.menu)
        self.menu_button.pack(side=LEFT)

        self.menu_button.bind("<Button-1>", lambda e: self.menu_button.event_generate('<<Invoke>>'))

    def add_item(self, title, func, seperator=False):
        self.menu.add_command(label=title, command=func)
        if seperator:
            self.menu.add_separator()
