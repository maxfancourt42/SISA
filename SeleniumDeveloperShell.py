from selenium import webdriver
import os
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

# workaround for sendkeys
def sendkeyschecker(element, texttosend):
    while element.get_attribute('value') != texttosend:
        word = list(texttosend)
        element.clear()
        for x in word:
            element.send_keys(x)

# auto login function
def login():
    global passwordvariable
    global usernamevariable
    # get username from the user
    usernamevariable = simpledialog.askstring("Username", "Username please: ", parent=mainframe)
    if usernamevariable == None:
        usernamevariable = "max.fancourt@iucn.org"

    # place the password dialogbox
    passwordvariable = simpledialog.askstring("Password", "Password please: ", parent=mainframe, show="*")
    if passwordvariable == None:
        passwordvariable = "b1IXIYRyPODHe2123Zhu9tFD2331FF"

    # navigate to training homepage
    try:
        #driver.get("http://train.iucnsis.org/apps/org.iucn.sis.server/SIS/index.html#")
        driver.implicitly_wait(5)
        driver.get("http://sis.iucnsis.org/apps/org.iucn.sis.server/SIS/index.html")

        # find username and password boxes, inset details, press login button and report success
        username = driver.find_element_by_id('x-auto-17-input')
        username.clear()
        username.send_keys(usernamevariable)
        sendkeyschecker(username, str(usernamevariable))

        password = driver.find_element_by_id('x-auto-18-input')
        password.clear()
        password.send_keys(passwordvariable)
        sendkeyschecker(password, str(passwordvariable))

        driver.find_element_by_xpath('//*[@id="x-auto-19"]/tbody/tr[2]/td[2]/em/button').click()

        # set SIS up so that it searches entire taxonomy
        # reset to home page
        driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel").click()

        # open advanced search box
        driver.find_element_by_xpath("//*[contains(text(), 'Advanced Search')]").click()

        # select the Search All taxonomy levels button (training SIS)
        # driver.execute_script("arguments[0].click();", driver.find_element_by_id('gwt-uid-15'))
        # select the Search All taxonomy levels button (live SIS)
        driver.execute_script("arguments[0].click();", driver.find_element_by_id('gwt-uid-11'))

        # close the advanced search box
        driver.find_element_by_css_selector('.x-nodrag.x-tool-close.x-tool.x-component').click()

    except NoSuchElementException:
        messagebox.showerror("An Error Has Occurred", "Password or Username incorrect, please try again")
        pass

# function being tested
def testfunction():
    # navigate to the map page
    list = driver.find_elements_by_class_name("gwt-ListBox")[1]
    # find the drop down menu and get its current option
    select = Select(list)
    selected_option = select.first_selected_option
    print(selected_option.text)

    # find out if the data sensitive check box has been selected
    checkbox = driver.find_element_by_class_name("gwt-CheckBox")
    checkbox2 = checkbox.find_element_by_tag_name("input")
    print(checkbox2.is_selected())

# get the directory from which the python file is running
filedir = os.path.dirname(__file__)

# function declarations
# setup the webdriver
options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : '{}'.format(os.path.expanduser("~\Desktop\AttachmentDownload"))}
options.add_experimental_option('prefs', prefs)
options.add_argument('--lang=en-GB')
options.add_argument('--disable-infobars')

driver = webdriver.Chrome(executable_path='%s\ChromeDriver\chromedriver.exe' % filedir, options=options)

# create basic GUI with a button to trigger
root = tk.Tk()
root.title("SIS Assistant")
root.resizable(width=tk.TRUE, height=tk.TRUE)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry('%dx%d+%d+%d' % (510, 510, screen_width - 535, 5))
root.update()

# maximise window briefly to get the maximum window size
driver.set_window_position(0, 0)
driver.maximize_window()

browserdimensions = driver.get_window_size()

# setup the webdriver window correctly.
driver.set_window_size((browserdimensions['width'] - 450), browserdimensions['height']-20)

# create mainframe
mainframe = tk.Frame(root)
mainframe.grid(column=0, row=0, sticky=tk.NSEW)
mainframe.master.minsize(width=510, height=510)
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

button = tk.Button(mainframe, text="Press Me", command=lambda: testfunction())
button.grid(row=0, column=0)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

driver.get("http://sis.iucnsis.org/apps/org.iucn.sis.server/SIS/index.html")

login()

root.mainloop()
