from tkinter import *
from PIL import Image, ImageTk
from pdfviewer.tooltip import ToolTip


class HoverButton(Button):

    def __init__(self, master, tool_tip=None, image_path=None, keep_pressed=False, **kw):
        Button.__init__(self, master=master, **kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        if keep_pressed:
            self.bind("<Button-1>", self.on_click)
        if image_path:
            self.image = ImageTk.PhotoImage(Image.open(image_path))
            self.configure(image=self.image)
        if tool_tip:
            ToolTip(self, text=tool_tip)

    def on_click(self, e):
        if self['background'] == self.defaultBackground:
            self['background'] = self['activebackground']
        else:
            self['background'] = self.defaultBackground

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground
