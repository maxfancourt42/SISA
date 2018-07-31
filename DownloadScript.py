import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog

import os
import time
import subprocess

# install dropbox before anything nothing can be downloaded
subprocess.Popen('cmd.exe /C pip install dropbox')

import dropbox

# asks the user to choose the install directory and then creates the empty file structure within
def setinstalldir():
    global filedir
    # ask the user where they want to install SISA
    filedir = tkinter.filedialog.askdirectory()

    filelocation.set("%s/SISA/" % filedir)
    # create the top level installation folder
    os.makedirs("%s/SISA" % filedir)
    # create the Dependencies folder
    os.makedirs("%s/SISA/Dependencies" % filedir)
    # create the TempFiles folder
    os.makedirs("%s/SISA/TempFiles" % filedir)
    # create the Images folder
    os.makedirs("%s/SISA/Images" % filedir)
    # create the ChromeDriver folder
    os.makedirs("%s/SISA/ChromeDriver" % filedir)
    # create the internal spatial data store
    os.makedirs("%s/SISA/SpatialDataStore" % filedir)
    # create the HTMLFiles folder
    os.makedirs("%s/SISA/HTMLFiles" % filedir)
    # create the ReviewDirections folder
    os.makedirs("%s/SISA/ReviewDirections" % filedir)


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
    downloadstatus.set("Downloading ReviewDirections Files")

    # download the ReviewDirections
    for entry in dbx.files_list_folder("/ReviewDirections").entries:
        print(entry.name)
        dbx.files_download_to_file(path="/ReviewDirections/%s" % entry.name, download_path="%s/SISA/ReviewDirections/%s" % (filedir, entry.name))

    downloadstatus.set("ReviewDirections Downloaded")
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
    print("logo.ico")
    downloadstatus.set("Downloading Loose Files")
    dbx.files_download_to_file(path="/logo.ico", download_path="%s/SISA/logo.ico" % (filedir))
    print("ReviewAssistant.py")
    dbx.files_download_to_file(path="/ReviewAssistant.py", download_path="%s/SISA/ReviewAssistant.py" % (filedir))
    print("VersionNumber.txt")
    dbx.files_download_to_file(path="/VersionNumber.txt", download_path="%s/SISA/VersionNumber.txt" % (filedir))
    print("APIkey.txt")
    dbx.files_download_to_file(path="/APIkey.txt", download_path="%s/SISA/APIkey.txt" % (filedir))

    downloadstatus.set("Downloading Complete")
    root.update()


def install():
    global filedir

    installstatus.set("Installing Pip wheel")
    root.update()
    time.sleep(0.5)

    # first ensure that wheel is installed for python
    subprocess.Popen('cmd.exe /C pip install wheel')

    installstatus.set("Installing GDAL")
    root.update()
    time.sleep(0.5)

    # then install GDAL
    subprocess.Popen('cmd.exe /C pip install %s/SISA/Dependencies/GDAL-2.2.4-cp36-cp36m-win32.whl' % filedir)

    installstatus.set("Installing Fiona")
    root.update()
    time.sleep(0.5)

    # then install Fiona
    subprocess.Popen('cmd.exe /C pip install %s/SISA/Dependencies/Fiona-1.7.11.post1-cp36-cp36m-win32.whl' % filedir)

    installstatus.set("Installing Shapely")
    root.update()
    time.sleep(0.5)

    # then install Shapely
    subprocess.Popen('cmd.exe /C pip install %s/SISA/Dependencies/Shapely-1.6.4.post1-cp36-cp36m-win32.whl' % filedir)

    installstatus.set("Installing Other required libaries")
    root.update()
    time.sleep(0.5)

    # then install the rest according to the provided requirements txt that ships with download
    subprocess.Popen('cmd.exe /C pip install -r %s/SISA/Dependencies/requirements.txt' % filedir)

    installstatus.set("Installation Complete")
    root.update()
    time.sleep(0.5)

# create the installer GUI
root = Tk()
root.title("SIS Assistant Installer")
root.resizable(width=False, height=False)

# create stringvars needed
filelocation = StringVar()
filelocation.set("Install Path Not Set")
downloadstatus = StringVar()
downloadstatus.set("Pending")
installstatus = StringVar()
installstatus.set("Pending")


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
ttk.Label(mainframe, textvariable=filelocation, font=(None, 10), background="#DFE8F6").grid(column=1, row=2)
ttk.Label(mainframe, text="Step 2. Download Required Files", font=(None, 12), background="#DFE8F6").grid(column=1, row=5)
ttk.Label(mainframe, textvariable=downloadstatus, font=(None, 10), background="#DFE8F6").grid(column=1, row=6)
ttk.Label(mainframe, text="Step 3. Install Python Libaries", font=(None, 12), background="#DFE8F6").grid(column=1, row=8)
ttk.Label(mainframe, textvariable=installstatus, font=(None, 10), background="#DFE8F6").grid(column=1, row=9)


# buttons
setinstalldirbutton = ttk.Button(mainframe, text="Select", command=lambda: setinstalldir())
setinstalldirbutton.grid(column=1, row=3)
downloadbutton = ttk.Button(mainframe, text="Download", command=lambda: download())
downloadbutton.grid(column=1, row=7)
installbutton = ttk.Button(mainframe, text="Install", command=lambda: install())
installbutton.grid(column=1, row=10)

# final buffer tidy up
mainframe.columnconfigure((0, 1, 2), weight=1)
mainframe.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# start the mainloop
root.mainloop()



