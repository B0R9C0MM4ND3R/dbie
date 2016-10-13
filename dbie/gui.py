import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
from pycorenlp import StanfordCoreNLP
import subprocess
import spacy

from dbie import analyzer_type
from dbie import check_connection
from dbie import choose_tagger
from dbie import search_adb_ndb
from dbie import stanford
from dbie.analyzer_spacy import AnalyzerSpacy
from dbie.splash import Splash
from dbie.analyzer_stanford import AnalyzerStanford


# this class represents the gui and also has most of its functions
class MainGui(tk.Frame):
    spacy_nlp = ()
    stanford_nlp = ()
    stanford_server = stanford.Server()
    name_index = 0
    letter_index = 0
    # True for spaCy, False for Stanford
    tagger_bool = False

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        self.letter_tuple = ()
        self.name_tuple = ()
        self.controller.withdraw()
        self.controller.protocol('WM_DELETE_WINDOW', self.destroy_all)

        self.adb_ndb_label = tk.Label(self, text="Alte/Neue Deutsche Bibliothek")
        self.adb_ndb_box = ttk.Combobox(self, values=["NDB", "ADB"])
        self.letter_label = tk.Label(self, text="Anfangsbuchstabe", state=tk.DISABLED)
        self.letter_box = ttk.Combobox(self)
        self.name_label = tk.Label(self, text="Name", state=tk.DISABLED)
        self.extract_btn = tk.Button(self, text="Extrahieren", state=tk.DISABLED,
                                     command=self.__extract)
        self.name_box = ttk.Combobox(self)
        self.txt = tk.Text(self, borderwidth=3, relief="sunken")
        scrollbar = tk.Scrollbar(self.txt)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar.config(command=self.txt.yview())
        self.save_btn = tk.Button(self, text="Speichern",
                                  command=self.__save_data_extract)
        self.menu = tk.Menu(self.controller)
        self.extract_all_menu = tk.Menu(self.menu, tearoff=0)
        self.tagger_menu = tk.Menu(self.menu, tearoff=0)

        # Analyzer types
        self.spacy = analyzer_type.Analyzer("Spacy", "NUM", "LOC", "PROPN")
        self.stanford = analyzer_type.Analyzer("Stanford", "CARD", "I-LOC", "NE")

        self.stopped = False
        self.__choose_tagger()

    def __create_widgets(self):
        self.controller.deiconify()
        self.__create_menu()

        self.disable_btn(self.save_btn)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(4, weight=1)
        self.columnconfigure(3, pad=50)
        self.columnconfigure(0, pad=50)
        self.rowconfigure(0, pad=50)
        self.rowconfigure(3, pad=50)
        self.rowconfigure(2, pad=50)
        self.rowconfigure(3, pad=20)

        self.adb_ndb_label.grid(row=0, column=0)
        self.adb_ndb_box.grid(row=0, column=1)
        self.adb_ndb_box.bind("<<ComboboxSelected>>", self.__fill_letter_box)
        self.adb_ndb_box.state(["readonly"])
        self.letter_label.grid(row=1, column=0)
        self.letter_box.state(["readonly"])
        self.letter_box.grid(row=1, column=1)
        self.letter_box.bind("<<ComboboxSelected>>", self.__fill_name_box)
        self.name_label.grid(row=2, column=0)
        self.extract_btn.grid(row=3, column=0)
        self.name_box.grid(row=2, column=1)
        self.name_box.state(["readonly"])
        self.name_box.bind("<<ComboboxSelected>>", self.__activate_extract_btn)
        self.save_btn.grid(row=3, column=1)

        self.txt.config(font=("consolas", 12), undo=True, wrap='word')
        self.txt.grid(row=4, column=0, columnspan=2, rowspan=2)
        self.txt.grid_configure(sticky="nsew")
        self.txt.config(state=tk.DISABLED)
        centralise(self.controller, 0, 0)

    # fill the letter box with the values of the selected biography
    def __fill_letter_box(self, event):
        self.letter_box.set("")
        self.name_box.set("")
        if not self.__conn_check():
            self.adb_ndb_box.set("")
            return
        if self.adb_ndb_box.get() == "ADB":
            self.letter_box["values"] = search_adb_ndb.get_all_adb_letters()
            self.letter_tuple = search_adb_ndb.get_all_adb()
        else:
            self.letter_box["values"] = search_adb_ndb.get_all_ndb_letters()
            self.letter_tuple = search_adb_ndb.get_all_ndb()
        self.disable_btn(self.extract_btn)
        self.letter_label.config(state=tk.NORMAL)
        self.name_label.config(state=tk.DISABLED)

    # fill the name box with the values from the selected first letter
    def __fill_name_box(self, event):
        self.name_box.set("")
        self.letter_index = 0
        for (x, y) in self.letter_tuple:
            if x == self.letter_box.get():
                break
            else:
                self.letter_index += 1
        if not self.__conn_check():
            self.adb_ndb_box.set("")
            self.letter_box.set("")
            return
        self.name_tuple = search_adb_ndb.get_all_ndb_adb_names(
            self.letter_tuple[self.letter_index][1])
        name_list = []
        for (x, y) in self.name_tuple:
            name_list.append(x)
        self.name_box["values"] = name_list
        self.name_label.config(state=tk.NORMAL)
        self.disable_btn(self.extract_btn)

    # creates the menu for the gui
    def __create_menu(self, extract_all_running=False):
        if not (extract_all_running is True or extract_all_running is False):
            raise ValueError("extract_all_running must be bool!")
        file_menu = tk.Menu(self.menu, tearoff=0)

        file_menu.add_command(label="Beenden", command=self.destroy_all)
        self.menu.add_cascade(label="Datei", menu=file_menu)
        self.extract_all_menu.add_command(label="Starten", command=self.__show_popup_warning_extract_all)
        self.extract_all_menu.add_command(label="Abbrechen", command=self.__stop_extract_all)
        self.extract_all_menu.entryconfig(1, state=tk.DISABLED)
        self.menu.add_cascade(label="Alles extrahieren", menu=self.extract_all_menu)
        help_menu = tk.Menu(self.menu, tearoff=0)
        help_menu.add_command(label="Über",
                              command=lambda: self.controller.show_frame("AboutGUI"))
        self.tagger_menu.add_command(label="Stanford", command=self.__change_tagger)
        self.tagger_menu.add_command(label="spaCy", command=self.__change_tagger)
        if self.tagger_bool:
            self.tagger_menu.entryconfig(1, state=tk.DISABLED)
        else:
            self.tagger_menu.entryconfig(0, state=tk.DISABLED)
        self.menu.add_cascade(label="Wechsle Tagger", menu=self.tagger_menu)
        self.menu.add_cascade(label="Hilfe", menu=help_menu)
        self.controller.config(menu=self.menu)

    # if necessary shuts down server for the stanford tagger and destroys the gui
    def destroy_all(self):
        if tk.messagebox.askokcancel("Beenden", "Möchten Sie das Programm "
                                                "wirklich beenden?"):
            if not self.tagger_bool:
                url = 'http://127.0.0.1:9000'
                # checks if the server has already been shutdown manually
                if check_connection.check_url(url):
                    self.stanford_server.join()
                    stanford.stop()
            self.stopped = True
            self.controller.destroy_lock()
            self.controller.destroy()
            self.controller.exit()

    # starts the server for the stanford tagger
    def __start_stanford(self):
        url = 'http://127.0.0.1:9000'
        self.stanford_server.start()
        while not check_connection.check_url(url):
            pass
        os.chdir('../..')
        self.stanford_nlp = StanfordCoreNLP(url)
        stanford.preload_classifiers(self.stanford_nlp)

    # loads the German language into spacy
    def __start_spacy(self):
        error = True
        while error:
            try:
                self.spacy_nlp = spacy.load('de')
                error = False
            except RuntimeError:
                if tk.messagebox.askokcancel("Fehlende Modelldaten", message="Modelldaten für spaCy wurden nicht gefunden.\n"
                                                         "Diese werden nun heruntergeladen."):
                    try:
                        subprocess.call('python -m spacy.de.download')
                    except OSError:
                        if tk.messagebox.showerror("Fehler", message="Herunterladen der Modelldaten fehlgeschlagen.\n"
                                                                  "Laden Sie die Daten manuell mit:\npython -m"
                                                                  " spacy.de.download"):
                            sys.exit()

                else:
                    sys.exit()

    # extracts the information about the selected person
    # uses the selected tagger
    def __extract(self):
        self.name_index = 0
        for (x, y) in self.name_tuple:
            if x == self.name_box.get():
                break
            else:
                self.name_index += 1
        self.__extract_conn_check()
        if self.stopped:
            return
        url = search_adb_ndb.url + self.name_tuple[self.name_index][1]
        self.__clear_txt()
        # begin the extraction with the right tagger
        if self.tagger_bool:
            analyzer = AnalyzerSpacy(self.spacy)
            out = AnalyzerSpacy.analyze(analyzer, url, self.spacy_nlp)
            self.__fill_txt(AnalyzerSpacy.get_name(url))
        else:
            analyzer = AnalyzerStanford(self.stanford)
            out = AnalyzerStanford.analyze(analyzer, url, self.stanford_nlp)
            self.__fill_txt(AnalyzerStanford.get_name(url))
        if type(out) is list:
            for item in out:
                self.__fill_txt('\n')
                self.__fill_txt(item)
        else:
            self.__fill_txt('\n')
            self.__fill_txt(out)
        self.save_btn.config(state=tk.NORMAL)

    # activates the extract button
    def __activate_extract_btn(self, event):
        self.extract_btn.config(state=tk.NORMAL)

    # disables a button
    @staticmethod
    def disable_btn(btn):
        btn.config(state=tk.DISABLED)

    # shows a popup warning if the user really wants to extract all data
    def __show_popup_warning_extract_all(self):
        if tk.messagebox.askokcancel("Warnung", """Sind Sie wirklich sicher, alle Datensätze
                extrahieren zu wollen?\nDer Vorgang kann sehr lange dauern!
                \n\nDie Dateien werden in den Ordner 'saves'
                 gespeichert."""):
            self.update()
            self.__extract_all()

    # extracts all the data from the website
    def __extract_all(self):
        self.stopped = False
        self.__clear_all_labels_boxes(True)
        self.extract_all_menu.entryconfig(1, state=tk.NORMAL)
        self.extract_all_menu.entryconfig(0, state=tk.DISABLED)
        self.update()
        self.__clear_txt()
        element_count = 0
        self.__fill_txt("Starten der Vorbereitung zum Extrahieren.\n"
                        "Während dem Ladevorgang kann nicht abgebrochen werden.\n"
                        "Bitte warten...\n")
        self.update()
        self.__extract_conn_check()
        adb_tuple_letter = search_adb_ndb.get_all_adb()
        ndb_tuple_letter = search_adb_ndb.get_all_ndb()
        adb_tuple_name = []
        ndb_tuple_name = []
        i = 0
        # load all the names and urls in the tuples
        for (x, y) in adb_tuple_letter:
            self.__extract_conn_check()
            if self.stopped:
                return
            adb_tuple_name.append(search_adb_ndb.get_all_ndb_adb_names(y))
            element_count += len(adb_tuple_name[i])
            i += 1
        i = 0
        for (x, y) in ndb_tuple_letter:
            self.__extract_conn_check()
            if self.stopped:
                return
            ndb_tuple_name.append(search_adb_ndb.get_all_ndb_adb_names(y))
            element_count += len(ndb_tuple_name[i])
            i += 1
        self.__fill_txt("Vorbereitungen abgeschlossen.\n")
        self.__fill_txt("Starten der Extraktion der Daten.\n")
        i = 1
        # begin the extraction of the biography
        for array in adb_tuple_name:
            self.__extract_conn_check()
            if self.stopped:
                return
            i = self.__help_extract_all(array, element_count, i, "adb")
        for array in ndb_tuple_name:
            if self.stopped:
                return
            self.__extract_conn_check()
            self.__help_extract_all(array, element_count, i, "ndb")
        self.__fill_txt("Extraktion abgeschlossen.")
        self.__clear_all_labels_boxes()
        self.menu.entryconfig("Alles extrahieren", state=tk.NORMAL)
        self.menu.entryconfig(3, state=tk.NORMAL)

    # fills the text area
    def __fill_txt(self, text):
        self.txt.config(state=tk.NORMAL)
        self.txt.insert(tk.END, text)
        self.txt.config(state=tk.DISABLED)

    # clears the text area
    def __clear_txt(self):
        self.txt.config(state=tk.NORMAL)
        self.txt.delete('1.0', tk.END)
        self.txt.config(state=tk.DISABLED)

    # opens a window to choose the tagger
    def __choose_tagger(self):
        choose_tagger.ChooseTagger(self)

    # loads the selected tagger and shows the splash screen
    def load_data(self):
        self.update()
        splash = Splash(self.controller)
        if self.tagger_bool:
            self.__start_spacy()
        else:
            self.__start_stanford()
        splash.destroy()
        self.__create_widgets()

    # opens a file menu, so that the user can select where he wants
    # to save the extracted data and saves it
    def __save_data_extract(self):
        file_opt = options = {}
        path_dir = os.path.dirname(__file__) + os.path.sep + "saves"
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)
        name = self.name_box.get()
        name = name.replace(" ", "_")
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('text files', '.txt')]
        options['initialdir'] = path_dir
        options['title'] = 'Wo soll die Datei gespeichert werden?'
        options['initialfile'] = name + '.txt'
        filename = tk.filedialog.asksaveasfilename(**file_opt)
        if filename:
            with open(filename, "w") as file:
                file.write(self.txt.get("1.0", tk.END))

    @staticmethod
    # save method for the extract_all() method
    def save_data_extract_all(person, text, sub_dir):
        path_dir = os.path.dirname(__file__) + os.path.sep + "saves" + os.path.sep + sub_dir
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)
        name = person
        name = name.replace(" ", "_")
        name = name.replace("\n", "")
        with open(path_dir + os.path.sep + name + ".txt", "a") as file:
            file.write(text)

    # extraction method for extract_all()
    def __help_extract_all(self, array, element_count, i, sub_dir):
        for (x, y) in array:
            if self.stopped:
                return i
            url = search_adb_ndb.url + y
            if self.tagger_bool:
                analyzer = AnalyzerSpacy(self.spacy)
                out = AnalyzerSpacy.analyze(analyzer, url, self.spacy_nlp)
                name = AnalyzerSpacy.get_name(url)
            else:
                analyzer = AnalyzerStanford(self.stanford)
                out = AnalyzerStanford.analyze(analyzer, url, self.stanford_nlp)
                name = AnalyzerStanford.get_name(url)
            self.save_data_extract_all(name, name + "\n", sub_dir)
            if type(out) is list:
                for item in out:
                    self.save_data_extract_all(name, " ".join(item), sub_dir)
                    self.save_data_extract_all(name, "\n", sub_dir)
            else:
                self.save_data_extract_all(name, out, sub_dir)
                self.save_data_extract_all(name, "\n", sub_dir)
            self.__clear_txt()
            text = str(i) + " von " + str(element_count) + " Elementen bearbeitet."
            self.__fill_txt(text)
            self.update()
            i += 1
        return i

    # enables or disables all labels and buttons
    def __clear_all_labels_boxes(self, disable_all=False):
        if disable_all is False or disable_all is True:
            self.letter_label.config(state=tk.DISABLED)
            if disable_all is False:
                self.adb_ndb_label.config(state=tk.NORMAL)
            else:
                self.adb_ndb_label.config(state=tk.DISABLED)
            self.name_label.config(state=tk.DISABLED)
            self.letter_box.set("")
            self.letter_box["values"] = []
            self.adb_ndb_box.set("")
            self.name_box.set("")
            self.name_box["values"] = []
        else:
            raise ValueError("disable_all must be a bool!")

    # changes the tagger, hides the gui and loads the splash screen while doing it
    def __change_tagger(self):
        self.tagger_bool = not self.tagger_bool
        self.controller.withdraw()
        splash = Splash(self.controller)
        if self.tagger_bool:
            stanford.stop()
            self.tagger_menu.entryconfig(1, state=tk.DISABLED)
            self.tagger_menu.entryconfig(0, state=tk.NORMAL)
            self.__start_spacy()
        else:
            self.tagger_menu.entryconfig(1, state=tk.NORMAL)
            self.tagger_menu.entryconfig(0, state=tk.DISABLED)
            self.spacy_nlp = ()
            self.stanford_server = stanford.Server()
            self.__start_stanford()
        splash.destroy()
        self.controller.deiconify()
        centralise(self.controller, 0, 0)

    # stops the function to extract all item
    def __stop_extract_all(self):
        self.stopped = True
        self.extract_all_menu.entryconfig(1, state=tk.DISABLED)
        self.extract_all_menu.entryconfig(0, state=tk.NORMAL)
        self.__clear_all_labels_boxes()
        self.__clear_txt()

    # checks  the connection for "http://www.deutsche-biographie.de" and stops the
    # extraction of the user wants to
    def __extract_conn_check(self):
        conn = check_connection.check_url('http://129.187.254.245')
        while not conn:
            if self.__conn_warning():
                for i in range(0, 5):
                    conn = check_connection.check_url('http://129.187.254.245')
                    if conn:
                        break
            else:
                self.__stop_extract_all()
                return

    # checks the connection for "http://www.deutsche-biographie.de"
    def __conn_check(self):
        conn = check_connection.check_url('http://129.187.254.245')
        while not conn:
            if self.__conn_warning():
                for i in range(0, 5):
                    conn = check_connection.check_url('http://129.187.254.245')
                    if conn:
                        break
            else:
                return False
        return True

    # creates a warning for a connection error
    @staticmethod
    def __conn_warning():
        return tk.messagebox.askretrycancel("Verbindungsfehler", "Es scheint ein Verbindungsfehler"
                                                          " aufgetreten  zu sein.\n"
                                                          "Falls der Fehler weiterhin besteht,"
                                                          " verbinden Sie sich mit einem Proxy-"
                                                          "Server, einem VPN Service oder "
                                                          "kontaktieren Sie ihren Administrator.")

    # sets the tagger_bool variable
    def set_tagger_bool(self, tagger_bool):
        if tagger_bool is True or tagger_bool is False:
            self.tagger_bool = tagger_bool
        else:
            raise ValueError("tagger_bool must be bool")


# method to centralise a given frame/toplevel element
def centralise(toplevel, width, height):
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w / 2 - size[0] / 2 - width / 2
    y = h / 2 - size[1] / 2 - height
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))
