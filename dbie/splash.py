import os
import tkinter as tk
from PIL import Image, ImageTk

from dbie import gui


# splash screen when the program is loading the tagger files
class Splash(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        img = ()
        try:
            img = Image.open(os.path.dirname(__file__) + os.path.sep + "pic" + os.path.sep + "uni_logo.png")
            img = img.resize((100, 50))
            img = ImageTk.PhotoImage(img)
            load_panel = True
        except IOError:
            load_panel = False
            print("Konnte Datei 'uni_logo.png' nicht finden!")
        self.toplevel = tk.Toplevel(self)
        self.toplevel.title("Bitte warten")
        self.toplevel.overrideredirect(1)
        text = " Bitte warten Sie bis das Programm\n komplett geladen wurde."
        if load_panel:
            panel = tk.Label(self.toplevel, image=img)
            panel.grid(row=0, column=0, rowspan=2, columnspan=2)
        label1 = tk.Label(self.toplevel, text=text)
        label1.grid(row=2, column=0, rowspan=2, columnspan=2)
        label1.config(compound=tk.CENTER)
        gui.centralise(self.toplevel, 215, 100)
        self.toplevel.minsize(215, 100)
        self.update()
