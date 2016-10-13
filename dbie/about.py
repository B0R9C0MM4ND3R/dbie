import tkinter as tk


# this class only shows why the program was made and who the developers were
class AboutGUI(tk.Frame):
    desc_text = """Dieses Programm wurde von Studenten der Universität Passau entwickelt.
                Im Sommersemester 2016 mussten diese im Rahmen der Veranstaltung
                'Text Mining Project' eine Software zu einem bestimmten Thema
                programmieren. Das Thema dieser Software ist die Extraktion von
                Orten und Zeitpunkten von biographischen Texten der
                Deutschen Nationalen Biographie."""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, pad=20)
        desc_label = tk.Label(self, text=self.desc_text)
        desc_label.grid(row=0, column=0, columnspan=2, rowspan=2)
        dev_label1 = tk.Label(self, text="Entwickler:")
        dev_label1.grid(row=3, column=0, padx=25)
        dev_label2 = tk.Label(self, text="Christoph Stemp\nAndreas Vogt")
        dev_label2.grid(row=3, column=1, columnspan=1, rowspan=1)
        button = tk.Button(self, text="Zurück",
                           command=lambda: controller.show_frame("MainGui"))
        button.grid(row=4, column=1)
