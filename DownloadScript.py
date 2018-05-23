import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog

import os
import dropbox
import time
import subprocess

# asks the user to choose the install directory and then creates the empty file structure within
def setinstalldir():
    global filedir
    # ask the user where they want to install SISA
    filedir = tkinter.filedialog.askdirectory()

    if filedir != "":
        filelocation.set("%s/SISA/" % filedir)
        # create the top level installation folder
        os.makedirs("%s/SISA" % filedir)
        # create the Dependencies folder
        os.makedirs("%s/SISA/Dependencies" % filedir)
        # create the Images folder
        os.makedirs("%s/SISA/Images" % filedir)
        # create the ChromeDriver folder
        os.makedirs("%s/SISA/ChromeDriver" % filedir)
        # create the internal spatial data store
        os.makedirs("%s/SISA/SpatialDataStore" % filedir)
        # create the HTMLFiles folder
        os.makedirs("%s/SISA/HTMLFiles" % filedir)
        # create the SpatialDataStore
        os.makedirs("%s/SISA/SpatialDataStore" % filedir)

    else:
        filedir = "C:/Users/fancourtm/Desktop/testdownload"

def download():
    global filedir

    APIkey = simpledialog.askstring("API Key", "API Key Please: ", parent=mainframe)

    dbx = dropbox.Dropbox('%s' % APIkey)

    downloadstatus.set("Downloading libaries")
    # download Dependencies to correct location
    for entry in dbx.files_list_folder("/Dependencies").entries:
        print(entry.name)
        dbx.files_download_to_file(path="/Dependencies/%s" % entry.name, download_path="%s/SISA/Dependencies/%s" % (filedir, entry.name))

    downloadstatus.set("Libaries Downloaded")
    root.update()
    time.sleep(0.5)
    downloadstatus.set("Images Downloading")
    root.update()

    # download the images to the correct location
    for entry in dbx.files_list_folder("/Images").entries:
        print(entry.name)
        dbx.files_download_to_file(path="/Images/%s" % entry.name, download_path="%s/SISA/Images/%s" % (filedir, entry.name))

    downloadstatus.set("Images Downloaded")
    root.update()
    time.sleep(0.5)
    downloadstatus.set("ChromeDriver Downloading")
    root.update()

    # download the chromedriver
    for entry in dbx.files_list_folder("/ChromeDriver").entries:
        print(entry.name)
        dbx.files_download_to_file(path="/ChromeDriver/%s" % entry.name, download_path="%s/SISA/ChromeDriver/%s" % (filedir, entry.name))

    downloadstatus.set("Chromedriver Downloaded")
    root.update()
    time.sleep(0.5)
    downloadstatus.set("Downloading HTML Files")

    # download the HTMLFIles
    for entry in dbx.files_list_folder("/HTMLFiles").entries:
        print(entry.name)
        dbx.files_download_to_file(path="/HTMLFiles/%s" % entry.name, download_path="%s/SISA/HTMLFiles/%s" % (filedir, entry.name))

    downloadstatus.set("HTML Files Downloaded")
    root.update()
    time.sleep(0.5)
    downloadstatus.set("Downloading Complete")

    # TO DO
    # download the Review Assistant python script and then place a .BAT file on the


def install():
    global filedir

    # first ensure that wheel is installed for python
    subprocess.Popen('cmd.exe /C pip install wheel')

    # then install GDAL
    subprocess.Popen('cmd.exe /C pip install %s/SISA/Dependencies/GDAL-2.2.4-cp36-cp36m-win32.whl' % filedir)

    # then install Fiona
    subprocess.Popen('cmd.exe /C pip install %s/SISA/Dependencies/Fiona-1.7.11.post1-cp36-cp36m-win32.whl' % filedir)

    # then install Shapely
    subprocess.Popen('cmd.exe /C pip install %s/SISA/Dependencies/Shapely-1.6.4.post1-cp36-cp36m-win32.whl' % filedir)

    # then install the rest according to the provided requirements txt that ships with download
    subprocess.Popen('cmd.exe /K pip install -r C:\\Users\\fancourtm\\Desktop\\testdownload\\SISA\\Dependencies\\requirements.txt')

# create the installer GUI
root = Tk()
root.title("SIS Assistant Installer")
root.resizable(width=False, height=False)

# create stringvars needed
filelocation = StringVar()
filelocation.set("Install Path Not Set")
downloadstatus = StringVar()
downloadstatus.set("Pending")

# setup style for tbe GUI
style = ttk.Style()
style.configure("TFrame", background="#DFE8F6")

# place the window in the middle of the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry('%dx%d+%d+%d' % (510, 510, screen_width/2 - 510/2, screen_height/2 - 510/2))

# mainframe
mainframe = ttk.Frame(root, padding="0 0 0 0")
Grid.rowconfigure(root, 0, weight=1)
Grid.columnconfigure(root, 0, weight=1)
mainframe.grid(column=0, row=0, sticky=N+S+E+W)
mainframe.master.minsize(width=510, height=510)

# Labels
ttk.Label(mainframe, text="SIS Assistant Installer", font=(None, 15), background="#DFE8F6").grid(column=1, row=0)
ttk.Label(mainframe, text="Step 1. Select Install Location", font=(None, 12), background="#DFE8F6").grid(column=1, row=1)
ttk.Label(mainframe, textvariable=filelocation, font=(None, 10), background="#DFE8F6").grid(column=1, row=3)
ttk.Label(mainframe, text="Step 2. Download Required Files", font=(None, 12), background="#DFE8F6").grid(column=1, row=5)
ttk.Label(mainframe, textvariable=downloadstatus, font=(None, 10), background="#DFE8F6").grid(column=1, row=7)
SolidDown = PhotoImage(file="C:\\Users\\fancourtm\\PycharmProjects\\SISA\\Images\\SolidDown.png")
ttk.Label(mainframe, image=SolidDown).grid(column=1, row=10)

# buttons
setinstalldirbutton = ttk.Button(mainframe, text="Select", command=lambda: setinstalldir())
setinstalldirbutton.grid(column=1, row=4)
downloadbutton = ttk.Button(mainframe, text="Select", command=lambda: download())
downloadbutton.grid(column=1, row=8)
installbutton = ttk.Button(mainframe, text="Install", command=lambda: install())
installbutton.grid(column=1, row=9)

# final buffer tidy up
mainframe.columnconfigure((0, 1, 2), weight=1)
mainframe.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# start the mainloop
root.mainloop()



