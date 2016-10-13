import os
import sys
import tkinter as tk
import tkinter.messagebox

from dbie import gui, about, check_connection

if os.name == 'nt':
    import msvcrt
else:
    import fcntl


# main class for starting the program
class MainFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (gui.MainGui, about.AboutGUI):
            page_name = F.__name__
            frame = F(container, self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("MainGui")

    # changes to the given page
    def show_frame(self, page_name):
        # Show a frame for the given page name
        frame = self.frames[page_name]
        frame.tkraise()

    # sets the file pointer
    def set_fp(self, fp):
        self.fp = fp

    # deletes the lock file
    def destroy_lock(self):
        self.fp.close()
        os.remove(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "program.pid")

    # exits the program
    @staticmethod
    def exit():
        sys.exit()


if __name__ == "__main__":
    # checks the connection
    con_bool = False
    # sometimes one check isn't enough because it says False even if a connection is there
    # that's why it checks a few times till it says finally False
    for i in range(0, 5):
        con_bool = check_connection.check_url('http://129.187.254.245')
        if con_bool:
            break
    if not con_bool:
        root = tk.Tk()
        root.withdraw()
        if tk.messagebox.showerror("Keine Netzwerkverbindung", "Es konnte keine Verbindung zu " +
                "http://www.deutsche-biographie.de/\n" +
                "hergestellt werden.\n\nDas Programm beendet sich jetzt."):
            sys.exit(2)
    # locks the programm, so that it can only be opened once
    pid_file = 'program.pid'
    fp = open(pid_file, 'w')
    try:
        if os.name == 'nt':
            msvcrt.locking(fp.fileno(), msvcrt.LK_LOCK, 10)
        else:
            fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        sys.exit(1)
    app = MainFrame()
    app.set_fp(fp)
    app.title("Deutsche Biographie - Information Extractor")
    app.minsize(650, 600)
    app.mainloop()
