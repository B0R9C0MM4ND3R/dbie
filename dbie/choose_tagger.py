from tkinter import *

from dbie import gui


# class with which the user can choose the tagger he wants to use
class ChooseTagger(Frame):
    message = """Welchen Tagger wollen Sie für die Bearbeitung wählen?
    spaCy = Reiner Python Tagger (benötigt mehr RAM, aber genauer)
    Stanford NLP = Java Tagger (ungenauer)"""

    def __init__(self, parent):
        Frame.__init__(self)
        self.parent = parent
        self.toplevel = Toplevel(self)
        self.toplevel.focus_force()
        self.toplevel.grab_set()
        self.toplevel.title("Auswahl des Taggers")
        self.toplevel.protocol('WM_DELETE_WINDOW', sys.exit)
        gui.centralise(self.toplevel, 400, 90)
        self.toplevel.minsize(390, 90)
        self.toplevel.resizable(height=False, width=False)
        self.__create_widgets()

    def __create_widgets(self):
        label1 = Label(self.toplevel, text=self.message)
        label1.grid(row=0, column=0, columnspan=2, rowspan=1)
        ok_btn = Button(self.toplevel, text="spaCy", command=self.__spacy)
        ok_btn.grid(row=1, column=0)
        cancel_btn = Button(self.toplevel, text="Stanford NLP", command=self.__stanford)
        cancel_btn.grid(row=1, column=1)

    # sets the bool to False, so that the Stanford tagger will be loaded
    def __stanford(self):
        self.parent.set_tagger_bool(False)
        self.__my_destroy()

    # sets the bool to True, so that the Stanford tagger will be loaded
    def __spacy(self):
        self.parent.set_tagger_bool(True)
        self.__my_destroy()

    # destroys itself and loads the tagger
    def __my_destroy(self):
        self.grab_release()
        self.destroy()
        self.parent.load_data()
