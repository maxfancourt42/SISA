# version 5.1

# import the libaries needed
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains

import csv
import os
import time
import urllib.request

import datetime
import webbrowser
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter.scrolledtext import ScrolledText

# get the directory from which the python file is running
filedir = os.path.dirname(__file__)

print(filedir)

# function declarations
# setup the webdriver
options = webdriver.ChromeOptions()
options.add_argument('--lang=en-GB')
options.add_argument('--disable-infobars')

driver = webdriver.Chrome(executable_path='%s\ChromeDriver\chromedriver.exe' % filedir, chrome_options=options)

# workaround for sendkeys
def sendkeyschecker(element, texttosend):
    while element.get_attribute('value') != texttosend:
        word = list(texttosend)
        element.clear()
        for x in word:
            element.send_keys(x)

# binary search algorithm searches for a needle in a haystack
def binary_search(haystack, preneedle):
    min = 0
    max = len(haystack) - 1

    tosearchfor = str.lower(preneedle)
    needle = ""
    for x in tosearchfor:
        a = (ord(x) - 87)
        needle = needle + str(a)

    while True:
        if max < min:
            return -1

        test = ((min + max)//2)
        if haystack.iat[test, 0] < int(needle):
            min = test + 1
        elif haystack.iat[test, 0] > int(needle):
            max = test - 1
        else:
            return haystack.iat[test, 2]

# function to log in and set SIS up for use
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
        passwordvariable = "y54*RlcsPSQHlKQ"

    # navigate to training homepage
    try:
        #driver.get("http://train.iucnsis.org/apps/org.iucn.sis.server/SIS/index.html#")
        driver.implicitly_wait(10)
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

        # deactivate the login button, and renable the other buttons
        loginbutton.configure(state=DISABLED)
        searchbyanythingbutton.configure(state=NORMAL)
        species_name_entry.configure(state=NORMAL)
        logoutbutton.configure(state=NORMAL)
        taxadderframebutton.configure(state=NORMAL)
        singlereviewbutton.configure(state=DISABLED)
        simplesearchbutton.configure(state=NORMAL)

    except NoSuchElementException:
        messagebox.showerror("Generic Error Llama", "Password or Username incorrect, please try again")
        pass

    hideall()

# function to log out of SIS and prompt login again
def logout():
    driver.find_element_by_xpath('//*[@id="x-auto-223"]').click()
    driver.find_element_by_xpath("//*[contains(text(), 'Yes')]").click()
    loginbutton.configure(state=NORMAL)

    # disable all the other buttons
    species_name_entry.configure(state=DISABLED)
    searchbyanythingbutton.configure(state=DISABLED)
    singlereviewbutton.configure(state=DISABLED)
    simplesearchbutton.configure(state=DISABLED)
    taxadderframebutton.configure(state=DISABLED)
    logoutbutton.configure(state=DISABLED)

# function to search for a species using ID
def searchbyanything(value):
    # go back to the homepage
    resetimage = driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel")
    driver.execute_script("arguments[0].click();", resetimage)

    # test to see if ID has been given, if so just search for it
    if any(char.isdigit() for char in value):
        # open advanced search box
        driver.find_element_by_xpath("//*[contains(text(), 'Advanced Search')]").click()

        # find searchbox
        searchbox = driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".gwt-TextBox")

        # send the search term
        searchbox.clear()
        searchbox.send_keys("%s" % value)
        sendkeyschecker(searchbox, str(value))
        time.sleep(1)

        # search for the search button and click it
        driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".x-btn-text").click()
        time.sleep(3)
        return

    else:
        # go back to the homepage
        resetimage = driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel")
        driver.execute_script("arguments[0].click();", resetimage)
        # open advanced search box
        driver.find_element_by_xpath("//*[contains(text(), 'Advanced Search')]").click()
        # find searchbox
        searchbox = driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".gwt-TextBox")
        # send the search term
        searchbox.clear()
        searchbox.send_keys("%s" % value)
        sendkeyschecker(searchbox, str(value))
        time.sleep(1)

        driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".x-btn-text").click()
        time.sleep(3)

        # first of all find the number of pages to be searched
        numberofpagestext = driver.find_elements_by_css_selector(".my-paging-text.x-component")
        numberofpages = int(numberofpagestext[3].text.split()[1])

        # create a list of all search results use the number of pages to bound the for loop
        for x in range(0, numberofpages):
            driver.implicitly_wait(0)
            potentiallist = driver.find_elements_by_css_selector(".search_result_taxon_default")
            # loop through the results on the page
            for x in potentiallist:
                # compare text with value searched (case sensitive) if found click, else pass
                if x.text == value:
                   x.click()
                   return 1
            # if page has been searched then advance to the next page and try again
            try:
                potentiallist2 = driver.find_elements_by_css_selector(".x-btn-image")
                potentiallist2[9].click()
                potentiallist.clear()
            except:
                print("can't press button")
                break
        # if after searching all the pages it hasn't been found then return not found (0)
        return 0

# this function takes input from the database and queries SIS for the species, it then navigates to that page
def tablesearch():
    # go back to the homepage
    resetimage = driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel")
    driver.execute_script("arguments[0].click();", resetimage)
    # get the search term
    value = species_ID.get()

    # test to see if ID has been given, if so just search for it
    if any(char.isdigit() for char in value):
        driver.implicitly_wait(5)
        # open advanced search box
        driver.find_element_by_xpath("//*[contains(text(), 'Advanced Search')]").click()
        # find searchbox
        searchbox = driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".gwt-TextBox")
        # send the search term
        searchbox.clear()
        searchbox.send_keys("%s" % value)
        sendkeyschecker(searchbox, str(value))
        # search for the search button and click it
        driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".x-btn-text").click()
        return

    else:
        driver.implicitly_wait(5)
        # open advanced search box
        driver.find_element_by_xpath("//*[contains(text(), 'Advanced Search')]").click()
        # find searchbox
        searchbox = driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".gwt-TextBox")
        # send the search term
        searchbox.clear()
        searchbox.send_keys("%s" % value)
        sendkeyschecker(searchbox, str(value))
        time.sleep(1)
        # search for it
        driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".x-btn-text").click()
        time.sleep(3)
        # try first element found, click on it
        try:
            print("llama")
            check = driver.find_element_by_xpath("//*[contains(text(), '%s')]" % value)
            checktext = check.text
            if checktext == value:
                check.click()
            else:
                raise WebDriverException

        except WebDriverException:
            for x in range(2, 1000):
                print("llama%i" % x)
                try:
                    check2 = driver.find_element_by_xpath("(//*[contains(text(), '%s')])[position()='%d']" % (value, x))
                    checktext2 = check2.text
                    if checktext2 == value:
                        check2.click()
                        break

                except NoSuchElementException:
                    messagebox.showerror("There's a llama afoot", "unable to find species")
                    driver.find_element_by_css_selector(".x-nodrag.x-tool-close.x-tool.x-component").click()
                    break

                except WebDriverException:
                    print("llamanoisedetected")
                    pass

# function to change the text of a button
def buttonchanger(button, text):
    try:
        if button == "SISKingdomSV":
            SISKingdomSV.set("%s" % text)
        elif button == "SISPhylumSV":
            SISPhylumSV.set("%s" % text)
        elif button == "SISClassSV":
            SISClassSV.set("%s" % text)
        elif button == "SISOrderSV":
            SISOrderSV.set("%s" % text)
        elif button == "SISFamilySV":
            SISFamilySV.set("%s" % text)
        elif button == "SISGenusSV":
            SISGenusSV.set("%s" % text)
        elif button == "SISSpeciesSV":
            SISSpeciesSV.set("%s" % text)
        # elif button == "SISInfrarankSV":
            # taxlabel26SV.set("%s" % text)
        elif button == "userKingdomSV":
            userKingdomSV.set("%s" % text)
        elif button == "userPhylumSV":
            userPhylumSV.set("%s" % text)
        elif button == "userClassSV":
            userClassSV.set("%s" % text)
        elif button == "userOrderSV":
            userOrderSV.set("%s" % text)
        elif button == "userFamilySV":
            userFamilySV.set("%s" % text)
        elif button == "userGenusSV":
            userGenusSV.set("%s" % text)
        elif button == "userSpeciesSV":
            userSpeciesSV.set("%s" % text)
        # elif button == "userInfrarankSV":
            # userInfrarankSV.set("%s" % text)

        else:
           pass

    except:
        print("error")

# resets the taxonomic checker
def taxonomiccheckerrest():
    # SIS bankbone
    # labels
    SISKingdomSV.set("SISKingdom")
    SISPhylumSV.set("SISPhylum")
    SISClassSV.set("SISClass")
    SISOrderSV.set("SISOrder")
    SISFamilySV.set("SISFamily")
    SISGenusSV.set("SISGenus")
    SISSpeciesSV.set("SISSpecies")
    # userInfrarankSV.set("Infrarank"

    # arrows
    SISKParrow.config(image=SolidDown)
    SISPCarrow.config(image=SolidDown)
    SISCOarrow.config(image=SolidDown)
    SISOFarrow.config(image=SolidDown)
    SISFGarrow.config(image=SolidDown)
    SISGSarrow.config(image=SolidDown)

    # cross arrows
    # arrows
    KPcrossarrow.config(image=Blank)
    PCcrossarrow.config(image=Blank)
    COcrossarrow.config(image=Blank)
    OFcrossarrow.config(image=Blank)
    FGcrossarrow.config(image=Blank)
    GScrossarrow.config(image=Blank)

    # user data
    # arrows
    KParrow.config(image=Blank)
    PCarrow.config(image=Blank)
    COarrow.config(image=Blank)
    OFarrow.config(image=Blank)
    FGarrow.config(image=Blank)
    GSarrow.config(image=Blank)

    # labels
    userKingdomSV.set("Kingdom (K)")
    userPhylumSV.set("Phylum (P)")
    userClassSV.set("Class (C)")
    userOrderSV.set("Order (O)")
    userFamilySV.set("Family (F)")
    userGenusSV.set("Genus (G)")
    userSpeciesSV.set("Species (S)")
    # userInfrarankSV.set("Infrarank")

    # reset the detail boxes
    kingdomdetails.grid_forget()
    phylumdetails.grid_forget()
    classdetails.grid_forget()
    orderdetails.grid_forget()
    familydetails.grid_forget()
    genusdetails.grid_forget()
    speciesdetails.grid_forget()

    # add to workingset button
    addtoworkingsetbutton.grid_forget()

# function to arrange all graphical arrows after taxonomy has been checked
def arrowsorter():
    # create flags for checking
    global sisflag
    global userflag

    sisflag = 0
    userflag = 0

    # test to detect if something is only being shown to illustrate
    # reset all arrows to default
    # arrows
    SISKParrow.config(image=SolidDown)
    SISPCarrow.config(image=SolidDown)
    SISCOarrow.config(image=SolidDown)
    SISOFarrow.config(image=SolidDown)
    SISFGarrow.config(image=SolidDown)
    SISGSarrow.config(image=SolidDown)

    # cross arrows
    # arrows
    KPcrossarrow.config(image=Blank)
    PCcrossarrow.config(image=Blank)
    COcrossarrow.config(image=Blank)
    OFcrossarrow.config(image=Blank)
    FGcrossarrow.config(image=Blank)
    GScrossarrow.config(image=Blank)

    # user data
    # arrows
    KParrow.config(image=Blank)
    PCarrow.config(image=Blank)
    COarrow.config(image=Blank)
    OFarrow.config(image=Blank)
    FGarrow.config(image=Blank)
    GSarrow.config(image=Blank)

    # Hide all detail boxes
    kingdomdetails.grid_forget()
    phylumdetails.grid_forget()
    classdetails.grid_forget()
    orderdetails.grid_forget()
    familydetails.grid_forget()
    genusdetails.grid_forget()
    speciesdetails.grid_forget()

    # loop through the SIS backbone, if next one is blank put the above and below arrow as blank
    if SISKingdomSV.get() == "":
        SISKParrow.config(image=Blank)
        kingdomdetails.grid(column=3, row=4)
    if SISPhylumSV.get() == "":
        SISPCarrow.config(image=Blank)
        SISKParrow.config(image=Blank)
        phylumdetails.grid(column=3, row=6)
    if SISClassSV.get() == "":
        SISCOarrow.config(image=Blank)
        SISPCarrow.config(image=Blank)
        classdetails.grid(column=3, row=8)
    if SISOrderSV.get() == "":
        SISOFarrow.config(image=Blank)
        SISCOarrow.config(image=Blank)
        orderdetails.grid(column=3, row=10)
    if SISFamilySV.get() == "":
        SISFGarrow.config(image=Blank)
        SISOFarrow.config(image=Blank)
        familydetails.grid(column=3, row=12)
    if SISGenusSV.get() == "":
        SISGSarrow.config(image=Blank)
        SISFGarrow.config(image=Blank)
        genusdetails.grid(column=3, row=14)
    if SISSpeciesSV.get() == "":
        speciesdetails.grid(column=3, row=16)
        SISGSarrow.config(image=Blank)

    # loop through the user input if not blank then mark cross arrow as potential.
    if userPhylumSV.get() != "" and SISPhylumSV.get() == "":
        KPcrossarrow.config(image=leftorightpotential)
        userflag = 1
    else:
        userflag = 0

    if userClassSV.get() != "" and SISClassSV.get() == "":
        if userflag == 1:
            PCarrow.config(image=DownPossible)
        else:
            PCcrossarrow.config(image=leftorightpotential)
            userflag = 1
    else:
        userflag = 0

    if userOrderSV.get() != "" and SISOrderSV.get() == "":
        if userflag == 1:
            COarrow.config(image=DownPossible)
        else:
            COcrossarrow.config(image=leftorightpotential)
            userflag = 1
    else:
        userflag = 0

    if userFamilySV.get() != "" and SISFamilySV.get() == "":
        if userflag == 1:
            OFarrow.config(image=DownPossible)
        else:
            OFcrossarrow.config(image=leftorightpotential)
            userflag = 1
    else:
        userflag = 0

    if userGenusSV.get() != "" and SISGenusSV.get() == "":
        if userflag == 1:
            FGarrow.config(image=DownPossible)
        else:
            FGcrossarrow.config(image=leftorightpotential)
            userflag = 1
    else:
        userflag = 0

    if userSpeciesSV.get() != "" and SISSpeciesSV.get() == "":
        if userflag == 1:
            GSarrow.config(image=DownPossible)
        else:
            GScrossarrow.config(image=leftorightpotential)
            userflag = 1
    else:
        userflag = 0

# function to remove duplicates from the tax tree
def duplicateremover():
    if SISKingdomSV.get() == userKingdomSV.get():
        buttonchanger("userKingdomSV", "")
    if SISPhylumSV.get() == userPhylumSV.get():
        buttonchanger("userPhylumSV", "")
    if SISClassSV.get() == userClassSV.get():
        buttonchanger("userClassSV", "")
    if SISOrderSV.get() == userOrderSV.get():
        buttonchanger("userOrderSV", "")
    if SISFamilySV.get() == userFamilySV.get():
        buttonchanger("userFamilySV", "")
    if SISGenusSV.get() == userGenusSV.get():
        buttonchanger("userGenusSV", "")
    if SISSpeciesSV.get() == userSpeciesSV.get():
        buttonchanger("userSpeciesSV", "")
    # clear up any of the base SIS flags
    if SISKingdomSV.get() == "SISKingdom":
        buttonchanger("SISKingdomSV", "")
    if SISPhylumSV.get() == "SISPhylum":
        buttonchanger("SISPhylumSV", "")
    if SISClassSV.get() == "SISClass":
        buttonchanger("SISClassSV", "")
    if SISOrderSV.get() == "SISOrder":
        buttonchanger("SISOrderSV", "")
    if SISFamilySV.get() == "SISFamily":
        buttonchanger("SISFamilySV", "")
    if SISGenusSV.get() == "SISGenus":
        buttonchanger("SISGenusSV", "")
    if SISSpeciesSV.get() == "SISSpecies":
        buttonchanger("SISSpeciesSV", "")

# function to add species to working set
def addtoworkingset():
    global databaseta
    # reset to the homepage
    try:
        resetimage = driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel")
        driver.execute_script("arguments[0].click();", resetimage)
    except:
        messagebox.showerror("Generic Error Llama", "Unable to reset to homepage, try again")
        return 1
    try:
        # get row number
        rownumber = taxonomyrowtrackerIntVar.get()

        # get genus, species and workingset
        genus = databaseta.iat[rownumber, 10]
        species = databaseta.iat[rownumber, 12]
        workingset = databaseta.iat[rownumber, 18]

        # set implicit wait
        driver.implicitly_wait(5)
    except:
        messagebox.showerror("Generic Error Llama", "Unable to get data from database, try again")
        return 1


    # if yes then add the species to the indicated working set
    # first find the filter box at the top
    listoffilterboxes = driver.find_elements_by_css_selector(".x-form-empty-field")
    # clear and send working set name
    listoffilterboxes[0].clear()
    listoffilterboxes[0].send_keys(workingset)
    sendkeyschecker(listoffilterboxes[0], str(workingset))
    # the find and select element with the working set name and double click it
    actionChains = ActionChains(driver)
    actionChains.double_click(driver.find_element_by_xpath("//*[contains(text(), '%s')]" % workingset)).perform()
    # find and press taxa manager button
    driver.find_element_by_xpath("//*[contains(text(), 'Taxa Manager')]").click()
    # find the select species to add to working set button and click
    driver.find_elements_by_css_selector(".x-btn.float-left.x-component.x-btn-icon.x-unselectable")[0].click()
    # find the text box to input the binomial
    listoftextboxes = driver.find_elements_by_css_selector(".gwt-TextBox")
    listoftextboxes[2].clear()
    listoftextboxes[2].send_keys("%s %s" % (genus, species))
    sendkeyschecker(listoftextboxes[2], "%s %s" % (genus, species))
    # find the search button and click it
    listofsearchboxes = driver.find_elements_by_xpath("//*[contains(text(), 'Search')]")
    listofsearchboxes[1].click()
    # attempt to look for species, but if not found then report that it is already in the working set
    try:
        # find the item with the span text of the Genus Species Combination
        fulllist = driver.find_elements_by_css_selector(".search_result_taxon_default")
        # run through this list and click the one with the matching text
        for index, element in enumerate(fulllist):
            if fulllist[index].text == "%s %s" % (genus, species):
                element.click()
                break
        # finally press the add button
        driver.find_element_by_xpath("//*[contains(text(), 'Add')]").click()
        # and then the ok button
        driver.find_element_by_xpath("//*[contains(text(), 'OK')]").click()

    except:
        messagebox.showinfo("Species already in Working Set")
        listoffilterboxes[0].clear()
        addtoworkingsetbutton.grid_forget()
        return 0

    # clear the working set box for the next use
    listoffilterboxes[0].clear()

    # hide the "add to working set" button and replace with added text
    addtoworkingsetbutton.grid_forget()
    userFamilySV.set("Added to Working Set")
    taxlabel14.grid(columnspan=3)

    # changed the notes column to reflect this change
    databaseta.iat[rownumber, 20] = "Was already in SIS, added to working set"

# load user selected review data and then ready the review assistant
def loaddataandreadyreviewassistant():
    # prompt the user to open the csv they want to read from
    global databasera
    global fastreviewdirections

    try:
        # create the database for review assistant
        filenamera.set(filedialog.askopenfilename())
        databasera = pandas.read_excel((filenamera.get()), converters={'ID': int, 'Genus': str, 'Species': str,
                                                                   'Threat Category': str, 'Criteria String': str,
                                                                   'Criteria Passed?': str, 'Validity Passed?': str,
                                                                   'Map Passed?': str, 'Notes': str, 'Kingdom': str,
                                                                   'Phylum': str, 'Class': str, 'Order': str,
                                                                   'Family': str, 'Genus': str, 'Species': str,
                                                                   'Infrarank': str, 'Taxonomic Authority': str,
                                                                   'Taxonomic Reference': str, 'Working Set': str,
                                                                   'Assessment Passed?': str})
        databasera = databasera.fillna('')

        # reset the tablerow variable and click to start button to start from the beginning of the list
        tablerownumber.set(0)

        # ask the user if they want to load in a geodatebase with the maps set file pointer to it if they do
        if messagebox.askyesnocancel(title="Open Maps", message="Do you have any maps for this working set?") == True:
            locationofmaps.set(filedialog.askdirectory())

        # activate table button
        simplesearchbutton.configure(state=NORMAL)

        # undertake the special update function to setup the page ready for reviewing
        # get current value of the rowtracker
        rownumber = (tablerownumber.get())

        # Get the current species genus and name from the table and the species ID
        output = databasera.iat[rownumber, 1]
        output2 = databasera.iat[rownumber, 2]
        speciesID = databasera.iat[rownumber,0]

        # Get the correct Category and criteria from the table
        candcouput1 = databasera.iat[rownumber, 3]
        candcoutput2 = databasera.iat[rownumber, 4]

        # check to ensure that the database is still in the scope of the underlying database
        if rownumber - 1 <= 0:
            previousspeciesoutput = ""
            previousspeciesoutput2 = ""

            nextspeciesoutput = databasera.iat[rownumber + 1, 1]
            nextspeciesoutput2 = databasera.iat[rownumber + 1, 2]

            goback.config(state='disabled')

        elif rownumber + 1 >= len(databasera):
            previousspeciesoutput = databasera.iat[rownumber - 1, 1]
            previousspeciesoutput2 = databasera.iat[rownumber - 1, 2]

            nextspeciesoutput = ""
            nextspeciesoutput2 = ""

            goforward.config(state='disabled')

        else:
            previousspeciesoutput = databasera.iat[rownumber - 1, 1]
            previousspeciesoutput2 = databasera.iat[rownumber - 1, 2]

            nextspeciesoutput = databasera.iat[rownumber + 1, 1]
            nextspeciesoutput2 = databasera.iat[rownumber + 1, 2]

            goback.config(state='normal')
            goforward.config(state='normal')

        # then set the value of the external rowtracker to the new value
        currentspeciesname.set("%s %s" % (output, output2))
        previousspecies.set("%s %s" % (previousspeciesoutput, previousspeciesoutput2))
        nextspecies.set("%s %s" % (nextspeciesoutput, nextspeciesoutput2))
        candc.set("%s %s" % (candcouput1, candcoutput2))

        # make the page navigation buttons disappear
        generatetemplatebutton.grid_forget()
        populatebutton.grid_forget()
        reviewassistantmenu.grid_forget()
        continuewhereyouleft.grid_forget()

        # make the navigate buttons appear
        goforward.grid(column=2, row=11, sticky=S)
        goback.grid(column=0, row=11, sticky=S)

        # make the variable names appear
        previouspeciesvariable.grid(column=0, row=10)
        currentspeciesnamelabel.grid(column=1, row=1)
        candclabel.grid(column=1, row=2, sticky=N)
        nextspecieslabel.grid(column=2, row=10)
        textlabel1.grid(column=1, row=1, sticky=N)
        textlabel2.grid(column=0, row=9)
        textlabel3.grid(column=2, row=9)
        previouspeciesvariable.grid(column=0, row=10)
        currentspeciesnamelabel.grid(column=1, row=1)
        nextspecieslabel.grid(column=2, row=10)
        textlabel5.grid(column=0, row=4, sticky=E)
        textlabel4.grid(column=0, row=5, sticky=E)
        textlabel6.grid(column=0, row=6, sticky=E)
        textlabel7.grid(column=1, row=9)
        entryvariable1.grid(column=1, row=10)
        skiptobutton.grid(column=1, row=11)
        assessmentnumber.grid(column=2, row=1)
        criteriacheck.grid(column=1, row=4, sticky=E)
        verifiedcheck.grid(column=1, row=5, sticky=E)
        mapscheck.grid(column=1, row=6, sticky=E)
        notesbox.grid(row=7, column=0, columnspan=10, rowspan=2, sticky=NSEW)
        skiptobutton.grid(column=1, row=11)
        reviewtoolsbutton.grid(column=2, row=12, columnspan=2)

        # call the search function to look for that species ID
        species_ID.set(speciesID)
        tablesearch()

        # load the species data if it has any else set to defaults
        reviewload()

        # update the progress number
        databaselength.set(str(tablerownumber.get() + 1) + ' of ' + str(len(databasera)))

        # open the tool menu
        createtoolwindow()

        # load the fastdirections file
        fastreviewdirections = pandas.read_csv("%s\\ReviewDirections\\fastreviewdirections.csv" % filedir)

    except:
        messagebox.showerror("There's a llama afoot", "please select a file to load")

# load user selected taxonomic file and then ready the taxonomic assistant
def loaddataandreadytaxassistant():
    # prompt the user to open the csv they want to read from
    global databaseta

    #try:
    # create the database for review assistant
    filenameta.set(filedialog.askopenfilename())
    databaseta = pandas.read_excel((filenameta.get()), converters={'Kingdom': str, 'KCheck': str, 'Phylum': str,
                                                                   'PCheck': str, 'Class': str, 'CCheck': str,
                                                                   'Order': str, 'OCheck': str, 'Family': str,
                                                                   'FCheck': str, 'Genus': str, 'GCheck': str,
                                                                   'Species': str, 'SCheck': str, 'Infrarank': str,
                                                                   'ICheck': str, 'Taxonomic Authority': str,
                                                                   'Taxonomic Reference': str, 'Working Set': str,
                                                                   'Species Added?': str, 'Notes': str,
                                                                   'ID': int, 'Preprocessed?': int})
    # undertake data scrubbing
    databaseta[['Preprocessed?']] = databaseta[['Preprocessed?']].fillna(value=0)
    databaseta = databaseta.fillna("")

    # set the rowtracker to 0
    taxonomyrowtrackerIntVar.set(0)

    # reset the screen
    taxonomiccheckerrest()

    # if the notes field reads already in SIS then show add to working set button
    if databaseta.iat[0, 20] == "Already in SIS":
        # check to see if the next row has blank check values (look in kingdom box for a value)
        if databaseta.iat[taxonomyrowtrackerIntVar.get(), 22] == 0:
            preprocess()
            taxsave()

        # load the user data for the first species
        userKingdomSV.set("%s" % databaseta.iat[0, 0])
        userPhylumSV.set("%s" % databaseta.iat[0, 2])
        userClassSV.set("%s" % databaseta.iat[0, 20])
        taxlabel12.grid(columnspan=3)
        taxlabel12.config(wraplength=250)
        addtoworkingsetbutton.grid(column=2, row=12, columnspan=3)
        userOrderSV.set("%s" % databaseta.iat[0, 6])
        userFamilySV.set("%s" % databaseta.iat[0, 8])
        userGenusSV.set("%s" % databaseta.iat[0, 10])
        userSpeciesSV.set("%s" % databaseta.iat[0, 12])
        # userInfrarankSV.set("%s" % databaseta.iat[0, 14])

        # if check value is 1, then put in the same value as database (as this indicates match), else put what SIS has
        if databaseta.iat[0, 1] == "M":
            SISKingdomSV.set("%s" % databaseta.iat[0, 0])
        else:
            SISKingdomSV.set("%s" % databaseta.iat[0, 1])
        if databaseta.iat[0, 3] == "M":
            SISPhylumSV.set("%s" % databaseta.iat[0, 2])
        else:
            SISPhylumSV.set("%s" % databaseta.iat[0, 3])
        if databaseta.iat[0, 5] == "M":
            SISClassSV.set("%s" % databaseta.iat[0, 4])
        else:
            SISClassSV.set("%s" % databaseta.iat[0, 5])
        if databaseta.iat[0, 7] == "M":
            SISOrderSV.set("%s" % databaseta.iat[0, 6])
        else:
            SISOrderSV.set("%s" % databaseta.iat[0, 7])
        if databaseta.iat[0, 9] == "M":
            SISFamilySV.set("%s" % databaseta.iat[0, 8])
        else:
            SISFamilySV.set("%s" % databaseta.iat[0, 9])
        if databaseta.iat[0, 11] == "M":
            SISGenusSV.set("%s" % databaseta.iat[0, 10])
        else:
            SISGenusSV.set("%s" % databaseta.iat[0, 11])
        if databaseta.iat[0, 13] == "M":
            SISSpeciesSV.set("%s" % databaseta.iat[0, 12])
        else:
            SISSpeciesSV.set("%s" % databaseta.iat[0, 13])
        #if databaseta.iat[rownumber, 15] == 0:
        #    SISInfrarankSV.set("%s" % databaseta.iat[rownumber, 14])

        CombinationStringVar.set("%s %s %s" % (databaseta.iat[0, 10], databaseta.iat[0, 12], databaseta.iat[0, 14]))
        copyname()
        duplicateremover()
        arrowsorter()

        # then set the value of the progress tracker to the new value
        taxonomicprogresstracker.set("%s of %s" % (taxonomyrowtrackerIntVar.get() + 1, len(databaseta)))

        # set the buttons up correctly
        # check to ensure that the database is still in the scope of the underlying database and change buttons accordingly
        previousspeciestax.config(state='normal')
        nextspeciestax.config(state='normal')
        if taxonomyrowtrackerIntVar.get() - 1 < 0:
            previousspeciestax.config(state='disabled')
        elif taxonomyrowtrackerIntVar.get() + 1 >= len(databaseta):
            nextspeciestax.config(state='disabled')

        # go to the taxonomic page
        gototaxspecial()
        root.update()

    # if not NO then check to see if notes column is blank, if not then show that
    elif databaseta.iat[0, 20] != "":
        # check to see if the row has blank check values
        if databaseta.iat[taxonomyrowtrackerIntVar.get(), 22] == 0:
            preprocess()
            taxsave()

        # load the user data for the first species
        userKingdomSV.set("%s" % databaseta.iat[0, 0])
        userPhylumSV.set("%s" % databaseta.iat[0, 2])
        userClassSV.set("%s" % databaseta.iat[0, 20])
        taxlabel12.grid(columnspan=3)
        taxlabel12.config(wraplength=250)
        userOrderSV.set("%s" % databaseta.iat[0, 6])
        userFamilySV.set("%s" % databaseta.iat[0, 8])
        userGenusSV.set("%s" % databaseta.iat[0, 10])
        userSpeciesSV.set("%s" % databaseta.iat[0, 12])
        # userInfrarankSV.set("%s" % databaseta.iat[0, 14])

        # if check value is 1, then put in the same value as database (as this indicates match), else put what SIS has
        if databaseta.iat[0, 1] == "M":
            SISKingdomSV.set("%s" % databaseta.iat[0, 0])
        else:
            SISKingdomSV.set("%s" % databaseta.iat[0, 1])
        if databaseta.iat[0, 3] == "M":
            SISPhylumSV.set("%s" % databaseta.iat[0, 2])
        else:
            SISPhylumSV.set("%s" % databaseta.iat[0, 3])
        if databaseta.iat[0, 5] == "M":
            SISClassSV.set("%s" % databaseta.iat[0, 4])
        else:
            SISClassSV.set("%s" % databaseta.iat[0, 5])
        if databaseta.iat[0, 7] == "M":
            SISOrderSV.set("%s" % databaseta.iat[0, 6])
        else:
            SISOrderSV.set("%s" % databaseta.iat[0, 7])
        if databaseta.iat[0, 9] == "M":
            SISFamilySV.set("%s" % databaseta.iat[0, 8])
        else:
            SISFamilySV.set("%s" % databaseta.iat[0, 9])
        if databaseta.iat[0, 11] == "M":
            SISGenusSV.set("%s" % databaseta.iat[0, 10])
        else:
            SISGenusSV.set("%s" % databaseta.iat[0, 11])
        if databaseta.iat[0, 13] == "M":
            SISSpeciesSV.set("%s" % databaseta.iat[0, 12])
        else:
            SISSpeciesSV.set("%s" % databaseta.iat[0, 13])
        #if databaseta.iat[rownumber, 15] == 0:
        #    SISInfrarankSV.set("%s" % databaseta.iat[rownumber, 14])

        CombinationStringVar.set("%s %s %s" % (databaseta.iat[0, 10], databaseta.iat[0, 12], databaseta.iat[0, 14]))
        copyname()
        duplicateremover()
        arrowsorter()

        # then set the value of the progress tracker to the new value
        taxonomicprogresstracker.set("%s of %s" % (taxonomyrowtrackerIntVar.get() + 1, len(databaseta)))

        # set the buttons up correctly
        # check to ensure that the database is still in the scope of the underlying database and change buttons accordingly
        previousspeciestax.config(state='normal')
        nextspeciestax.config(state='normal')
        if taxonomyrowtrackerIntVar.get() - 1 < 0:
            previousspeciestax.config(state='disabled')
        elif taxonomyrowtrackerIntVar.get() + 1 >= len(databaseta):
            nextspeciestax.config(state='disabled')

        # go to the taxonomic page
        gototaxspecial()
        root.update()

    # else set up as normal
    else:
        # load the user data for the first species
        userKingdomSV.set("%s" % databaseta.iat[0, 0])
        userPhylumSV.set("%s" % databaseta.iat[0, 2])
        userClassSV.set("%s" % databaseta.iat[0, 4])
        userOrderSV.set("%s" % databaseta.iat[0, 6])
        userFamilySV.set("%s" % databaseta.iat[0, 8])
        userGenusSV.set("%s" % databaseta.iat[0, 10])
        userSpeciesSV.set("%s" % databaseta.iat[0, 12])
        # userInfrarankSV.set("%s" % databaseta.iat[0, 14])

        # if check value is 1, then put in the same value as database (as this indicates match), else put what SIS has
        if databaseta.iat[0, 1] == "M":
            SISKingdomSV.set("%s" % databaseta.iat[0, 0])
        else:
            SISKingdomSV.set("%s" % databaseta.iat[0, 1])
        if databaseta.iat[0, 3] == "M":
            SISPhylumSV.set("%s" % databaseta.iat[0, 2])
        else:
            SISPhylumSV.set("%s" % databaseta.iat[0, 3])
        if databaseta.iat[0, 5] == "M":
            SISClassSV.set("%s" % databaseta.iat[0, 4])
        else:
            SISClassSV.set("%s" % databaseta.iat[0, 5])
        if databaseta.iat[0, 7] == "M":
            SISOrderSV.set("%s" % databaseta.iat[0, 6])
        else:
            SISOrderSV.set("%s" % databaseta.iat[0, 7])
        if databaseta.iat[0, 9] == "M":
            SISFamilySV.set("%s" % databaseta.iat[0, 8])
        else:
            SISFamilySV.set("%s" % databaseta.iat[0, 9])
        if databaseta.iat[0, 11] == "M":
            SISGenusSV.set("%s" % databaseta.iat[0, 10])
        else:
            SISGenusSV.set("%s" % databaseta.iat[0, 11])
        if databaseta.iat[0, 13] == "M":
            SISSpeciesSV.set("%s" % databaseta.iat[0, 12])
        else:
            SISSpeciesSV.set("%s" % databaseta.iat[0, 13])
        #if databaseta.iat[rownumber, 15] == 0:
        #    SISInfrarankSV.set("%s" % databaseta.iat[rownumber, 14])

        CombinationStringVar.set("%s %s %s" % (databaseta.iat[0, 10], databaseta.iat[0, 12], databaseta.iat[0, 14]))
        copyname()
        duplicateremover()
        arrowsorter()



        # then set the value of the progress tracker to the new value
        taxonomicprogresstracker.set("%s of %s" % (taxonomyrowtrackerIntVar.get() + 1, len(databaseta)))

        # set the buttons up correctly
        # check to ensure that the database is still in the scope of the underlying database and change buttons accordingly
        previousspeciestax.config(state='normal')
        nextspeciestax.config(state='normal')
        if taxonomyrowtrackerIntVar.get() - 1 < 0:
            previousspeciestax.config(state='disabled')
        elif taxonomyrowtrackerIntVar.get() + 1 >= len(databaseta):
            nextspeciestax.config(state='disabled')

        # go to the taxonomic page
        gototaxspecial()
        root.update()

    #except:
       # pass

# function to unhide the review assistant allowing the user to continue where they left off
def unhidereviewassistant():
    # make the page navigation buttons disappear
    generatetemplatebutton.grid_forget()
    populatebutton.grid_forget()
    reviewassistantmenu.grid_forget()
    continuewhereyouleft.grid_forget()

    # make the navigate buttons appear
    goforward.grid(column=2, row=11, sticky=S)
    goback.grid(column=0, row=11, sticky=S)

    # make the variable names appear
    previouspeciesvariable.grid(column=0, row=10)
    currentspeciesnamelabel.grid(column=1, row=1)
    candclabel.grid(column=1, row=2, sticky=N)
    nextspecieslabel.grid(column=2, row=10)
    textlabel1.grid(column=1, row=1, sticky=N)
    textlabel2.grid(column=0, row=9)
    textlabel3.grid(column=2, row=9)
    previouspeciesvariable.grid(column=0, row=10)
    currentspeciesnamelabel.grid(column=1, row=1)
    nextspecieslabel.grid(column=2, row=10)
    textlabel5.grid(column=0, row=4, sticky=E)
    textlabel4.grid(column=0, row=5, sticky=E)
    textlabel6.grid(column=0, row=6, sticky=E)
    textlabel7.grid(column=1, row=9)
    entryvariable1.grid(column=1, row=10)
    skiptobutton.grid(column=1, row=11)
    assessmentnumber.grid(column=2, row=1)
    criteriacheck.grid(column=1, row=4, sticky=E)
    verifiedcheck.grid(column=1, row=5, sticky=E)
    mapscheck.grid(column=1, row=6, sticky=E)
    notesbox.grid(row=7, column=0, columnspan=10, rowspan=2, sticky=NSEW)
    skiptobutton.grid(column=1, row=11)
    reviewtoolsbutton.grid(column=2, row=12, columnspan=2)

    # make the tool bar appear

# function to activate repopulate and return to the main menu
def specialreturntomain():
    global mainframe
    try:
        reviewsave()
        hideall()
    except:
        pass

    finally:
        mainframe.tkraise()
        hidetoolwindow()
        # refresh the page by clicking the SIS logo
        driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel").click()

# this function saves the state of the species
def reviewsave():
    global databasera
    rownumber = (tablerownumber.get())
    # write the current button values to the database
    databasera.iat[rownumber, 5] = criteria.get()
    databasera.iat[rownumber, 6] = verified.get()
    databasera.iat[rownumber, 7] = maps.get()

    # write the notes field to the database
    databasera.iat[rownumber, 8] = notesbox.get("1.0", "end-1c")

    # write the formula to the final column
    databasera.iat[rownumber, 9] = '=NOT(OR(G%i="NOT PASSED",H%i="NOT PASSED",I%i="NOT PASSED"))' % (rownumber + 2, rownumber + 2, rownumber + 2)

    # write database to the excel document
    writer = pandas.ExcelWriter((filenamera.get()), engine='xlsxwriter')
    databasera.to_excel(writer, sheet_name='Sheet 1')
    writer.save()

    # move to the main text body before moving on
    #driver.find_element_by_css_selector(".x-form-trigger.x-form-trigger-arrow").click()
    #driver.find_element_by_xpath("//*[contains(text(), 'All Fields View')]").click()
    #driver.find_element_by_xpath("//*[contains(text(), 'Text Accounts')]").click()

# this function saves the current tax state of the species
def taxsave():
    global databaseta

    # write database to the excel document
    writer = pandas.ExcelWriter((filenameta.get()), engine='xlsxwriter')
    databaseta.to_excel(writer, sheet_name='Sheet 1')
    writer.save()

# this function loads the current status of the species
def reviewload():
    global databasera
    rownumber = (tablerownumber.get())
    # get the current values from the database (for the buttons)
    criteria.set(databasera.iat[rownumber, 5])
    verified.set(databasera.iat[rownumber, 6])
    maps.set(databasera.iat[rownumber, 7])

    # get the correct notes from the database
    notesoutput = databasera.iat[rownumber, 8]

    # clear the notes box and then insert the next text
    notesbox.delete('1.0', END)
    notesbox.insert(INSERT, "%s" % notesoutput)

    # open the assessment chooser window
    assessmentlistchooser()

# advance/go back a row on the table
def update(advorgoback):
    global databasera
    global filedir

    # ensure that the driver is on the correct page
    driver.switch_to.window(driver.window_handles[0])
    # save the current data
    reviewsave()
    # refresh the page by clicking the SIS logo
    driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel").click()
    # get current value of the rowtracker
    rownumber = (tablerownumber.get())
    # check to make sure that you don't go out of bounds (i.e. can't go below 1)
    if advorgoback == -1 and (rownumber < 0):
        return 0
    # if valid then change the tracker for use in the function
    rownumber = ((tablerownumber.get()) + advorgoback)
    tablerownumber.set(rownumber)

    # Get the current species genus and name from the table and ID
    output = databasera.iat[rownumber, 1]
    output2 = databasera.iat[rownumber, 2]
    SpeciesID = databasera.iat[rownumber, 0]

    # Get the correct Category and criteria from the table
    candcouput1 = databasera.iat[rownumber, 3]
    candcoutput2 = databasera.iat[rownumber, 4]

    # check to ensure that the database is still in the scope of the underlying database
    if rownumber - 1 < 0:
        previousspeciesoutput = ""
        previousspeciesoutput2 = ""

        nextspeciesoutput = databasera.iat[rownumber + 1, 1]
        nextspeciesoutput2 = databasera.iat[rownumber + 1, 2]

        goback.config(state='disabled')

    elif rownumber + 1 >= len(databasera):
        previousspeciesoutput = databasera.iat[rownumber - 1, 1]
        previousspeciesoutput2 = databasera.iat[rownumber - 1, 2]

        nextspeciesoutput = ""
        nextspeciesoutput2 = ""

        goforward.config(state='disabled')

    else:
        previousspeciesoutput = databasera.iat[rownumber - 1, 1]
        previousspeciesoutput2 = databasera.iat[rownumber - 1, 2]

        nextspeciesoutput = databasera.iat[rownumber + 1, 1]
        nextspeciesoutput2 = databasera.iat[rownumber + 1, 2]

        goback.config(state='normal')
        goforward.config(state='normal')

    # then set the value of the external rowtracker to the new value
    currentspeciesname.set("%s %s" % (output, output2))
    previousspecies.set("%s %s" % (previousspeciesoutput, previousspeciesoutput2))
    nextspecies.set("%s %s" % (nextspeciesoutput, nextspeciesoutput2))
    candc.set("%s %s" % (candcouput1, candcoutput2))

    # call the search function to look for that species ID
    species_ID.set(SpeciesID)
    tablesearch()

    # if the map viewer has been activated then create map else skip
    # Get the current species genus and name from the table
    if mapengineactive.get() == 1:
        # first destroy the current windows else they stack up
        maptestslevel.destroy()
        # check to see if current species map has been created, if it has then open it and display
        if os.path.isfile("%s\\SpatialDataStore\\%s_%s.html" % (filedir, output, output2)):
            webbrowser.open("%s\\SpatialDataStore\\%s_%s.html" % (filedir, output, output2))
            maptests("%s_%s" % (output, output2), "NoValue")
        # if not then create the map and then open it
        else:
            if (createmap("%s_%s" % (output, output2))) == 0:
                messagebox.showerror(title="Mysterious Rubber Duck", message="No map for this species could be found")
            else:
                # create the map driver itself
                webbrowser.open("%s\\SpatialDataStore\\%s_%s.html" % (filedir, output, output2))
                maptests("%s_%s" % (output, output2), "NoValue")

    # load the species data if it has any else set to defaults
    reviewload()

    # update the progress number
    databaselength.set(str(tablerownumber.get() + 1) + ' of ' + str(len(databasera)))

    # set the menu tracker to 0
    reviewmenuplacetracker.set(0)

# skip to a specific row of the tax table
def taxskipto():
    global databaseta

    # save the current data
    taxsave()

    # refresh the page by clicking the SIS logo
    driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel").click()
    # get current value of the rowtracker
    rownumber = skiptoentrySV.get() - 1
    # check to make sure that you don't go out of bounds (i.e. can't go below 1)
    if rownumber <= 0:
        return 0
    # if valid then change the tracker for use in the function
    taxonomyrowtrackerIntVar.set(rownumber)

    # check to ensure that the database is still in the scope of the underlying database and change buttons accordingly
    previousspeciestax.config(state=NORMAL)
    nextspeciestax.config(state=NORMAL)

    if rownumber - 1 < 0:
        previousspeciestax.config(state=DISABLED)
    if rownumber + 1 >= len(databaseta):
        nextspeciestax.config(state=DISABLED)

    # then set the value of the progress tracker to the new value
    taxonomicprogresstracker.set("%s of %s" % (taxonomyrowtrackerIntVar.get() + 1, len(databaseta)))

    # reset the screen
    taxonomiccheckerrest()
    copiedtexVar.set("Copy")

    # load the user data for the first species
    userKingdomSV.set("%s" % databaseta.iat[rownumber, 0])
    userPhylumSV.set("%s" % databaseta.iat[rownumber, 2])
    userClassSV.set("%s" % databaseta.iat[rownumber, 4])
    userOrderSV.set("%s" % databaseta.iat[rownumber, 6])
    userFamilySV.set("%s" % databaseta.iat[rownumber, 8])
    userGenusSV.set("%s" % databaseta.iat[rownumber, 10])
    userSpeciesSV.set("%s" % databaseta.iat[rownumber, 12])
    # userInfrarankSV.set("%s" % databaseta.iat[0, 14])


    # if check value is 1, then put in the same value as database (as this indicates match), else put what SIS has
    if databaseta.iat[rownumber, 1] == "M":
        SISKingdomSV.set("%s" % databaseta.iat[rownumber, 0])
    else:
        SISKingdomSV.set("%s" % databaseta.iat[rownumber, 1])
    if databaseta.iat[rownumber, 3] == "M":
        SISPhylumSV.set("%s" % databaseta.iat[rownumber, 2])
    else:
        SISPhylumSV.set("%s" % databaseta.iat[rownumber, 3])
    if databaseta.iat[rownumber, 5] == "M":
        SISClassSV.set("%s" % databaseta.iat[rownumber, 4])
    else:
        SISClassSV.set("%s" % databaseta.iat[rownumber, 5])
    if databaseta.iat[rownumber, 7] == "M":
        SISOrderSV.set("%s" % databaseta.iat[rownumber, 6])
    else:
        SISOrderSV.set("%s" % databaseta.iat[rownumber, 7])
    if databaseta.iat[rownumber, 9] == "M":
        SISFamilySV.set("%s" % databaseta.iat[rownumber, 8])
    else:
        SISFamilySV.set("%s" % databaseta.iat[rownumber, 9])
    if databaseta.iat[rownumber, 11] == "M":
        SISGenusSV.set("%s" % databaseta.iat[rownumber, 10])
    else:
        SISGenusSV.set("%s" % databaseta.iat[rownumber, 11])
    if databaseta.iat[rownumber, 13] == "M":
        SISSpeciesSV.set("%s" % databaseta.iat[rownumber, 12])
    else:
        SISSpeciesSV.set("%s" % databaseta.iat[rownumber, 13])
    #if databaseta.iat[rownumber, 15] == 0:
    #    SISInfrarankSV.set("%s" % databaseta.iat[rownumber, 14])

    CombinationStringVar.set("%s %s %s" % (databaseta.iat[rownumber, 10], databaseta.iat[rownumber, 12], databaseta.iat[rownumber, 14]))

    copyname()
    duplicateremover()
    arrowsorter()

    # clear the skip to box
    skiptoentrySV.set(1)

# quit preprocess and return to tax menu
def preprocessreturn():
    global preprocesswindow
    preprocesswindow.destroy()
    taxadderassistantframe.tkraise()

# opens a toplevel asking the user to preprocess a number of species for addition
def preprocess():
    global databaseta
    global preprocesswindow

    preprocesswindow = Toplevel()
    preprocesswindow.config(background="#DFE8F6")
    # position of parent window
    x = root.winfo_x()
    y = root.winfo_y()

    w = simplesearchframe.winfo_width()
    h = simplesearchframe.winfo_height()

    # place the top window
    preprocesswindow.geometry('%dx%d+%d+%d' % (w, h / 2, x, y + h/2))
    preprocesswindow.resizable(0, 0)

    # create the various labels required
    # sum the preprocessed column to get number checked
    databaseta['Preprocessed?'].astype(int)
    total = databaseta['Preprocessed?'].sum()
    # check if "" in which case set to 0
    if total == "":
        total = 0
    # labels
    ttk.Label(preprocesswindow, text="Preprocessing Required to Continue", background="#DFE8F6", font=(None, 15)).grid(column=0, row=0, sticky=EW, columnspan=7)
    ttk.Label(preprocesswindow, text="%s of %s have already been processed" % (total, len(databaseta)), background="#DFE8F6").grid(column=0, row=1, sticky=EW, columnspan=7)
    ttk.Label(preprocesswindow, text="You are at number %s" % (taxonomyrowtrackerIntVar.get()), background="#DFE8F6").grid(column=0, row=2, sticky=EW, columnspan=7)

    # buttons
    # number left in dataset
    numberleft = len(databaseta) - total

    pre10 = ttk.Button(preprocesswindow, text="Preprocess 10", command=lambda: taxonomychecker(10))
    pre20 = ttk.Button(preprocesswindow, text="Preprocess 20", command=lambda: taxonomychecker(20))
    pre50 = ttk.Button(preprocesswindow, text="Preprocess 50", command=lambda: taxonomychecker(50))
    pre100 = ttk.Button(preprocesswindow, text="Preprocess 100", command=lambda: taxonomychecker(100))
    ttk.Button(preprocesswindow, text="Preprocess remaining (%i)" % numberleft, command=lambda: taxonomychecker(numberleft)).grid(column=0, row=7, sticky=EW)
    ttk.Button(preprocesswindow, text="Quit", command=lambda: preprocessreturn()).grid(column=1, row=8, sticky=EW)

    pre10.grid(column=0, row=3, sticky=EW)
    pre20.grid(column=0, row=4, sticky=EW)
    pre50.grid(column=0, row=5, sticky=EW)
    pre100.grid(column=0, row=6, sticky=EW)

    # block buttons that are larger than the number left
    if 10 > numberleft:
        pre10.config(state=DISABLED)
        pre20.config(state=DISABLED)
        pre50.config(state=DISABLED)
        pre100.config(state=DISABLED)
    elif 20 > numberleft:
        pre20.config(state=DISABLED)
        pre50.config(state=DISABLED)
        pre100.config(state=DISABLED)
    elif 50 > numberleft:
        pre50.config(state=DISABLED)
        pre100.config(state=DISABLED)
    elif 100 > numberleft:
        pre100.config(state=DISABLED)

    preprocesswindow.columnconfigure((0, 1), weight=1)
    preprocesswindow.rowconfigure((0, 1, 2), weight=1)

# advance/go back a row of the tax table
def taxupdate(advorgoback):
    global databaseta

    # reset the screen and display the results
    taxonomiccheckerrest()
    copiedtexVar.set("Copy")

    # get current value of the rowtracker
    rownumber = taxonomyrowtrackerIntVar.get()

    # save the current data
    taxsave()

    # refresh the page by clicking the SIS logo
    driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel").click()

    # check to make sure that you don't go out of bounds (i.e. can't go below 1)
    if advorgoback == -1 and (rownumber < 0):
        return 0
    # if valid then change the tracker for use in the function
    rownumber = (taxonomyrowtrackerIntVar.get() + advorgoback)
    taxonomyrowtrackerIntVar.set(rownumber)

    # check to ensure that the database is still in the scope of the underlying database and change buttons accordingly
    previousspeciestax.config(state=NORMAL)
    nextspeciestax.config(state=NORMAL)

    if rownumber - 1 < 0:
        previousspeciestax.config(state=DISABLED)
    if rownumber + 1 >= len(databaseta):
        nextspeciestax.config(state=DISABLED)

    # then set the value of the progress tracker to the new value
    taxonomicprogresstracker.set("%s of %s" % (taxonomyrowtrackerIntVar.get() + 1, len(databaseta)))

    if databaseta.iat[taxonomyrowtrackerIntVar.get(), 22] == 0:
        preprocess()
        taxsave()

    # if Already in SIS in notes column then show add to working set button and text
    if databaseta.iat[rownumber, 20] == "Already in SIS":
        # load the user data for the first species
        userKingdomSV.set("%s" % databaseta.iat[rownumber, 0])
        userPhylumSV.set("%s" % databaseta.iat[rownumber, 2])
        userClassSV.set("%s" % databaseta.iat[rownumber, 20])
        taxlabel12.grid(columnspan=3)
        taxlabel12.config(wraplength=250)
        addtoworkingsetbutton.grid(column=2, row=12, columnspan=3)
        userOrderSV.set("%s" % databaseta.iat[rownumber, 6])
        userFamilySV.set("%s" % databaseta.iat[rownumber, 8])
        userGenusSV.set("%s" % databaseta.iat[rownumber, 10])
        userSpeciesSV.set("%s" % databaseta.iat[rownumber, 12])
        # userInfrarankSV.set("%s" % databaseta.iat[0, 14])

        # if check value is 1, then put in the same value as database (as this indicates match), else put what SIS has
        if databaseta.iat[rownumber, 1] == "M":
            SISKingdomSV.set("%s" % databaseta.iat[rownumber, 0])
        else:
            SISKingdomSV.set("%s" % databaseta.iat[rownumber, 1])
        if databaseta.iat[rownumber, 3] == "M":
            SISPhylumSV.set("%s" % databaseta.iat[rownumber, 2])
        else:
            SISPhylumSV.set("%s" % databaseta.iat[rownumber, 3])
        if databaseta.iat[rownumber, 5] == "M":
            SISClassSV.set("%s" % databaseta.iat[rownumber, 4])
        else:
            SISClassSV.set("%s" % databaseta.iat[rownumber, 5])
        if databaseta.iat[rownumber, 7] == "M":
            SISOrderSV.set("%s" % databaseta.iat[rownumber, 6])
        else:
            SISOrderSV.set("%s" % databaseta.iat[rownumber, 7])
        if databaseta.iat[rownumber, 9] == "M":
            SISFamilySV.set("%s" % databaseta.iat[rownumber, 8])
        else:
            SISFamilySV.set("%s" % databaseta.iat[rownumber, 9])
        if databaseta.iat[rownumber, 11] == "M":
            SISGenusSV.set("%s" % databaseta.iat[rownumber, 10])
        else:
            SISGenusSV.set("%s" % databaseta.iat[rownumber, 11])
        if databaseta.iat[rownumber, 13] == "M":
            SISSpeciesSV.set("%s" % databaseta.iat[rownumber, 12])
        else:
            SISSpeciesSV.set("%s" % databaseta.iat[rownumber, 13])
        #if databaseta.iat[rownumber, 15] == 0:
        #    SISInfrarankSV.set("%s" % databaseta.iat[rownumber, 14])

        CombinationStringVar.set("%s %s %s" % (databaseta.iat[rownumber, 10], databaseta.iat[rownumber, 12], databaseta.iat[rownumber, 14]))
        copyname()
        duplicateremover()
        arrowsorter()
    # if not NO then check to see if notes column is blank, if not then show that
    elif databaseta.iat[rownumber, 20] != "":
        # load the user data for the first species
        userKingdomSV.set("%s" % databaseta.iat[rownumber, 0])
        userPhylumSV.set("%s" % databaseta.iat[rownumber, 2])
        userClassSV.set("%s" % databaseta.iat[rownumber, 20])
        taxlabel12.grid(columnspan=3)
        taxlabel12.config(wraplength=250)
        userOrderSV.set("%s" % databaseta.iat[rownumber, 6])
        userFamilySV.set("%s" % databaseta.iat[rownumber, 8])
        userGenusSV.set("%s" % databaseta.iat[rownumber, 10])
        userSpeciesSV.set("%s" % databaseta.iat[rownumber, 12])
        # userInfrarankSV.set("%s" % databaseta.iat[0, 14])

        # if check value is 1, then put in the same value as database (as this indicates match), else put what SIS has
        if databaseta.iat[rownumber, 1] == "M":
            SISKingdomSV.set("%s" % databaseta.iat[rownumber, 0])
        else:
            SISKingdomSV.set("%s" % databaseta.iat[rownumber, 1])
        if databaseta.iat[rownumber, 3] == "M":
            SISPhylumSV.set("%s" % databaseta.iat[rownumber, 2])
        else:
            SISPhylumSV.set("%s" % databaseta.iat[rownumber, 3])
        if databaseta.iat[rownumber, 5] == "M":
            SISClassSV.set("%s" % databaseta.iat[rownumber, 4])
        else:
            SISClassSV.set("%s" % databaseta.iat[rownumber, 5])
        if databaseta.iat[rownumber, 7] == "M":
            SISOrderSV.set("%s" % databaseta.iat[rownumber, 6])
        else:
            SISOrderSV.set("%s" % databaseta.iat[rownumber, 7])
        if databaseta.iat[rownumber, 9] == "M":
            SISFamilySV.set("%s" % databaseta.iat[rownumber, 8])
        else:
            SISFamilySV.set("%s" % databaseta.iat[rownumber, 9])
        if databaseta.iat[rownumber, 11] == "M":
            SISGenusSV.set("%s" % databaseta.iat[rownumber, 10])
        else:
            SISGenusSV.set("%s" % databaseta.iat[rownumber, 11])
        if databaseta.iat[rownumber, 13] == "M":
            SISSpeciesSV.set("%s" % databaseta.iat[rownumber, 12])
        else:
            SISSpeciesSV.set("%s" % databaseta.iat[rownumber, 13])
        #if databaseta.iat[rownumber, 15] == 0:
        #    SISInfrarankSV.set("%s" % databaseta.iat[rownumber, 14])

        CombinationStringVar.set("%s %s %s" % (databaseta.iat[rownumber, 10], databaseta.iat[rownumber, 12], databaseta.iat[rownumber, 14]))
        copyname()
        duplicateremover()
        arrowsorter()

    # else set up as normal
    else:
        # load the user data for the first species
        userKingdomSV.set("%s" % databaseta.iat[rownumber, 0])
        userPhylumSV.set("%s" % databaseta.iat[rownumber, 2])
        userClassSV.set("%s" % databaseta.iat[rownumber, 4])
        userOrderSV.set("%s" % databaseta.iat[rownumber, 6])
        userFamilySV.set("%s" % databaseta.iat[rownumber, 8])
        userGenusSV.set("%s" % databaseta.iat[rownumber, 10])
        userSpeciesSV.set("%s" % databaseta.iat[rownumber, 12])
        # userInfrarankSV.set("%s" % databaseta.iat[0, 14])

        # if check value is 1, then put in the same value as database (as this indicates match), else put what SIS has
        if databaseta.iat[rownumber, 1] == "M":
            SISKingdomSV.set("%s" % databaseta.iat[rownumber, 0])
        else:
            SISKingdomSV.set("%s" % databaseta.iat[rownumber, 1])
        if databaseta.iat[rownumber, 3] == "M":
            SISPhylumSV.set("%s" % databaseta.iat[rownumber, 2])
        else:
            SISPhylumSV.set("%s" % databaseta.iat[rownumber, 3])
        if databaseta.iat[rownumber, 5] == "M":
            SISClassSV.set("%s" % databaseta.iat[rownumber, 4])
        else:
            SISClassSV.set("%s" % databaseta.iat[rownumber, 5])
        if databaseta.iat[rownumber, 7] == "M":
            SISOrderSV.set("%s" % databaseta.iat[rownumber, 6])
        else:
            SISOrderSV.set("%s" % databaseta.iat[rownumber, 7])
        if databaseta.iat[rownumber, 9] == "M":
            SISFamilySV.set("%s" % databaseta.iat[rownumber, 8])
        else:
            SISFamilySV.set("%s" % databaseta.iat[rownumber, 9])
        if databaseta.iat[rownumber, 11] == "M":
            SISGenusSV.set("%s" % databaseta.iat[rownumber, 10])
        else:
            SISGenusSV.set("%s" % databaseta.iat[rownumber, 11])
        if databaseta.iat[rownumber, 13] == "M":
            SISSpeciesSV.set("%s" % databaseta.iat[rownumber, 12])
        else:
            SISSpeciesSV.set("%s" % databaseta.iat[rownumber, 13])
        #if databaseta.iat[rownumber, 15] == 0:
        #    SISInfrarankSV.set("%s" % databaseta.iat[rownumber, 14])

        CombinationStringVar.set("%s %s %s" % (databaseta.iat[rownumber, 10], databaseta.iat[rownumber, 12], databaseta.iat[rownumber, 14]))
        copyname()
        duplicateremover()
        arrowsorter()

# skip to the required assessment
def skiptofunction():
    global databasera
    goback.config(state='normal')
    goforward.config(state='normal')

    # get the number to skip to
    numbertoskipto = (skipto.get() - 1)
    skipto.set("")
    # save the current data
    reviewsave()
    # refresh the page by clicking the SIS logo
    driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel").click()
    # check to make sure that you don't go out of bounds (i.e. can't go below 2 or above max length of list)
    if numbertoskipto < 0 or numbertoskipto > len(databasera):
        return 0
    # if valid then change the tracker for use in the function
    rownumber = numbertoskipto
    tablerownumber.set(numbertoskipto)

    # Get the current species genus and name from the table and species ID
    output = databasera.iat[rownumber, 1]
    output2 = databasera.iat[rownumber, 2]
    SpeciesID = databasera.iat[rownumber, 0]

    # Get the correct Category and criteria from the table
    candcouput1 = databasera.iat[rownumber, 3]
    candcoutput2 = databasera.iat[rownumber, 4]

    # check to ensure that the database is still in the scope of the underlying database
    if rownumber - 1 < 0:
        previousspeciesoutput = ""
        previousspeciesoutput2 = ""

        nextspeciesoutput = databasera.iat[rownumber + 1, 1]
        nextspeciesoutput2 = databasera.iat[rownumber + 1, 2]

        goback.config(state='disabled')

    elif rownumber + 1 >= len(databasera):
        previousspeciesoutput = databasera.iat[rownumber - 1, 1]
        previousspeciesoutput2 = databasera.iat[rownumber - 1, 2]

        nextspeciesoutput = ""
        nextspeciesoutput2 = ""

        goforward.config(state='disabled')

    else:
        previousspeciesoutput = databasera.iat[rownumber - 1, 1]
        previousspeciesoutput2 = databasera.iat[rownumber - 1, 2]

        nextspeciesoutput = databasera.iat[rownumber + 1, 1]
        nextspeciesoutput2 = databasera.iat[rownumber + 1, 2]

        goback.config(state='normal')
        goforward.config(state='normal')

    # then set the value of the external rowtracker to the new value
    currentspeciesname.set("%s %s" % (output, output2))
    previousspecies.set("%s %s" % (previousspeciesoutput, previousspeciesoutput2))
    nextspecies.set("%s %s" % (nextspeciesoutput, nextspeciesoutput2))
    candc.set("%s %s" % (candcouput1, candcoutput2))

    # call the search function to look for that species ID
    species_ID.set(SpeciesID)
    tablesearch()

    # update the tracker number
    databaselength.set(str(tablerownumber.get() + 1) + ' of ' + str(len(databasera)))

    # load the species data if it has any else set to defaults
    reviewload()

# shut down the assistant
def quit():
    global root
    root.quit()
    driver.quit()

# swap the status of the review assisant buttons from/to passed/not passed
def swapstate(buttontext, actualbutton):
    tempvariable = buttontext.get()
    if tempvariable == "Not Passed":
        buttontext.set("Passed")
    else:
        buttontext.set("Not Passed")

# create a top level with all the review tools in it
def createtoolwindow():
    #create window and update frame to ensure correct size
    global top
    top.deiconify()

    #hide the open button, show the get rid of button
    hidetoolsbutton.grid(column=2, row=12)
    reviewtoolsbutton.grid_forget()

    # position of parent window
    x = root.winfo_x()
    y = root.winfo_y()

    # size of parent window
    w = simplesearchframe.winfo_width()
    h = simplesearchframe.winfo_height()

    # place the top window
    top.geometry('%dx%d+%d+%d' % (w, h/5, x, y+h+42))
    top.resizable(0, 0)

    # tool window buttons declaration
    gotoadmin = ttk.Button(top, text="Admin Panel", command=lambda: gotoadminfunc())
    returntomain = ttk.Button(top, text="Main Text", command=lambda: returntofulltext())
    checkanddownloadbutton = ttk.Button(top, text="Attachments?", command=lambda: checkanddownloadassessments())
    loadreferencetab = ttk.Button(top, text="References?", command=lambda: gotoreferences())
    validateassessmentbutton = ttk.Button(top, textvariable=validatebuttontext, command=lambda: validateassessment(validatebuttontext.get()))
    nextitem = ttk.Button(top, text=">", command=lambda: gotonextmenuitem(), state=NORMAL)
    previousitem = ttk.Button(top, text="<", command=lambda: gotopreviousmenutiem(), state=NORMAL)
    activatemapengine = ttk.Button(top, textvariable=mapenginetext, command=lambda: mapengineswitch())

    # tool window buttons placement
    checkanddownloadbutton.grid(column=0, row=0, sticky=EW)
    loadreferencetab.grid(column=1, row=0, sticky=EW)
    validateassessmentbutton.grid(column=2, row=0, sticky=EW)

    previousitem.grid(column=0, row=1, sticky=EW)
    returntomain.grid(column=1, row=1, sticky=EW)
    nextitem.grid(column=2, row=1, sticky=EW)

    gotoadmin.grid(column=0, row=2, sticky=EW)
    activatemapengine.grid(column=2, row=2, sticky=EW)

    top.columnconfigure((0, 1, 2), weight=1)
    top.rowconfigure((0, 1, 2), weight=1)

# hide the review tools popup window
def hidetoolwindow():
    hidetoolsbutton.grid_forget()
    reviewtoolsbutton.grid(column=2, row=12)
    top.withdraw()

# Checks shapefile against the required and standard attributes, returns a list of fields that are not in either first list = missing required, second = fields to remove
def checkpolygonfields(shapefiletotest, freshwater):
    global mapchecks

    # create container for the list of lists.
    returnlist = [[] for _ in range(2)]

    if freshwater:
        requiredpolygonfields = ['ID_NO', 'BASIN_ID', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION', 'geometry']
    else:
        requiredpolygonfields = ['ID_NO', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION', 'geometry']
    # create a list that contains all the required polygon attributes
    # create a list that contains all the optional polygon attributes
    optionalpolygonfields = ['FID', 'OBJECTID', 'SOURCE', 'DIS_COMM', 'ISLAND', 'SUBSPECIES', 'SUBPOP', 'TAX_COMM', 'DATA_SENS', 'SENS_COMM']

    # create an empty list to contain the attribute names from the test data
    datapolygonfields = []

    # first screen for essential fields
    # create list of attributes in the layer
    for x in shapefiletotest:
        datapolygonfields.append(x)

    # find the missing required fields and append to the first position in the list
    missingrequired = list(set(requiredpolygonfields)-set(datapolygonfields))
    for x in missingrequired:
        returnlist[0].append(x)

    # find what additional fields have been provided
    extrafields = list(set(datapolygonfields)-set(requiredpolygonfields))
    if len(extrafields) == 0:
        for y in extrafields:
            returnlist[1].append(y)
    # if additional fields, then test to see if they are in the optional list
    else:
        fieldstoberemoved = list(set(extrafields)-set(optionalpolygonfields))
        for z in fieldstoberemoved:
            returnlist[1].append(z)

    # return values
    return returnlist

# check a field against its inbuilt criteria
def checkfield(shapefiletotest, attributetoinspect):
    if attributetoinspect == 'PRESENCE':
        presenceerrors = []
        try:
            for prow, pvalue in enumerate(shapefiletotest['PRESENCE']):
                if pvalue == 0 or pvalue > 6:
                    presenceerrors.append(['PRESENCE', prow])
                if pvalue == 2:
                    presenceerrors.append(['PRESENCE', prow])
            return presenceerrors
        except:
            presenceerrors.append(['Presence Error'])
            return presenceerrors

    elif attributetoinspect == 'ORIGIN':
        originerrors = []
        try:
            for orow, ovalue in enumerate(shapefiletotest['ORIGIN']):
                if ovalue == 0 or ovalue > 6:
                    originerrors.append(['ORIGIN', orow])
            return originerrors
        except:
            originerrors.append(['Origin Error'])
            return originerrors

    elif attributetoinspect == 'SEASONAL':
        seasonalerrors = []
        try:
            for srow, svalue in enumerate(shapefiletotest['SEASONAL']):
                if svalue == 0 or svalue > 5:
                    seasonalerrors.append(['SEASONAL', srow])
            return seasonalerrors
        except:
            seasonalerrors.append(['Seasonal Error'])
            return seasonalerrors

    elif attributetoinspect == 'COMPILER':
        comperrors = []
        try:
            for comrow, comvalue in enumerate(shapefiletotest['COMPILER']):
                if comvalue == "" or comvalue == None:
                    comperrors.append(['COMPILER', comrow])
                try:
                    if any(char.isdigit() for char in comvalue):
                        comperrors.append(['COMPILER', comrow])
                except:
                    pass
            return comperrors
        except:
            comperrors.append(['Compiler Error'])
            return comperrors

    elif attributetoinspect == 'YEAR':
        yearerrors = []
        try:
            for yrow, yvalue in enumerate(shapefiletotest['YEAR']):
                if len(str(yvalue)) != 4 or isinstance(yvalue, str) or yvalue > int(time.strftime("%Y")):
                    yearerrors.append(['YEAR', yrow])
            return yearerrors
        except:
            yearerrors.append(['Year Error'])
            return yearerrors

    elif attributetoinspect == 'CITATION':
        citationerrors = []
        try:
            firstvalue = (shapefiletotest['CITATION'][0])
            for crow, cvalue in enumerate(shapefiletotest['CITATION']):
                if cvalue == "" or cvalue != firstvalue:
                    citationerrors.append(['CITATION', crow])
            return citationerrors
        except:
            citationerrors.append(['Citation Error'])
            return citationerrors

    elif attributetoinspect == 'BINOMIAL':
        binomialerrors = []
        # get the name of the species from the database
        rownumber = tablerownumber.get()
        output = databasera.iat[rownumber, 1]
        output2 = databasera.iat[rownumber, 2]
        try:
            for brow, bvalue in enumerate(shapefiletotest['BINOMIAL']):
                if bvalue != ("%s %s" % (output, output2)):
                    binomialerrors.append(['BINOMIAL', brow])
            return binomialerrors
        except:
            binomialerrors.append(['Binomial Error'])
            return binomialerrors

    else:
        print("Invalid attribute provided")

# check the order of the attributes returns 1 if correct, 0 if not
def checkattributeorder(shapefiletotest):
    correctorder = ['ID_NO', 'BASIN_ID', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION', 'SOURCE', 'DIS_COMM', 'ISLAND', 'SUBSPECIES', 'SUBPOP', 'TAX_COMM', 'DATA_SENS', 'SENS_COMM', 'Shape_Leng', 'Shape_Area', 'geometry']

    finalorder=[]
    #first create the local correct order
    for x in correctorder:
        if x in shapefiletotest:
            finalorder.append(x)

    for x, y in enumerate(shapefiletotest):
        if finalorder[x] != y:
            return False
    return True

# collates and writes to file the changes for the required attribute changes
def commitchanges(correctorder, shapefiletofix, speciesname, freshwater):
    global fixattributesTL

    # create a list to store the changes that need to be made
    listofchanges = []
    internalcounter = 3
    # collate the changes to be made list original to what it should be
    for counter, combobox in enumerate(fixattributesTL.children.values()):
        if 'combobox' in str(combobox):
            if combobox.get() != "PRESENT":
                listofchanges.append([correctorder[counter - internalcounter], combobox.get()])
            internalcounter = internalcounter + 1

    # loop through the list of changes and add columns as necessary
    for x in listofchanges:
        # if add as a new variable then add a new variable in with the correct type
        if x[1] == "Add as a new variable":
            # if number then 0 column, else put filler text
            if x[0] in ('BINOMIAL', 'COMPILER', 'CITATION'):
                shapefiletofix["%s" % x[0]] = "text"
            else:
                shapefiletofix["%s" % x[0]] = 0
        # if not then copy the old column over to a new column with a new name, then drop old column
        else:
            shapefiletofix["%s" % x[0]] = shapefiletofix["%s" % x[1]]
            shapefiletofix.drop("%s" % x[1], axis=1, inplace=True)

    # get the data from the designated location
    fp = locationofmaps.get()

    # after all changes have occurred then save the file
    shapefiletofix.to_file(fp, driver='ESRI Shapefile', layer=speciesname)

    # destroy the toplevel
    fixattributesTL.destroy()

    # create the new map
    rownumber = (tablerownumber.get())
    createmap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    fixattributesTL.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname, freshwater)

# Fix the required attributes field
def fixrequiredattributes(shapefiletofix, freshwater, missingrequired, speciesname):
    global fixattributesTL

    if freshwater == True:
        correctorder = ['ID_NO', 'BASIN_ID', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION']
    else:
        correctorder = ['ID_NO', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION']

    # create a top level in the middle of the screen
    # create the toplevel to house everything
    # dimensions of parent window
    x = root.winfo_screenwidth()
    y = root.winfo_screenheight()

    # set the width to the width of the
    fixattributesTL = Toplevel()
    fixattributesTL.config(background="#DFE8F6")
    fixattributesTL.geometry('%dx%d+%d+%d' % (500, 500, x/2 - 250, y/2 - 250))

    listofattributes = []
    listofattributes.append("Add as a new variable")
    # create the list of attributes in the list
    for x in shapefiletofix:
        listofattributes.append(x)

    # Create the table headers
    ttk.Label(fixattributesTL, text="Required Attribute", font=(None, 15, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=0, sticky=NSEW)
    ttk.Label(fixattributesTL, text="Status", font=(None, 15, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=1, row=0, sticky=NSEW)
    # run through the required attributes, if the attribute exists in the list of missing then flag the options up
    for x, y in enumerate(correctorder):
        # if in the list of missing then create the label with the options
        if y in missingrequired:
            ttk.Label(fixattributesTL, text="%s" % y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x+1, sticky=NSEW)
            ttk.Combobox(fixattributesTL, values=listofattributes, state="readonly").grid(column=1, row=x+1, sticky=NSEW)
        else:
            ttk.Label(fixattributesTL, text="%s" % y, borderwidth=3, relief="solid", background="#DFE8F6", foreground="#828282").grid(column=0, row=x+1, sticky=NSEW)
            ttk.Combobox(fixattributesTL, state="disabled").grid(column=1, row=x+1, sticky=NSEW)

    # run through and for all blank ones write as PRESENT
    # collate the changes to be made list original to what it should be
    for counter, combobox in enumerate(fixattributesTL.children.values()):
        if 'combobox' in str(combobox):
            if combobox.instate([DISABLED, ]):
                combobox.set("PRESENT")

    # finally add the commit button to the bottom
    ttk.Button(fixattributesTL, text="Commit Changes", command=lambda: commitchanges(correctorder, shapefiletofix, speciesname, freshwater)).grid(column=1, row=20, sticky=NSEW, columnspan=2)
    # status of each one can either be present, or a drop down menu with the full list of attributes remaining or an add button
    # at the end it deletes the current map and reopens the new one

    # give weight to the rows and column
    fixattributesTL.columnconfigure((0, 1), weight=1)
    fixattributesTL.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,14,15,16,17,18,19,20), weight=1)

    # fill the remaing space
    for child in fixattributesTL.winfo_children():
        child.grid_configure(padx=5, pady=5)

# Reorder the attributes so that they are in the correct order
def reorganiseattributes(shapefiletorearrange, speciesname, freshwater):
    correctorder = ['ID_NO', 'BASIN_ID', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION', 'SOURCE', 'DIS_COMM', 'ISLAND', 'SUBSPECIES', 'SUBPOP', 'TAX_COMM', 'DATA_SENS', 'SENS_COMM', 'Shape_Leng', 'Shape_Area', 'geometry']

    finalorder=[]
    # first run through and remove all attributes not present
    for x in correctorder:
        if x in shapefiletorearrange:
            finalorder.append(x)

    rearranged = geopandas.GeoDataFrame()
    rearranged = shapefiletorearrange[finalorder]

    fp = locationofmaps.get()
    rearranged.to_file(fp, driver='ESRI Shapefile', layer=speciesname)

    # recreate the map
    rownumber = (tablerownumber.get())
    createmap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname, freshwater)

# Remove the extra fields that have been provided
def dropextrafields(shapefiletofix, speciesname ,freshwater):
    # first rerun the extra fields to get the correct data
    fieldstodrop = checkpolygonfields(shapefiletofix, True)[1]

    for x in fieldstodrop:
        shapefiletofix.drop('%s' % x, axis=1, inplace=True)

    fp = locationofmaps.get()
    shapefiletofix.to_file(fp, driver='ESRI Shapefile', layer=speciesname)

    # recreate the map
    rownumber = (tablerownumber.get())
    createmap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname, freshwater)

# commit citation field changes
def commitcitationfieldrepair(shapefiletofix, speciesname, freshwater, value):
    # replace all values in the BINOMIAL field with the correct name
    shapefiletofix["CITATION"] = str(value)

    # save the shapefile
    fp = locationofmaps.get()
    shapefiletofix.to_file(fp, driver='ESRI Shapefile', layer=speciesname)

    # recreate the map
    rownumber = (tablerownumber.get())
    createmap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    citationrepairTL.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname, freshwater)

# function to ask user what the correct citation should be and offer the functionality to repair it
def repaircitationfield(shapefiletofix, speciesname, freshwater):
    global citationrepairTL

    # create the toplevel to house everything
    # dimensions of parent window
    x = root.winfo_screenwidth()
    y = root.winfo_screenheight()

    # set the width to the width of the
    citationrepairTL = Toplevel()
    citationrepairTL.config(background="#DFE8F6")
    citationrepairTL.geometry('%dx%d+%d+%d' % (300, 160, x / 2 - 150, y / 2 - 80))

    # Create the table headers
    ttk.Label(citationrepairTL, text="Citation Error", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=0, sticky=NSEW, columnspan=3)
    ttk.Label(citationrepairTL, text="Enter correct citation below", borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=1, sticky=NSEW, columnspan=3)

    # Create a entry box for the user to enter the correct data
    newcitationSV = StringVar()
    ttk.Entry(citationrepairTL, textvariable=newcitationSV).grid(column=0, row=2, sticky=NSEW, columnspan=3)

    # Create a button to commit the change
    ttk.Button(citationrepairTL, text="Commit", command=lambda: commitcitationfieldrepair(shapefiletofix, speciesname, freshwater, newcitationSV.get())).grid(column=0, row=3, sticky=NSEW, columnspan=3)

    # give weight to the rows and column
    citationrepairTL.columnconfigure((0, 1, 2), weight=1)
    citationrepairTL.rowconfigure((0, 1, 2), weight=1)

    # fill the remaing space
    for child in citationrepairTL.winfo_children():
        child.grid_configure(padx=2, pady=5)

# Repair binomial field by copying the SIS name into all the rows of the binomial column
def repairbinomialfield(shapefiletofix, speciesname ,freshwater):
    rownumber = (tablerownumber.get())

    # get the correct name from the database
    correctname = "%s %s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2])

    # replace all values in the BINOMIAL field with the correct name
    shapefiletofix["BINOMIAL"] = correctname

    # save the shapefile
    fp = locationofmaps.get()
    shapefiletofix.to_file(fp, driver='ESRI Shapefile', layer=speciesname)

    # recreate the map
    createmap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname, freshwater)

# Gets edits made by the user for the POS repairs and commits them to the shapefile
def commitPOSchanges(errortable, shapefiletofix, freshwater, speciesname):
    global repairPOSfieldsTL
    # first take the error table, add a new column which is the corrected data
    counter = 0
    for combobox in repairPOSfieldsTL.children.values():
        if 'combobox' in str(combobox):
            # test to see if any invalid codes provided, cancel if so
            if combobox.get() == "Invalid Code":
                messagebox.showerror(title="Error Duck", message="Invalid Presence code provided please fix before committing")
                return 0
            else:
                errortable[counter].append(combobox.get())
                counter = counter + 1

    # loop through the corrections and fix the shapefile
    for x in errortable:
        shapefiletofix.at[x[1], x[0]] = x[2]

    # get the data from the designated location
    fp = locationofmaps.get()

    # after all changes have occurred then save the file
    shapefiletofix.to_file(fp, driver='ESRI Shapefile', layer=speciesname)

    # destroy the toplevel
    repairPOSfieldsTL.destroy()

    # create the new map
    rownumber = (tablerownumber.get())
    createmap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    repairPOSfieldsTL.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname, freshwater)

# For the POS repair window, fills all rows with a number provided by the user
def fillallPOS(value, attribute):
    testvalue = value.get()

    if attribute == "presence":
        if testvalue in ["1", "3", "4", "5", "6"]:
            for combobox in repairPOSfieldsTL.children.values():
                if 'combobox' in str(combobox):
                    combobox.set(testvalue)
                    value.delete(0, len(testvalue))
        else:
            messagebox.showerror(title="Error Duck", message="Invalid Presence code")
            value.delete(0, len(testvalue))
    elif attribute == "origin":
        if testvalue in ["1", "2", "3", "4", "5", "6"]:
            for combobox in repairPOSfieldsTL.children.values():
                if 'combobox' in str(combobox):
                    combobox.set(testvalue)
                    value.delete(0, len(testvalue))
        else:
            messagebox.showerror(title="Error Duck", message="Invalid origin code")
            value.delete(0, len(testvalue))
    elif attribute == "seasonal":
        if testvalue in ["1", "2", "3", "4", "5"]:
            for combobox in repairPOSfieldsTL.children.values():
                if 'combobox' in str(combobox):
                    combobox.set(testvalue)
                    value.delete(0, len(testvalue))
        else:
            messagebox.showerror(title="Error Duck", message="Invalid seasonality code")
            value.delete(0, len(testvalue))

    elif attribute == "compiler":
        for combobox in repairPOSfieldsTL.children.values():
            if 'combobox' in str(combobox):
                combobox.set(testvalue)
                value.delete(0, len(testvalue))

    else:
        if len(testvalue) == 4 and int(testvalue) <= int(time.strftime("%Y")):
            for combobox in repairPOSfieldsTL.children.values():
                if 'combobox' in str(combobox):
                    combobox.set(testvalue)
                    value.delete(0, len(testvalue))
        else:
            messagebox.showerror(title="Error Duck", message="Invalid year provided")
            value.delete(0, len(testvalue))

# Repair the presence field, convert all 2's to 1 and flag the rest for review
def repairPOSfields(shapefiletofix, speciesname, freshwater, errortable, field):
    global repairPOSfieldsTL

    # create the toplevel to house everything
    # dimensions of parent window
    x = root.winfo_screenwidth()
    y = root.winfo_screenheight()

    # set the width to the width of the
    repairPOSfieldsTL = Toplevel()
    repairPOSfieldsTL.config(background="#DFE8F6")
    repairPOSfieldsTL.geometry('%dx%d+%d+%d' % (500, 500, x/2 - 250, y/2 - 250))

    # Create the table headers
    ttk.Label(repairPOSfieldsTL, text="%s attribute errors" % field.capitalize(), font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=0, sticky=NSEW, columnspan=3)
    ttk.Label(repairPOSfieldsTL, text="Error on row", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=1, sticky=NSEW)
    ttk.Label(repairPOSfieldsTL, text="Current value", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=1, row=1, sticky=NSEW)
    ttk.Label(repairPOSfieldsTL, text="New Value", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=2, row=1, sticky=NSEW)

    if field == "presence":
        # run through the error table, create a new row for each error
        for x, y in enumerate(errortable):
            # get the current code for this row
            # if in the list of missing then create the label with the options
            ttk.Label(repairPOSfieldsTL, anchor="center", text="%s" % errortable[x][1], borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
            ttk.Label(repairPOSfieldsTL, anchor="center", text=shapefiletofix[errortable[x][0]][errortable[x][1]], borderwidth=3, relief="solid", background="#DFE8F6").grid(column=1, row=x + 2, sticky=NSEW)
            ttk.Combobox(repairPOSfieldsTL, state="readonly", values=[1, 2, 3, 4, 5, 6]).grid(column=2, row=x + 2, sticky=NSEW)
    elif field == "origin":
        # run through the error table, create a new row for each error
        for x, y in enumerate(errortable):
            # get the current code for this row
            # if in the list of missing then create the label with the options
            ttk.Label(repairPOSfieldsTL, anchor="center", text="%s" % errortable[x][1], borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
            ttk.Label(repairPOSfieldsTL, anchor="center", text=shapefiletofix[errortable[x][0]][errortable[x][1]], borderwidth=3, relief="solid", background="#DFE8F6").grid(column=1, row=x + 2, sticky=NSEW)
            ttk.Combobox(repairPOSfieldsTL, state="readonly", values=[1, 3, 4, 5, 6]).grid(column=2, row=x + 2, sticky=NSEW)
    elif field == "seasonal":
        # run through the error table, create a new row for each error
        for x, y in enumerate(errortable):
            # get the current code for this row
            # if in the list of missing then create the label with the options
            ttk.Label(repairPOSfieldsTL, anchor="center", text="%s" % errortable[x][1], borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
            ttk.Label(repairPOSfieldsTL, anchor="center", text=shapefiletofix[errortable[x][0]][errortable[x][1]], borderwidth=3, relief="solid", background="#DFE8F6").grid(column=1, row=x + 2, sticky=NSEW)
            ttk.Combobox(repairPOSfieldsTL, state="readonly", values=[1, 2, 3, 4, 5]).grid(column=2, row=x + 2, sticky=NSEW)
    elif field == "year":
        # run through the error table, create a new row for each error
        for x, y in enumerate(errortable):
            # get the current code for this row
            # if in the list of missing then create the label with the options
            ttk.Label(repairPOSfieldsTL, anchor="center", text="%s" % errortable[x][1], borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
            ttk.Label(repairPOSfieldsTL, anchor="center", text=shapefiletofix[errortable[x][0]][errortable[x][1]], borderwidth=3, relief="solid", background="#DFE8F6").grid(column=1, row=x + 2, sticky=NSEW)
            ttk.Combobox(repairPOSfieldsTL, state="normal", values=["%s" % int(time.strftime("%Y"))]).grid(column=2, row=x + 2, sticky=NSEW)
    else:
        # run through the error table, create a new row for each error
        for x, y in enumerate(errortable):
            # get the current code for this row
            # if in the list of missing then create the label with the options
            ttk.Label(repairPOSfieldsTL, anchor="center", text="%s" % errortable[x][1], borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
            ttk.Label(repairPOSfieldsTL, anchor="center", text=shapefiletofix[errortable[x][0]][errortable[x][1]], borderwidth=3, relief="solid", background="#DFE8F6").grid(column=1, row=x + 2, sticky=NSEW)
            ttk.Combobox(repairPOSfieldsTL, state="normal", values=["%s" % shapefiletofix[errortable[x][0]][errortable[x][1]]]).grid(column=2, row=x + 2, sticky=NSEW)

    # run and convert all 2's to 1's (while leaving the option to change it to something else if wanted.
    counter = 0
    for combobox in repairPOSfieldsTL.children.values():
        if 'combobox' in str(combobox):
            if shapefiletofix[errortable[counter][0]][errortable[counter][1]] == 2:
                combobox.set(1)
            else:
                combobox.set("Invalid Code")
            counter = counter +1

    # finally add the commit button to the bottom
    ttk.Button(repairPOSfieldsTL, text="Commit Changes", command=lambda: commitPOSchanges(errortable, shapefiletofix, freshwater, speciesname)).grid(column=2, row=20, sticky=NSEW)

    # Add a fill all button
    test = ttk.Entry(repairPOSfieldsTL)
    test.grid(column=1, row=20, sticky=NSEW)
    ttk.Button(repairPOSfieldsTL, text="Fill All", command=lambda: fillallPOS(test, field)).grid(column=0, row=20, sticky=NSEW)

    # give weight to the rows and column
    repairPOSfieldsTL.columnconfigure((0, 1, 2), weight=1)
    repairPOSfieldsTL.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20), weight=1)

    # fill the remaing space
    for child in repairPOSfieldsTL.winfo_children():
        child.grid_configure(padx=2, pady=5)

# Take the exisiting CRS and convert to WGS 84
def changeCRS(shapefiletofix, speciesname, freshwater):
    # print the current CRS
    print(shapefiletofix.crs)

    try:
        shapefiletofix = shapefiletofix.to_crs({'init': 'epsg:4326'})
        # after all changes have occurred then save the file
        fp = locationofmaps.get()
        shapefiletofix.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
    except:
        messagebox.showerror(title="Global Llama", message="Error when transforming data")

    # print the new crs
    print(shapefiletofix.crs)

    # create the new map
    rownumber = (tablerownumber.get())
    createmap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname, freshwater)

# the shell for the map attributes testing
def maptests(speciesname, freshwater):
    global maptestslevel

    # create the toplevel to house everything
    # position of parent window
    x = root.winfo_x()
    y = root.winfo_y()

    # screen height
    xh = root.winfo_screenheight()

    # size of parent window
    w = simplesearchframe.winfo_width()
    h = simplesearchframe.winfo_height()

    # get the size of toolbar
    j = top.winfo_height()

    # set the width to the width of the
    maptestslevel = Toplevel()
    maptestslevel.config(background="#DFE8F6")
    maptestslevel.geometry('%dx%d+%d+%d' % (w, xh-(j*2)-h-100, x, y+h+j+95))

    # create the table headers
    ttk.Label(maptestslevel, text="Attribute Test", borderwidth=3, relief="solid", background="#DFE8F6",  anchor=CENTER, font=("bold")).grid(row=0, column=0, sticky=NSEW)
    ttk.Label(maptestslevel, text="Result", borderwidth=3, background="#DFE8F6", relief="solid", anchor=CENTER, font=("bold")).grid(row=0, column=1, sticky=NSEW)
    # get the data from the designated location
    fp = locationofmaps.get()
    # read shapefile from file
    data = geopandas.read_file(fp, driver='ESRI Shapefile', layer=speciesname)

    # check to see if backupfolder exists if not then create it
    if os.path.isdir("%s/backups" % fp) == False:
        os.makedirs("%s/backups" % fp)

    # if the file doesn't exist in backups then create a backup
    if os.path.exists("%s/backups/%s.shp" % (fp, speciesname)) == False:
        data.to_file("%s/backups/" % fp, driver='ESRI Shapefile', layer=speciesname)

    # check that all required fields are present, and identify fields that need to be removed
    if freshwater == "NoValue":
        freshwater = messagebox.askyesno(message="Is this species mapped with hydrobasins?")

    checkpoly = checkpolygonfields(data, freshwater)

    # if any required fields are missing then flag the error
    if len(checkpoly[0]) > 0:
        # check to see if this is a species that should be mapped with hydrobasins or not
        if "BASIN_ID" in checkpoly[0]:
            if freshwater == False:
                # if yes then remove BASIN_ID from the results
                while "BASIN_ID" in checkpoly[0]: checkpoly[0].remove("BASIN_ID")
                # recheck length, if still greater than 0 then there multiple required missing so flag error
                if len(checkpoly[0]) > 0:
                    ttk.Label(maptestslevel, text="Required attribute fields are missing", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=1, column=0, sticky=NSEW)
                    ttk.Button(maptestslevel, text="Fix", command=lambda: fixrequiredattributes(data, freshwater, checkpoly[0], speciesname)).grid(row=1, column=1)
                else:
                    ttk.Label(maptestslevel, text="All Required attributes present", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=1, column=0, sticky=NSEW)
                    ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=1, column=1, sticky=NSEW)
            # if no then flag the message,
            else:
                ttk.Label(maptestslevel, text="Required attribute fields are missing", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=1, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: fixrequiredattributes(data, freshwater, checkpoly[0], speciesname)).grid(row=1, column=1)
        else:
            ttk.Label(maptestslevel, text="Required attribute fields are missing", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=1, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: fixrequiredattributes(data, freshwater, checkpoly[0], speciesname)).grid(row=1, column=1)
    # if list is not greater than 0, then all required are present
    else:
        ttk.Label(maptestslevel, text="All Required attributes present", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=1, column=0, sticky=NSEW)
        ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=1, column=1, sticky=NSEW)

    # check remaining against the optional, if any non valid attributes then flag this error
    if len(checkpoly[1]) > 0:
        ttk.Label(maptestslevel, text="Non required/optional attributes present", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=2, column=0, sticky=NSEW)
        ttk.Button(maptestslevel, text="Fix", command=lambda: dropextrafields(data, speciesname, freshwater)).grid(row=2, column=1)
    else:
        ttk.Label(maptestslevel, text="No extra attributes present", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=2, column=0, sticky=NSEW)
        ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=2, column=1, sticky=NSEW)

    # check to see if any errors have been detected in the BINOMIAL column
    binomerrors = checkfield(data, 'BINOMIAL')
    if len(binomerrors) > 0:
        if binomerrors[0][0] == "Binomial Error":
            ttk.Label(maptestslevel, text="Binomial attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=3, column=0, sticky=NSEW)
            ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=3, column=1, sticky=NSEW)
        else:
            ttk.Label(maptestslevel, text="Binomial attribute doesn't match SIS name", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=3, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: repairbinomialfield(data, speciesname, freshwater)).grid(row=3, column=1)
    else:
        ttk.Label(maptestslevel, text="Validity of binomial field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=3, column=0, sticky=NSEW)
        ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=3, column=1, sticky=NSEW)

    # check to see if any errors have been detected in the PRESENCE column
    perrors = checkfield(data, 'PRESENCE')
    if len(perrors) > 0:
        if perrors[0][0] == "Presence Error":
            ttk.Label(maptestslevel, text="Presence attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=4, column=0, sticky=NSEW)
            ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=4, column=1, sticky=NSEW)
        else:
            ttk.Label(maptestslevel, text="Presence code error detected", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=4, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(data, speciesname, freshwater, perrors, "presence")).grid(row=4, column=1)
    else:
        ttk.Label(maptestslevel, text="Validity of presence codes", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=4, column=0, sticky=NSEW)
        ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=4, column=1, sticky=NSEW)

    # check to see if any errors have been detected in the ORIGIN column
    oerrors = checkfield(data, 'ORIGIN')
    if len(oerrors) > 0:
        if oerrors[0][0] == "Origin Error":
            ttk.Label(maptestslevel, text="Origin attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=5, column=0, sticky=NSEW)
            ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=5, column=1, sticky=NSEW)
        else:
            ttk.Label(maptestslevel, text="Origin code error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=5, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(data, speciesname, freshwater, oerrors, "origin")).grid(row=5, column=1)
    else:
        ttk.Label(maptestslevel, text="Validity of origin codes", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=5, column=0, sticky=NSEW)
        ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=5, column=1, sticky=NSEW)

    # check to see if any errors have been detected in the SEASONAL column
    serrors = checkfield(data, 'SEASONAL')
    if len(serrors) > 0:
        if serrors[0][0] == "Seasonal Error":
            ttk.Label(maptestslevel, text="Seasonal attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=6, column=0, sticky=NSEW)
            ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=6, column=1, sticky=NSEW)
        else:
            ttk.Label(maptestslevel, text="Seasonal code error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=6, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(data, speciesname, freshwater, serrors, "seasonal")).grid(row=6, column=1)
    else:
        ttk.Label(maptestslevel, text="Validity of seasonal codes", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=6, column=0, sticky=NSEW)
        ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=6, column=1, sticky=NSEW)

    # check to see if any errors have been detected in the COMPILER column
    cerrors = checkfield(data, 'COMPILER')
    if len(cerrors) > 0:
        if cerrors[0][0] == "Compiler Error":
            ttk.Label(maptestslevel, text="Compiler attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=7, column=0, sticky=NSEW)
            ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=7, column=1, sticky=NSEW)
        else:
            ttk.Label(maptestslevel, text="Compiler code error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=7, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(data, speciesname, freshwater, cerrors, "compiler")).grid(row=7, column=1)
    else:
        ttk.Label(maptestslevel, text="Validity of compiler attribute", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=7, column=0, sticky=NSEW)
        ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=7, column=1, sticky=NSEW)

    # check to see if any errors have been detected in the COMPILER column
    yerrors = checkfield(data, 'YEAR')
    if len(yerrors) > 0:
        if yerrors[0][0] == "Year Error":
            ttk.Label(maptestslevel, text="Year attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=8, column=0, sticky=NSEW)
            ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=8, column=1, sticky=NSEW)
        else:
            ttk.Label(maptestslevel, text="Year attribute error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=8, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(data, speciesname, freshwater, yerrors, "year")).grid(row=8, column=1)
    else:
        ttk.Label(maptestslevel, text="Validity of year attribute", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=8, column=0, sticky=NSEW)
        ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=8, column=1, sticky=NSEW)

    # check to see if any errors have been detected in the COMPILER column
    citerrors = checkfield(data, 'CITATION')
    if len(citerrors) > 0:
        if citerrors[0][0] == "Citation Error":
            ttk.Label(maptestslevel, text="Citation attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=9, column=0, sticky=NSEW)
            ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=9, column=1, sticky=NSEW)
        else:
            ttk.Label(maptestslevel, text="Citation attribute error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=9, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: repaircitationfield(data, speciesname, freshwater)).grid(row=9, column=1)
    else:
        ttk.Label(maptestslevel, text="Validity of citation attribute", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=9, column=0, sticky=NSEW)
        ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=9, column=1, sticky=NSEW)

    # check that the projection system being used is correct
    if data.crs['init'] != "epsg:4326":
        ttk.Label(maptestslevel, text="Coordinate Reference System Error", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=10, column=0, sticky=NSEW)
        ttk.Button(maptestslevel, text="Fix", command=lambda: changeCRS(data, speciesname, freshwater)).grid(row=10, column=1)
    else:
        ttk.Label(maptestslevel, text="Coordinate Reference System Check", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=10, column=0, sticky=NSEW)
        ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=10, column=1, sticky=NSEW)

    # if no attribute errors (i.e. all required present, and all extra removed) check the order
    if len(checkpoly[0]) == 0 and len(checkpoly[1]) == 0:
        if checkattributeorder(data):
            ttk.Label(maptestslevel, text="Attribute order", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=11, column=0, sticky=NSEW)
            ttk.Label(maptestslevel, text="PASSED", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=11, column=1, sticky=NSEW)
        else:
            ttk.Label(maptestslevel, text="Attributes in Wrong Order", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=11, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: reorganiseattributes(data, speciesname, freshwater)).grid(row=11, column=1)
    else:
        ttk.Label(maptestslevel, text="Can't check order at the moment", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=11, column=0, sticky=NSEW)
        ttk.Label(maptestslevel, text="N/A", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=11, column=1,sticky=NSEW)

    # give weight to the rows and column
    maptestslevel.columnconfigure((0, 1), weight=1)
    maptestslevel.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)

    # fill the remaing space
    for child in maptestslevel.winfo_children():
        child.grid_configure(padx=5, pady=2)

# activate the map engine if off, or turn it off if it on
def mapengineswitch():
    global mapdriver
    global databasera
    # first check if they have provided map data if not offer them the chance to open it from here
    rownumber = (tablerownumber.get())

    # Get the current species genus and name from the table
    output = databasera.iat[rownumber, 1]
    output2 = databasera.iat[rownumber, 2]

    if mapengineactive.get() == 0:
        # visual stuff to show loading
        mapenginetext.set("Loading...")
        root.update()
        # set the tracking variable to show that the mapengine is running
        mapengineactive.set(1)
        # create map for species, overwrite if already there
        if (createmap("%s_%s" % (output, output2))) == 0:
            messagebox.showerror(title="Mysterious Rubber Duck", message="No map for this species could be found")
            return 0
        # create the map driver itself
        webbrowser.open("%s\\SpatialDataStore\\%s_%s.html" % (filedir, output, output2), new=0)
        # then run the map checks required
        maptests("%s_%s" % (output, output2), "NoValue")
        # change the button text
        mapenginetext.set("Stop Maps")
    else:
        mapenginetext.set("Start Maps")
        mapengineactive.set(0)

# advance to the next menu section to review
def gotonextmenuitem():
    driver.implicitly_wait(2)
    global fastreviewdirections
    global reviewmenuplacetracker

    # click the current menu option
    driver.find_element_by_xpath("//*[contains(text(), '%s')]" % fastreviewdirections.iat[(reviewmenuplacetracker.get() % len(fastreviewdirections)), 0]).click()
    driver.find_element_by_xpath("//*[contains(text(), '%s')]" % fastreviewdirections.iat[(reviewmenuplacetracker.get() % len(fastreviewdirections)), 1]).click()

    # catch the 0 exception
    reviewmenuplacetracker.set((reviewmenuplacetracker.get()) + 1)

# go to the previous menu section to review
def gotopreviousmenutiem():
    driver.implicitly_wait(2)
    global fastreviewdirections
    global reviewmenuplacetracker

    # click the current menu option
    driver.find_element_by_xpath("//*[contains(text(), '%s')]" % fastreviewdirections.iat[
        (reviewmenuplacetracker.get() % len(fastreviewdirections)), 0]).click()
    driver.find_element_by_xpath("//*[contains(text(), '%s')]" % fastreviewdirections.iat[
        (reviewmenuplacetracker.get() % len(fastreviewdirections)), 1]).click()

    # catch the 0 exception
    reviewmenuplacetracker.set((reviewmenuplacetracker.get()) - 1)

# open and go to the admin fields ask if the assessment has passed or not and submit appropriate information
def gotoadminfunc():
    # navigate using the task bar to the admin section
    driver.find_element_by_css_selector(".x-form-trigger.x-form-trigger-arrow").click()
    driver.find_element_by_xpath("//*[contains(text(), 'Admin View')]").click()
    driver.find_element_by_xpath("//*[contains(text(), 'Red List Assessment')]").click()
    driver.find_element_by_xpath("//*[contains(text(), 'Assessment Information')]").click()

    # prompt has assessment passed? if yes then pass it all, if no then return assessment, insert notes field
    passresponse = messagebox.askyesnocancel(message="Has the assessment passed?")
    if passresponse == True:
        date = datetime.datetime.now()
        driver.find_element_by_xpath("//*[contains(text(), '--- Select ---')]").click()
        driver.find_element_by_xpath("//*[contains(text(), 'Done')]").click()
        databox = driver.find_element_by_css_selector(".gwt-TextBox")
        databox.clear()
        databox.send_keys("%s-%s-%s" % (date.year, date.month, date.day))
        driver.find_elements_by_xpath("//*[contains(text(), '--- Select ---')]")[1].click()
        driver.find_element_by_xpath("//*[contains(text(), 'Passed')]").click()
        driver.find_element_by_xpath("//*[contains(text(), 'Save')]").click()
    elif passresponse == False:
        date = datetime.datetime.now()
        driver.find_element_by_xpath("//*[contains(text(), '--- Select ---')]").click()
        driver.find_element_by_xpath("//*[contains(text(), 'Done')]").click()
        databox = driver.find_element_by_css_selector(".gwt-TextBox")
        databox.clear()
        databox.send_keys("%s-%s-%s" % (date.year, date.month, date.day))
        driver.find_elements_by_xpath("//*[contains(text(), '--- Select ---')]")[1].click()
        driver.find_element_by_xpath("//*[contains(text(), 'Returned for Improvements')]").click()
        improvtextbox = driver.find_elements_by_css_selector(".gwt-TextArea")[3]
        improvtextbox.clear()
        improvtextbox.send_keys("%s" % notesbox.get('1.0', END))
        driver.find_element_by_xpath("//*[contains(text(), 'Save')]").click()

# open and go to the full text fields
def returntofulltext():
    driver.find_element_by_css_selector(".x-form-trigger.x-form-trigger-arrow").click()
    driver.find_element_by_xpath("//*[contains(text(), 'All Fields View')]").click()
    driver.find_element_by_xpath("//*[contains(text(), 'Text Accounts')]").click()

# open and go to the references page
def gotoreferences():
    driver.find_element_by_xpath("//*[contains(text(), 'References')]").click()
    driver.find_element_by_xpath("//*[contains(text(), 'View References')]").click()

# check to see if there is an assessment, if there is then offer to download it
def checkanddownloadassessments():
    driver.find_element_by_xpath("//*[contains(text(), 'Attachments')]").click()
    driver.find_element_by_xpath("//*[contains(text(), 'Manage Attachments')]").click()

    #try:
        # find and click the ok button
        #driver.find_element_by_xpath("//*[contains(text(), 'There are no attachments for this assessment.')]").find_element_by_xpath("//*[contains(text(), 'OK')]").click()
        #messagebox.showinfo("Never seen invisible mountain llama", "No Attachment found")
    #except:
        #llama = messagebox.askyesno(title="Light Footed Super Sneaky Llama", message="Attachment found, do you want to download it?", icon='question')
        #print("%s" % llama)
        #pass

# generates an excel template for importing data
def generatetemplate():
    try:
        # create the panda datastrucuture with the correct headings
        saveto = StringVar()
        saveto.set("LLAMA")
        template = pandas.DataFrame(index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], columns=['ID','Genus','Species','Threat Category','Criteria String','Criteria Passed?','Validity Passed?','Map Passed?','Notes','Assessment Passed?'])
        saveto.set(filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=(("Excel Workbook", "*.xlsx"), ("All Files", "*."))))

        # check if no place has been provided.
        if (saveto.get() == "llama"):
            raise IOError

        # save the not passed to the three columns
        template.iat[0, 5] = "Not Passed"
        template.iat[0, 6] = "Not Passed"
        template.iat[0, 7] = "Not Passed"

        # save the assessment passed formula
        template.iat[0, 9] = '=NOT(OR(G2="NOT PASSED",H2="NOT PASSED",I2="NOT PASSED"))'

        # create the Pandas Excel writer
        writertemp = pandas.ExcelWriter(saveto.get(), engine='xlsxwriter')

        # convert the existing dataframe to the excel writer object
        template.to_excel(writertemp, sheet_name='Sheet 1')

        #Get the writer's workbook and worksheet objects
        worksheet = writertemp.sheets['Sheet 1']

        # set the column width
        worksheet.set_column('A:J', 18, None)

        # save the file
        writertemp.save()

        #report success
        messagebox.showinfo("Greater Spotted Swimming Llama", "Template has been generated")

    except:
        messagebox.showerror("Lesser Stripied Flying Llama", "Template has not been generated because of some error")

# event handler for when the user choses the assessment they want to go to.
def gotooption(event):
    global dspchoice
    driver.implicitly_wait(2)
    # go to the option selected from the combo box
    actionChains = ActionChains(driver)
    actionChains.double_click(driver.find_element_by_xpath("//*[contains(text(), '%s')]" % assessmentvar.get())).perform()

    # hide the selection menu
    dspchoice.withdraw()

# function to create the map for the current species
def createmap(speciesname):
    global filedir

    # get the location of the maps from the global variable
    fp = locationofmaps.get()

    # try to read the shapefile from file
    try:
        data = geopandas.read_file(fp, driver='ESRI Shapefile', layer=speciesname)
    except:
        return 0

    # transform the data into a json format for the folium engine
    jsondata = data.to_json()
    # map properties
    map = folium.Map([0, 0], tiles='Stamen Terrain')
    # set the default zoom to the current extent of the map
    bounds = data.total_bounds
    map.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
    # add the polygon to the map
    polygon = folium.features.GeoJson(jsondata, style_function=lambda feature: {'fillColor': '#ff0000' if feature['properties']['PRESENCE'] == 1 else '#ff9d00' if feature['properties']['PRESENCE'] == 2 else '#fffa00' if feature['properties']['PRESENCE'] == 3 else '#37ff00' if feature['properties']['PRESENCE'] == 4 else '#003fff' if feature['properties']['PRESENCE'] == 5 else '#e900ff', 'color': '#ff0000' if feature['properties']['ORIGIN'] == 1 else '#ff9d00' if feature['properties']['ORIGIN'] == 2 else '#fffa00' if feature['properties']['ORIGIN'] == 3 else '#37ff00' if feature['properties']['ORIGIN'] == 4 else '#003fff' if feature['properties']['ORIGIN'] == 5 else '#e900ff', 'fillOpacity': '0.6'})
    map.add_child(polygon)
    # convert the attribute table data for this species into a html table for this species
    # first drop the geometry column, for aesthetic purposes
    table = data.drop("geometry", axis=1)
    # convert table to html format
    table.to_html("%s\\TempFiles\\temptabledata.txt" % filedir, border=0)
    # open up the table outline
    tableoutline = open("%s\\HTMLFiles\\TableOutline.txt" % filedir)
    # open up the html table
    tocopyin = open("%s\\TempFiles\\temptabledata.txt" % filedir)
    # define the stylesheet location for writing
    location = "%s/HTMLFiles/stylesheet.css" % filedir
    # define the location to save the table html
    finalfile = open("%s\\TempFiles\\%s_temp.html" % (filedir, speciesname), "w+")

    # loop through the html and insert the created html text and the local location of the stylesheet
    for line in tableoutline:
        finalfile.write(line)
        if 'href=' in line:
            finalfile.write("\"%s\">" % location)
        if '<div class="fixed">' in line:
            for line2 in tocopyin:
                finalfile.write("%s" % line2)

    # once looped close open files, and tidy up the temp files
    tableoutline.close()
    tocopyin.close()
    finalfile.close()
    os.remove("%s\\TempFiles\\temptabledata.txt" % filedir)

    with open("%s/TempFiles/%s_temp.html" % (filedir, speciesname)) as myfile:
        data = myfile.read()

    # add this to the new map
    map.get_root().html.add_child(folium.Element(data))
    # export the map so that it can be opened by the program
    map.save("%s\\SpatialDataStore\\%s.html" % (filedir, speciesname))
    # delete the temp file
    os.remove("%s/TempFiles/%s_temp.html" % (filedir, speciesname))

# prototype function to allow selection of the available assessments on the taxon page
def assessmentlistchooser():
    global dspchoice
    assessmentvar.set("Click to choose assessment")
    list2 = []

    # set the size and position of the box to appear
    # position of parent window
    x = root.winfo_x()
    y = root.winfo_y()

    # size of parent window
    w = simplesearchframe.winfo_width()
    h = simplesearchframe.winfo_height()

    # place the top window
    dspchoice.geometry('%dx%d+%d+%d' % (w/2, h/6, x + w/7, y + h/2))
    dspchoice.resizable(0, 0)

    dspchoice.deiconify()

    # first of all get a list of all of assessments
    # get a list of all normal assessments
    listofassessments = driver.find_elements_by_xpath("//span[@class='regular-style']")
    # first pull out the drafts
    for x in range(0, len(listofassessments)):
        list2.append("%s" % listofassessments[x].text)

    combobox = ttk.Combobox(dspchoice, textvariable=assessmentvar, values=list2, state="readonly")
    combobox.grid(row=0, column=0, columnspan=3, sticky=NSEW)

    dspchoice.columnconfigure((0, 1, 2), weight=1)
    dspchoice.rowconfigure((0, 1, 2), weight=1)

    # set up the event to monitor for the combbox option being selected
    combobox.bind('<<ComboboxSelected>>', gotooption)

    # clear lists option
    list2.clear()
    listofassessments.clear()

# open and run the validate assessment function in SIS, sends username and password via url
def validateassessment(buttontext):
    global passwordvariable
    global usernamevariable
    global validatebuttontext

    if (buttontext == "Validate"):
        # get the assessment id from the URL string
        currenturl = driver.current_url
        assessmentid = currenturl.split("A", 1)[1]

        driver.execute_script("window.open('http://%s:%s@sis.iucnsis.org/apps/org.iucn.sis.server.extensions.integrity/validate?id=%s&type=submitted_status')" % (usernamevariable, passwordvariable, assessmentid))
        driver.switch_to.window(driver.window_handles[1])
        try:
            element = WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Click here to view')]")))
        finally:
            element.click()
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            validatebuttontext.set("Finish Validation")

    elif buttontext == "Finish Validation":
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        validatebuttontext.set("Validate")

# review a single species.
def singlereview():
    # ask user where they want to save the review

    # check to see if any data in here already, set the rownumber to the database length so that it appends to exisiting data

    # generate the template to save there and set the save file location to that

    # search for all submitted assessments
    #assessmentlist("submitted")
    # present user with drop down of all assessments to chose from

    # navigate to that assessment

    # navigate to the review assistant page

    # get the name of species

    # get the
    #speciesname = driver.find_element_by_css_selector(".gwt-HTML.SIS_taxonSummaryHeader.x-component").text
    pass

# generate a template for the taxonomic adder table
def generatetadaddertemplate():
    try:
        # create the panda datastrucuture with the correct headings
        saveto = StringVar()
        saveto.set("LLAMA")
        template = pandas.DataFrame(index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], columns=['Kingdom','KCheck','Phylum','PCheck','Class','CCheck','Order','OCheck','Family','FCheck','Genus','GCheck','Species','SCheck','Infrarank','ICheck','Taxonomic Authority','Taxonomic Reference','Working Set','Species Added?','Notes','ID','Preprocessed?'])
        saveto.set(filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=(("Excel Workbook", "*.xlsx"), ("All Files", "*."))))

        # check if no place has been provided.
        if (saveto.get() == "llama"):
            raise IOError

        # create the Pandas Excel writer
        writertemp = pandas.ExcelWriter(saveto.get(), engine='xlsxwriter')

        # convert the existing dataframe to the excel writer object
        template.to_excel(writertemp, sheet_name='Sheet 1')

        #Get the writer's workbook and worksheet objects
        worksheet = writertemp.sheets['Sheet 1']

        # set the column width
        worksheet.set_column('A:W', 12, None)
        worksheet.set_column('S:S', 19, None)

        # save the file
        writertemp.save()

        #report success
        messagebox.showinfo("Greater Spotted Swimming Llama", "Template has been generated")

    except:
        messagebox.showerror("Lesser Stripied Flying Llama", "Template has not been generated because of some error")

# hide everything on the review page
def hideall():
    # review asssistant elements
    goforward.grid_forget()
    goback.grid_forget()
    previouspeciesvariable.grid_forget()
    currentspeciesnamelabel.grid_forget()
    nextspecieslabel.grid_forget()
    candclabel.grid_forget()
    verifiedcheck.grid_forget()
    criteriacheck.grid_forget()
    mapscheck.grid_forget()
    notesbox.grid_forget()
    reviewtoolsbutton.grid_forget()
    skiptobutton.grid_forget()
    entryvariable1.grid_forget()
    assessmentnumber.grid_forget()
    hidetoolsbutton.grid_forget()
    reviewtoolsbutton.grid_forget()

    # make labels invisible
    textlabel1.grid_forget()
    textlabel2.grid_forget()
    textlabel3.grid_forget()
    textlabel4.grid_forget()
    textlabel5.grid_forget()
    textlabel6.grid_forget()
    textlabel7.grid_forget()

    # make the navigation buttons and text reappear
    reviewassistantmenu.grid(column=0, row=2, sticky=N, columnspan=3)
    continuewhereyouleft.grid(column=0, row=3, sticky=N, columnspan=3)
    populatebutton.grid(column=0, row=4, sticky=N, columnspan=3)
    generatetemplatebutton.grid(column=0, row=5, sticky=N, columnspan=3)

# go to taxonomic assistant page
def gototaxspecial():
    root.geometry('%dx%d+%d+%d' % (510, 2*(screen_height/3), screen_width - 535, 5))
    root.update()

    taxadderframe.tkraise()

# return to tax menu and restore screen size
def taxreturntomainspecial():
    global details

    # rest the screen dimensions
    root.geometry('%dx%d+%d+%d' % (510, 510, screen_width - 535, 5))

    # save the current state of the data
    taxsave()

    # close the details box if open
    try:
        details.destroy()
    except:
        pass

    taxadderassistantframe.tkraise()
    root.update()

# function to grab the taxon ID from the URL
def gettaxonID():
    global databaseta

    # first get the URL, pull the TAXON id out, and store it in the excel document.
    url = driver.current_url
    spliturl = url.split('T')

    return spliturl[1]

# add species or other level to SIS.
def add(leveltoadd, databasecolumn, button):
    # global variables needed
    global databaseta
    global TaxCurrentSpeciesDict
    global details

    hierarchylist2SIStext = ["SISKingdomSV", "SISPhylumSV", "SISClassSV", "SISOrderSV", "SISFamilySV", "SISGenusSV", "SISSpeciesSV"]
    hierarchylist2usertext = ["userKingdomSV", "userPhylumSV", "userClassSV", "userOrderSV", "userFamilySV", "userGenusSV", "userSpeciesSV"]

    rownumber = taxonomyrowtrackerIntVar.get()

    if leveltoadd == "species":
        # set implicit wait to five seconds to cover most load times
        driver.implicitly_wait(5)
        # go back to the homepage
        resetimage = driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel")
        driver.execute_script("arguments[0].click();", resetimage)
        # get the variables needed
        speciesvalue = levelnameSV.get()
        taxauthvalue = taxauthSV.get()
        taxrefvalue = taxrefSV.get()
        workingsetvalue = workingsetSV.get()

        # get the genus ID from internal dictionary
        genusid = databaseta.iat[rownumber, 21]
        try:
            # open advanced search box
            driver.find_element_by_xpath("//*[contains(text(), 'Advanced Search')]").click()
            # find searchbox
            searchbox = driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".gwt-TextBox")
            # send the search term
            searchbox.clear()
            searchbox.send_keys("%s" % genusid)
            sendkeyschecker(searchbox, str(genusid))
            # search for it
            driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".x-btn-text").click()
        except:
            messagebox.showerror("Generic Error Llama", "Error finding species, try again")
            return 1

        # open taxomatic tools, and open new child taxon
        try:
            driver.find_element_by_xpath("//*[contains(text(), 'Taxomatic Tools')]").click()
            driver.find_element_by_xpath("//*[contains(text(), 'Add New Child Taxon')]").click()
        except:
            messagebox.showerror("Generic Error Llama", "Error adding new species, try again")
            return 1

        # find the various boxes and input the data from the table.
        # class 3 is the species name, class 4 is the authority box
        try:
            listofall = driver.find_elements_by_css_selector(".x-form-field.x-form-text")
            speciesname = listofall[2]
            authorityname = listofall[3]
            speciesname.clear()
            authorityname.clear()
            authorityname.send_keys("%s" % taxauthvalue)
            sendkeyschecker(authorityname, str(taxauthvalue))
            speciesname.send_keys("%s" % speciesvalue)
            sendkeyschecker(speciesname, str(speciesvalue))

            test1 = listofall[5]
            test1.click()
            listofresponses1 = driver.find_elements_by_css_selector(".x-combo-list-item")
            listofresponses1[0].click()

            test2 = listofall[6]
            test2.click()
            listofresponses2 = driver.find_elements_by_css_selector(".x-combo-list-item")
            listofresponses2[0].click()

            # save and close
            time.sleep(1)
            driver.find_element_by_xpath("//*[contains(text(), 'Save and Close')]").click()
        except:
            messagebox.showerror("Generic Error Llama", "Error adding new data to SIS form")
            return 1

        # add to working set specified.
        try:
            # implicit wait
            driver.implicitly_wait(5)
            time.sleep(1)
            driver.find_element_by_xpath("//*[contains(text(), 'Yes')]").click()

            # get the full list of checklists (as this is all the workingsets you are subscribed to)
            list = driver.find_elements_by_css_selector(".x-view-item.x-view-item-check")
            for x in list:
                try:
                    daslist = x.find_elements_by_xpath(".//*")
                    for y in daslist:
                        if y.text == workingsetvalue:
                            daslist[3].click()
                            driver.find_element_by_xpath("//*[contains(text(), 'Add to Selected')]").click()
                            break
                    else:
                        continue
                    break
                except:
                    continue

        except:
            messagebox.showerror("Generic Error Llama", "Unable to add to working set, manually add")
            return 1

        # if tax reference indicated, then add it
        if taxrefvalue != "":
            try:
                driver.find_elements_by_css_selector(".gwt-Image.x-component")[11].click()
                driver.find_element_by_xpath("//*[contains(text(), 'Reference Search')]").click()
                # find the title of the paper input box and input the title
                titleboxs = driver.find_elements_by_css_selector('.x-form-field.x-form-text')
                titleboxs[3].clear()
                titleboxs[3].send_keys("%s" % taxrefvalue)
                sendkeyschecker(titleboxs[3], str(taxrefvalue))
                # find and press the search button
                titlesearchbox = driver.find_elements_by_xpath("//*[contains(text(), 'Search')]")
                titlesearchbox[1].click()
            except:
                messagebox.showerror("Generic Error Llama", "Error searching for name")
                return 1

            # search for the exact name if found then select and add, if not found then throw warning
            # set implicit wait to shorter to minimise wait time
            driver.implicitly_wait(0.5)
            # loop to wait till the search results have loaded
            while TRUE:
                try:
                    driver.find_element_by_xpath("//*[contains(text(), 'Loading...')]")
                except:
                    break
            # set the implicit wait back to standard
            driver.implicitly_wait(5)
            # get the list of references found
            try:
                listofnames = driver.find_elements_by_css_selector(".x-grid3-cell-inner.x-grid3-col-title")
                # loop through checking the title of each one against the provided reference.
                for a in listofnames:
                    try:
                        a.find_element_by_xpath("//*[contains(text(), '%s')]" % taxrefvalue)
                        if a.text == taxrefvalue:
                            a.click()
                            driver.find_element_by_xpath("//*[contains(text(), 'Attach Selected')]").click()
                            driver.find_element_by_xpath("//*[contains(text(), 'OK')]").click()
                            driver.find_element_by_css_selector(".x-nodrag.x-tool-close.x-tool.x-component").click()
                    except:
                        print("")
                        break
            except:
                messagebox.showerror("Generic Error Llama", "Unable to attach new reference")
                return 1

        # if it's got this far then all is good, save the species to the database
        try:
            # save the current name, taxonomic authority, taxonomic reference and workingset to the database (as user may have altered)
            databaseta.iat[rownumber, 12] = speciesvalue
            databaseta.iat[rownumber, 16] = taxauthvalue
            databaseta.iat[rownumber, 17] = taxrefvalue
            databaseta.iat[rownumber, 18] = workingsetvalue
            # change the SIS species label to this new value
            SISSpeciesSV.set(speciesvalue)
            # change the user side to blank
            userSpeciesSV.set("")
            # mark "Species added" column to yes and change the species check value to the name added
            databaseta.iat[rownumber, 19] = "Yes"
            databaseta.iat[rownumber, 13] = "M"
            # rerun the arrow setter and duplicate remover
            arrowsorter()
            duplicateremover()
            # save it all
            taxsave()
            # try to close the window
            button.set("Details")
            details.destroy()

        except:
            messagebox.showerror("Generic Error Llama", "Unable to Save to file")
            return 1

    elif(leveltoadd == "genus" or "family" or "order" or "class" or "phylum"):
        # set implicit wait to five seconds to cover most load times
        driver.implicitly_wait(5)
        # go back to the homepage
        resetimage = driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel")
        driver.execute_script("arguments[0].click();", resetimage)
        # get the variables needed
        taxlevelvalue = levelnameSV.get()
        taxauthvalue = taxauthSV.get()
        taxrefvalue = taxrefSV.get()

        # get the taxlevel ID from the ID column
        taxlevelid = databaseta.iat[rownumber, 21]
        try:
            # open advanced search box
            driver.find_element_by_xpath("//*[contains(text(), 'Advanced Search')]").click()
            # find searchbox
            searchbox = driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".gwt-TextBox")
            # send the search term
            searchbox.clear()
            searchbox.send_keys("%s" % taxlevelid)
            sendkeyschecker(searchbox, str(taxlevelid))
            # search for it
            driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".x-btn-text").click()
        except:
            messagebox.showerror("Generic Error Llama", "Error finding taxlevel, try again")
            return 1

        # open taxomatic tools, and open new child taxon
        try:
            driver.find_element_by_xpath("//*[contains(text(), 'Taxomatic Tools')]").click()
            driver.find_element_by_xpath("//*[contains(text(), 'Add New Child Taxon')]").click()
        except:
            messagebox.showerror("Generic Error Llama", "Error adding new taxlevel, try again")
            return 1

        # find the various boxes and input the data from the table.
        # class 3 is the species name, class 4 is the authority box
        try:
            listofall = driver.find_elements_by_css_selector(".x-form-field.x-form-text")
            speciesname = listofall[2]
            authorityname = listofall[3]
            speciesname.clear()
            authorityname.clear()
            authorityname.send_keys("%s" % taxauthvalue)
            sendkeyschecker(authorityname, str(taxauthvalue))
            speciesname.send_keys("%s" % taxlevelvalue)
            sendkeyschecker(speciesname, str(taxlevelvalue))

            test1 = listofall[5]
            test1.click()
            listofresponses1 = driver.find_elements_by_css_selector(".x-combo-list-item")
            listofresponses1[0].click()

            test2 = listofall[6]
            test2.click()
            listofresponses2 = driver.find_elements_by_css_selector(".x-combo-list-item")
            listofresponses2[0].click()

            # save and close
            time.sleep(1)
            driver.find_element_by_xpath("//*[contains(text(), 'Save and Close')]").click()
        except:
            messagebox.showerror("Generic Error Llama", "Error adding new data to SIS form")
            return 1

        # if tax reference indicated, then add it
        if taxrefvalue != "":
            try:
                driver.find_elements_by_css_selector(".gwt-Image.x-component")[11].click()
                driver.find_element_by_xpath("//*[contains(text(), 'Reference Search')]").click()
                # find the title of the paper input box and input the title
                titleboxs = driver.find_elements_by_css_selector('.x-form-field.x-form-text')
                titleboxs[3].clear()
                titleboxs[3].send_keys("%s" % taxrefvalue)
                sendkeyschecker(titleboxs[3], str(taxrefvalue))
                # find and press the search button
                titlesearchbox = driver.find_elements_by_xpath("//*[contains(text(), 'Search')]")
                titlesearchbox[1].click()
            except:
                messagebox.showerror("Generic Error Llama", "Error searching for name")
                return 1

            # search for the exact name if found then select and add, if not found then throw warning
            # set implicit wait to shorter to minimise wait time
            driver.implicitly_wait(0.5)
            # loop to wait till the search results have loaded
            while TRUE:
                try:
                    driver.find_element_by_xpath("//*[contains(text(), 'Loading...')]")
                except:
                    break
            # set the implicit wait back to standard
            driver.implicitly_wait(5)
            # get the list of references found
            try:
                listofnames = driver.find_elements_by_css_selector(".x-grid3-cell-inner.x-grid3-col-title")
                # loop through checking the title of each one against the provided reference.
                for a in listofnames:
                    try:
                        a.find_element_by_xpath("//*[contains(text(), '%s')]" % taxrefvalue)
                        if a.text == taxrefvalue:
                            a.click()
                            driver.find_element_by_xpath("//*[contains(text(), 'Attach Selected')]").click()
                            driver.find_element_by_xpath("//*[contains(text(), 'OK')]").click()
                            driver.find_element_by_css_selector(".x-nodrag.x-tool-close.x-tool.x-component").click()
                    except:
                        print("")
                        break
            except:
                messagebox.showerror("Generic Error Llama", "Unable to attach new reference")
                return 1

        # if it's got this far then all is good, save the tax level to the database
        try:
            # sleep for a second to let the webpage update
            time.sleep(1)
            # save the current name to the database (as user may have altered)
            databaseta.iat[rownumber, databasecolumn] = taxlevelvalue
            databaseta.iat[rownumber, databasecolumn + 1] = "M"
            # update the id at the end with the new ID
            newid = gettaxonID()
            databaseta.iat[rownumber, 21] = int(newid)
            # change the SIS species label to this new value
            buttonchanger(hierarchylist2SIStext[int(databasecolumn/2)], taxlevelvalue)
            # change the user side to blank
            buttonchanger(hierarchylist2usertext[int(databasecolumn/2)], "")
            # iterate through the rest of the column, whereever you get a match check the rest of the info to ensure match and then mark as added
            # get columm before data and store
            previouscolumn = databaseta.iat[rownumber, databasecolumn-2]
            for x in range(rownumber+1, len(databaseta)):
                if databaseta.iat[x, databasecolumn] == taxlevelvalue and databaseta.iat[x, databasecolumn-2] == previouscolumn:
                    databaseta.iat[x, databasecolumn + 1] = "M"
                    databaseta.iat[x, 21] = 0
                    databaseta.iat[x, 21] = int(newid)
            # save it all
            taxsave()
            # rerun the arrow setter and duplicate remover
            arrowsorter()
            duplicateremover()
            # try and close the window
            button.set("Details")
            details.destroy()

        except:
            messagebox.showerror("Generic Error Llama", "Unable to Save to file")
            return 1

# add the data provided and close the sourcesynonym adder box
def addandclosebox():
    global synonymsource
    global databaseta

    # get the rowcounter
    rowcounter = taxonomyrowtrackerIntVar.get()

    # record that species not added
    databaseta.iat[rowcounter, 19] = "No"
    # record a note saying that the species is in the taxonomic source as a synonym
    databaseta.iat[rowcounter, 20] = "Taxonomic source has this as a synonym of %s" % synonymtoadd.get()
    # change the screen to report this info
    buttonchanger("userClassSV", "Source indicated synonym of %s" % synonymtoadd.get())
    taxlabel12.grid(columnspan=3)
    taxlabel12.config(wraplength=250)
    taxsave()

    # hide the window
    synonymsource.withdraw()

# function to add to the notes field that the species couldn't be found within the taxonomic source
def cantfind():
    global synonymsource
    global databaseta

    # get the rowcounter
    rowcounter = taxonomyrowtrackerIntVar.get()

    # record that the species has not been found
    databaseta.iat[rowcounter, 19] = "No"
    # record a note that it was not able to be found in the taxonomic source
    databaseta.iat[rowcounter, 20] = "Unable to find in Taxonomic Source to check"
    # update screen
    buttonchanger("userClassSV", "Unable to find in Taxonomic Source")
    taxlabel12.grid(columnspan=3)
    taxlabel12.config(wraplength=250)
    taxsave()

    # hide the window
    synonymsource.withdraw()

# open box ask for synonym that source says it is, save to sheet and close toplevel
def sourcesynonym():
    global synonymsource
    synonymtoadd.set("")

    synonymsource.deiconify()

    # position of parent window
    x = root.winfo_x()
    y = root.winfo_y()

    # size of parent window
    w = simplesearchframe.winfo_width()
    h = simplesearchframe.winfo_height()

    # place the top window
    synonymsource.geometry('%dx%d+%d+%d' % (w, h / 4, x, y + h + 42))
    synonymsource.resizable(0, 0)

    #box contents
    ttk.Label(synonymsource, text="Synonym source says this species falls under", background="#DFE8F6", font=(None, 12)).grid(row=0, column=1, columnspan=3)
    ttk.Entry(synonymsource, textvariable=synonymtoadd, width=20).grid(row=1, column=0, columnspan=3)
    ttk.Button(synonymsource, text="Add", command=lambda: addandclosebox()).grid(row=1, column=0, columnspan=3, sticky=W)
    ttk.Button(synonymsource, text="Can't Find", command=lambda: cantfind()).grid(row=2, column=0, sticky=E)
    ttk.Button(synonymsource, text="Cancel", command=lambda: synonymsource.withdraw()).grid(row=2, column=1, columnspan=2, sticky=E)

    # space everything out
    synonymsource.columnconfigure((0, 1, 2), weight=1)
    synonymsource.rowconfigure((0, 1, 2, 3, 4), weight=1)

# create details box for tax adder frame
def detailbox(taxlevel, button, databasecolumn):
    global row
    global databaseta
    global details

    rowcounter = taxonomyrowtrackerIntVar.get()

    if button.get() == "Details":
        details = Toplevel()
        details.config(background="#DFE8F6")
        # position of parent window
        x = root.winfo_x()
        y = root.winfo_y()

        # create the text variables
        levelnameSV.set(databaseta.iat[rowcounter, databasecolumn])
        if taxlevel == "species":
            taxauthSV.set(databaseta.iat[rowcounter, 16])
            taxrefSV.set(databaseta.iat[rowcounter, 17])
            workingsetSV.set(databaseta.iat[rowcounter, 18])
        else:
            taxauthSV.set("")
            taxrefSV.set("")
            workingsetSV.set("")

        # size of parent window
        w = simplesearchframe.winfo_width()
        h = simplesearchframe.winfo_height()

        # place the top window
        details.geometry('%dx%d+%d+%d' % (w, h / 4, x, y + h + 42))
        details.resizable(0, 0)

        # create the various buttons and boxes needed
        taxonomiclevel = ttk.Label(details, font=(None, 15), text="%s      " % taxlevel, background="#DFE8F6")
        taxnamelabel = ttk.Label(details, text="Name:", background="#DFE8F6")
        taxnameentry = ttk.Entry(details, textvariable=levelnameSV, width=20)
        taxauthlabel = ttk.Label(details, text="Taxonomic Authority:", background="#DFE8F6")
        taxauthentrybox = ttk.Entry(details, width=20, textvariable=taxauthSV)
        labeltaxref = ttk.Label(details, text="Taxonomic Reference:", background="#DFE8F6")
        taxrefentrybox = ttk.Entry(details,textvariable=taxrefSV, width=20)
        addbutton = ttk.Button(details, text="Add", command=lambda: add(taxlevel, databasecolumn, button))
        markassynonym = ttk.Button(details, text="Problem...", command=lambda: sourcesynonym())
        workingsetentrybox = ttk.Entry(details, textvariable=workingsetSV, width=20)
        labelworkingset = ttk.Label(details, text="Working Set:", background="#DFE8F6")

        taxonomiclevel.grid(column=0, row=0, sticky=W)
        taxnamelabel.grid(column=0, row=1, sticky=W)
        taxnameentry.grid(column=1, row=1, sticky=W)
        taxauthlabel.grid(column=0, row=2, sticky=W)
        taxauthentrybox.grid(column=1, row=2, sticky=W)
        addbutton.grid(column=2, row=1, sticky=(N, S, W), rowspan=2)
        markassynonym.grid(column=2, row=3, sticky=(N, S, W), rowspan=2)
        labeltaxref.grid(column=0, row=3, sticky=W)
        taxrefentrybox.grid(column=1, row=3, sticky=W)
        labelworkingset.grid(column=0, row=4, sticky=W)
        workingsetentrybox.grid(column=1, row=4, sticky=W)

        if taxlevel == "species":
            workingsetentrybox.config(state=NORMAL)
        else:
            workingsetentrybox.config(state=DISABLED)

        # update the text
        button.set("Close")

        # configure over space
        details.columnconfigure((0, 1, 2), weight=1)
        details.rowconfigure((0, 1, 2, 3, 4), weight=1)
    else:
        # hide the window
        button.set("Details")
        details.destroy()

# function to copy the current genus species combo for tax adding purposes
def copyname():
    # copy the combination over to the clipboard for use
    root.clipboard_clear()
    root.clipboard_append(CombinationStringVar.get().rstrip())
    copiedtexVar.set("Copied")
    root.update()

# function to check for synonyms
def synonymchecker(speciestocheck):
    # go back to the homepage
    resetimage = driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel")
    driver.execute_script("arguments[0].click();", resetimage)

    driver.implicitly_wait(1)

    # open advanced search box
    driver.find_element_by_xpath("//*[contains(text(), 'Advanced Search')]").click()

    # unselect the search common names box
    driver.execute_script("arguments[0].click();", driver.find_element_by_id('gwt-uid-8'))

    # unselect the Search Scientific names box
    driver.execute_script("arguments[0].click();", driver.find_element_by_id('gwt-uid-10'))

    # find the input box
    # find searchbox
    searchbox = driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".gwt-TextBox")

    # send the search term
    searchbox.clear()
    searchbox.send_keys("%s" % speciestocheck)
    sendkeyschecker(searchbox, str(speciestocheck))
    time.sleep(1)

    # search for the search button and click it
    driver.find_element_by_css_selector('.x-window.x-component').find_element_by_css_selector(".x-btn-text").click()
    time.sleep(3)

    # if a result has been found then click on it and report success
    try:
        # click the first one
        driver.find_elements_by_css_selector(".search_result_taxon_default")[0].click()
        return 1
    # if not found then report and return 0
    except:
        return 0

# reset advanced search options
def resetadvancedoptions():
    # go back to the homepage
    resetimage = driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel")
    driver.execute_script("arguments[0].click();", resetimage)

    # open advanced search box
    driver.find_element_by_xpath("//*[contains(text(), 'Advanced Search')]").click()

    # unselect the search common names box
    driver.execute_script("arguments[0].click();", driver.find_element_by_id('gwt-uid-8'))

    # unselect the Search Scientific names box
    driver.execute_script("arguments[0].click();", driver.find_element_by_id('gwt-uid-10'))

    # close the advanced options box
    driver.find_element_by_css_selector('.x-nodrag.x-tool-close.x-tool.x-component').click()

# main algorithm for the taxonomy checker
def taxonomychecker(numbertoprocess):
    global databaseta
    global preprocesswindow

    for x in range(0, numbertoprocess):
        rownumber = taxonomyrowtrackerIntVar.get() + x
        try:
            # first search for the genus+species combination
            genusandspecies = searchbyanything("%s %s" % (databaseta.iat[rownumber, 10], databaseta.iat[rownumber, 12]))
            if genusandspecies == 1:
                # if returns 1 then it means a match has been found
                print("Species Found")
                # check the SIS taxonomy reporting any differences you might find
                taxonomyhierarchychecker(rownumber)
                # mark the species as Not added, and a note of already in SIS
                databaseta.iat[rownumber, 19] = "No"
                databaseta.iat[rownumber, 20] = "Already in SIS"
                # raise exception to get out of this iteration of the loop
                raise NameError("LlamaNoise")
            # if not found then run a synonym check
            else:
                genusandspeciessyn = synonymchecker("%s %s" % (databaseta.iat[rownumber, 10], databaseta.iat[rownumber, 12]))
                if genusandspeciessyn == 1:
                    print("Species synonym found")
                    taxonomyhierarchychecker(rownumber)
                    databaseta.iat[rownumber, 19] = "No"
                    databaseta.iat[rownumber, 20] = "Species exists in SIS as a synonym of %s" % genusandspeciessyn
                    resetadvancedoptions()
                    # raise exception to get out of this iteration of the loop
                    raise NameError("LlamaNoise")
                else:
                    print("No species synonym found")
                    resetadvancedoptions()

            # then search for the genus if not marked already as found
            if databaseta.iat[rownumber, 11] == "M":
                databaseta.iat[rownumber, 22] = 1
                raise NameError("LlamaNoise")
            else:
                genusalone = searchbyanything("%s" % (databaseta.iat[rownumber, 10]))
                if genusalone == 1:
                    # if returns 1 then it means a match has been found
                    print("Genus Found")
                    # check the SIS taxonomy reporting any differences you might find
                    taxonomyhierarchychecker(rownumber)
                    # run through the rest of the column if any species have the same genus and family, premark as ok
                    # get the mark values
                    kingdomcheckvalue = databaseta.iat[rownumber, 1]
                    phylumcheckvalue = databaseta.iat[rownumber, 3]
                    classcheckvalue = databaseta.iat[rownumber, 5]
                    ordercheckvalue = databaseta.iat[rownumber, 7]
                    familycheckvalue = databaseta.iat[rownumber, 9]
                    idcheckvalue = databaseta.iat[rownumber, 21]
                    # get the values for testing
                    familycolumn = databaseta.iat[rownumber, 8]
                    genuscolumn = databaseta.iat[rownumber, 10]
                    for y in range(rownumber, len(databaseta)):
                        if databaseta.iat[y, 10] == genuscolumn and databaseta.iat[y, 8] == familycolumn:
                            databaseta.iat[y, 11] = "M"
                            # mark the rest of the columns with the same value that they have thus been found
                            databaseta.iat[y, 1] = kingdomcheckvalue
                            databaseta.iat[y, 3] = phylumcheckvalue
                            databaseta.iat[y, 5] = classcheckvalue
                            databaseta.iat[y, 7] = ordercheckvalue
                            databaseta.iat[y, 9] = familycheckvalue
                            databaseta.iat[y, 21] = idcheckvalue
                    # finally raise exception to get out of this iteration of the loop
                    raise NameError("LlamaNoise")
                # if not found then run a synonym check
                else:
                    genusalonessyn = synonymchecker("%s" % (databaseta.iat[rownumber, 10]))
                    if genusalonessyn == 1:
                        print("Genus Synonym Found")
                        taxonomyhierarchychecker(rownumber)
                        resetadvancedoptions()
                        # raise exception to get out of this iteration of the loop
                        raise NameError("LlamaNoise")
                    else:
                        print("No Genus Synonym Found")
                        resetadvancedoptions()


            # then search for the family
            familyalone = searchbyanything("%s" % (databaseta.iat[rownumber, 8]))
            if familyalone == 1:
                # if returns 1 then it means a match has been found
                print("Family Found")
                # check the SIS taxonomy reporting any differences you might find
                taxonomyhierarchychecker(rownumber)
                # raise exception to get out of this iteration of the loop
                raise NameError("LlamaNoise")
            # if not found then run a synonym check
            else:
                familyalonesyn = synonymchecker("%s" % (databaseta.iat[rownumber, 8]))
                if familyalonesyn == 1:
                    print("Family Synonym Found")
                    taxonomyhierarchychecker(rownumber)
                    resetadvancedoptions()
                    # raise exception to get out of this iteration of the loop
                    raise NameError("LlamaNoise")
                else:
                    print("No Family Synonym Found")
                    resetadvancedoptions()

            # then search for the order
            orderalone = searchbyanything("%s" % (databaseta.iat[rownumber, 6]))
            if orderalone == 1:
                # if returns 1 then it means a match has been found
                print("Order Found")
                # check the SIS taxonomy reporting any differences you might find
                taxonomyhierarchychecker(rownumber)
                # raise exception to get out of this iteration of the loop
                raise NameError("LlamaNoise")
            # if not found then run a synonym check
            else:
                orderalonesyn = synonymchecker("%s" % (databaseta.iat[rownumber, 6]))
                if orderalonesyn == 1:
                    print("Order Synonym Found")
                    taxonomyhierarchychecker(rownumber)
                    resetadvancedoptions()
                    # raise exception to get out of this iteration of the loop
                    raise NameError("LlamaNoise")
                else:
                    print("No Order Synonym Found")
                    resetadvancedoptions()

            # then search for the class
            classalone = searchbyanything("%s" % (databaseta.iat[rownumber, 4]))
            if classalone == 1:
                # if returns 1 then it means a match has been found
                print("Class Found")
                # check the SIS taxonomy reporting any differences you might find
                taxonomyhierarchychecker(rownumber)
                # raise exception to get out of this iteration of the loop
                raise NameError("LlamaNoise")
            # if not found then run a synonym check
            else:
                classalonesyn = synonymchecker("%s" % (databaseta.iat[rownumber, 4]))
                if classalonesyn == 1:
                    print("Class Synonym Found")
                    taxonomyhierarchychecker(rownumber)
                    resetadvancedoptions()
                    # raise exception to get out of this iteration of the loop
                    raise NameError("LlamaNoise")
                else:
                    print("No Class Synonym Found")
                    resetadvancedoptions()

            # then search for the phylum
            phylumalone = searchbyanything("%s" % (databaseta.iat[rownumber, 2]))
            if phylumalone == 1:
                # if returns 1 then it means a match has been found
                print("Phylum Found")
                # check the SIS taxonomy reporting any differences you might find
                taxonomyhierarchychecker(rownumber)
                # raise exception to get out of this iteration of the loop
                raise NameError("LlamaNoise")
            # if not found then run a synonym check
            else:
                phylumalonesyn = synonymchecker("%s" % (databaseta.iat[rownumber, 2]))
                if phylumalonesyn == 1:
                    print("Phylum Synonym Found")
                    taxonomyhierarchychecker(rownumber)
                    resetadvancedoptions()
                    # raise exception to get out of this iteration of the loop
                    raise NameError("LlamaNoise")
                else:
                    print("No Phylum Synonym Found")
                    resetadvancedoptions()

            # then search for the kingdom
            kingdomalone = searchbyanything("%s" % (databaseta.iat[rownumber, 0]))
            if kingdomalone == 1:
                # if returns 1 then it means a match has been found
                print("Kingdom Found")
                # check the SIS taxonomy reporting any differences you might find
                taxonomyhierarchychecker(rownumber)
                # raise exception to get out of this iteration of the loop
                raise NameError("LlamaNoise")
            # if not found then run a synonym check
            else:
                kingdomalonesyn = synonymchecker("%s" % (databaseta.iat[rownumber, 0]))
                if kingdomalonesyn == 1:
                    print("Kingdom Synonym Found")
                    taxonomyhierarchychecker(rownumber)
                    resetadvancedoptions()
                    # raise exception to get out of this iteration of the loop
                    raise NameError("LlamaNoise")
                else:
                    print("No Kingdom Synonym Found")
                    resetadvancedoptions()
        except:
            pass

    # update the screen and close the preprocess window
    taxupdate(0)
    preprocesswindow.destroy()

# algorithm when on a taxon page to open and compare against SIS taxonomy
def taxonomyhierarchychecker(rownumber):
    global databaseta

    time.sleep(1)
    SISList = ["SISKingdomSV", "SISPhylumSV", "SISClassSV", "SISOrderSV", "SISFamilySV", "SISGenusSV", "SISSpeciesSV"]

    # grab and store taxonomy
    taxid = int(gettaxonID())

    # open up the hierarchy and test against the provided taxonomy
    driver.find_element_by_xpath("//*[contains(text(), 'View Hierarchy')]").click()

    # scrape the taxonomy from this page
    fulltaxonomy = driver.find_elements_by_css_selector(".SIS_HyperlinkLookAlike.fontSize14")

    # compare the scraped taxonomy with the provided taxonomy
    for x, y in enumerate(fulltaxonomy):
        # first update the SIS hierarchy to a list for use
        if x == 6:
            speciesonly = y.text.split()[1]
            buttonchanger("%s" % SISList[x], speciesonly)
            if speciesonly == databaseta.iat[rownumber, x * 2]:
                databaseta.iat[rownumber, (x * 2) + 1] = "M"
                # mark the species check as good
            else:
                # mark the species check as bad
                databaseta.iat[rownumber, (x * 2) + 1] = speciesonly
        elif y.text == databaseta.iat[rownumber, x * 2]:
            buttonchanger("%s" % SISList[x], y.text)
            # mark the species check as good
            databaseta.iat[rownumber, (x * 2) + 1] = "M"
        else:
            buttonchanger("%s" % SISList[x], y.text)
            # mark the tax level check as bad
            databaseta.iat[rownumber, (x * 2) + 1] = y.text
    root.update()
    # record the taxon id to the id box at the end
    databaseta.iat[rownumber, 21] = taxid

    # record that the species has been preprocessed
    databaseta.iat[rownumber, 22] = 1

    # save the output to file
    taxsave()
    # clean up
    resetimage = driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel")
    driver.execute_script("arguments[0].click();", resetimage)


# GUI code
# setup root
root = Tk()
root.title("SIS Assistant")
root.resizable(width=TRUE, height=TRUE)

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

# top levels
top = Toplevel()
top.config(background="#DFE8F6")
top.withdraw()
dspchoice = Toplevel()
dspchoice.config(background="#DFE8F6")
dspchoice.withdraw()
synonymsource = Toplevel()
synonymsource.config(background="#DFE8F6")
synonymsource.withdraw()

# global variables
filenamera = StringVar()
filenameta = StringVar()
locationofmaps = StringVar()

usernamevariable = None
passwordvariable = None
validatebuttontext = StringVar()
validatebuttontext.set("Validate")
reviewmenuplacetracker = IntVar()
reviewmenuplacetracker.set(0)
assessmentvar = StringVar()
synonomyvar = StringVar()
levelnameSV = StringVar()
taxauthSV = StringVar()
taxrefSV = StringVar()
workingsetSV = StringVar()
TaxCurrentSpeciesDict = {}
listofoptions = []
linklist = []
combobox = None
globallevel = IntVar()
synonymtoadd = StringVar()
synonymchosen = StringVar()
mapengineactive = IntVar()
mapengineactive.set(0)
mapenginetext = StringVar()
mapenginetext.set("Activate Maps")

# setup style
style = ttk.Style()
style.configure("TFrame", background="#DFE8F6")
csv.register_dialect('llama', lineterminator='\n')

# frame setup
# mainframe
mainframe = ttk.Frame(root, padding="0 0 0 0")
Grid.rowconfigure(root, 0, weight=1)
Grid.columnconfigure(root, 0, weight=1)
mainframe.grid(column=0, row=0, sticky=N+S+E+W)
mainframe.master.minsize(width=510, height=510)

# Simpleseachframe (aka the review assistant).
simplesearchframe = ttk.Frame(root, padding="0 0 0 0")
simplesearchframe.grid(column=0, row=0, sticky=N+S+E+W)
simplesearchframe.master.minsize(width=510, height=510)

# tableframe
tableframe = ttk.Frame(root, padding="0 0 0 0")
tableframe.grid(column=0, row=0, sticky=N+S+E+W)
tableframe.master.minsize(width=510, height=510)

# taxadderframe
taxadderframe = ttk.Frame(root, padding="0 0 0 0")
taxadderframe.grid(column=0, row=0, sticky=N+S+E+W)
taxadderframe.master.minsize(width=510, height=510)

# taxadderassistantframe
taxadderassistantframe = ttk.Frame(root, padding="0 0 0 0")
taxadderassistantframe.grid(column=0, row=0, sticky=N+S+E+W)
taxadderassistantframe.master.minsize(width=510, height=510)

# main frame
# main frame images
sislogo = PhotoImage(file="%s\\Images\\sislogo.png" % filedir)
topbar = PhotoImage(file="%s\\Images\\topbar.png" % filedir)

ttk.Label(mainframe, image=sislogo, borderwidth=0).grid(column=0, row=2, sticky=NW)
ttk.Label(mainframe, image=topbar, borderwidth=0).grid(column=0, row=1, columnspan=7)

# main frame labels
ttk.Label(mainframe, text="SISA v5.0", font=(None, 10), background="#DFE8F6").grid(column=6, row=2, sticky=NE)
ttk.Label(mainframe, text="Main Menu", font=(None, 15), background="#DFE8F6").grid(column=0, row=3, columnspan=8)
ttk.Label(mainframe, text="Taxon ID, or Binomial", font=(None, 10), background="#DFE8F6").grid(column=0, row=5, sticky=(S, W, E))

# mainframe string variables
anyvariable = StringVar()
species_ID = StringVar()

# mainframe buttons
loginbutton = ttk.Button(mainframe, text="Log In", command=lambda: login())
loginbutton.grid(column=0, row=4, sticky=(N, S, W))
species_name_entry = ttk.Entry(mainframe, width=20, textvariable=anyvariable, state=DISABLED)
species_name_entry.grid(column=0, row=6, sticky=(N, S, W, E), columnspan=1)
searchbyanythingbutton = ttk.Button(mainframe, text="Search", command=lambda: searchbyanything(anyvariable.get()), state=DISABLED)
searchbyanythingbutton.grid(column=0, row=7, sticky=(N, S, W, E))
singlereviewbutton = ttk.Button(mainframe, text="Review This Species", command=lambda: singlereview(), state=DISABLED)
singlereviewbutton.grid(column=1, row=7, sticky=(N, S, W, E))
simplesearchbutton = ttk.Button(mainframe, text="Review Assistant", command=simplesearchframe.tkraise, state=DISABLED)
simplesearchbutton.grid(column=0, row=8, sticky=(N, S, W, E))
taxadderframebutton = ttk.Button(mainframe, text="Taxonomy Assistant", command=taxadderassistantframe.tkraise, state=DISABLED)
taxadderframebutton.grid(column=0, row=9, sticky=(N, S, W, E))
logoutbutton = ttk.Button(mainframe, text="Log Out", command=lambda: logout(), state=DISABLED)
logoutbutton.grid(column=0, row=11, sticky=(N, S, W))

ttk.Button(mainframe, text="Quit", command=quit).grid(column=0, row=12, sticky=(N, S, W))

mainframe.columnconfigure((0, 1, 2), weight=1)
mainframe.rowconfigure((3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

# Taxonmyadderassistant frame (i.e. the menu for it)
# labels
ttk.Label(taxadderassistantframe, image=topbar, borderwidth=0).grid(column=0, row=0, sticky=EW)
ttk.Label(taxadderassistantframe, image=sislogo, borderwidth=0).grid(column=0, row=1, sticky=NW)
ttk.Label(taxadderassistantframe, text="Taxonomy Assistant Menu", font=(None, 15), background="#DFE8F6").grid(column=0, row=2, sticky=EW)

#buttons
taacontinue = ttk.Button(taxadderassistantframe, text="Continue session", command=lambda: gototaxspecial())
taacontinue.grid(column=0, row=3, sticky=N)
taanewdata = ttk.Button(taxadderassistantframe, text="Load New Data", command=lambda: loaddataandreadytaxassistant())
taanewdata.grid(column=0, row=4, sticky=N)
taagenerate = ttk.Button(taxadderassistantframe, text="Generate Template", command=lambda: generatetadaddertemplate())
taagenerate.grid(column=0, row=5, sticky=N)

taareturntomain = ttk.Button(taxadderassistantframe, text="Return to main menu", command=mainframe.tkraise)
taareturntomain.grid(column=0, row=10, sticky=SW, columnspan=3)

# give weight to rows and columns
taxadderassistantframe.columnconfigure((0, 1, 2), weight=1)
taxadderassistantframe.rowconfigure((2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)

# Taxonomy adder frame
# Taxonomy adder variables
CombinationStringVar = StringVar()
CombinationStringVar.set("Blank Blank")
taxonomyrowtrackerIntVar = IntVar()
taxonomyrowtrackerIntVar.set(0)
taxonomicprogresstracker = StringVar()
taxonomicprogresstracker.set("Blank of Blank")
copiedtexVar = StringVar()
copiedtexVar.set("Copy")
skiptoentrySV = IntVar()
skiptoentrySV.set(1)

# taxadder frame labels
ttk.Label(taxadderframe, image=topbar, borderwidth=0).grid(column=0, row=0, sticky=EW, columnspan=8)
ttk.Label(taxadderframe, image=sislogo, borderwidth=0).grid(column=0, row=1, sticky=NW, columnspan=3)

ttk.Label(taxadderframe, textvariable=CombinationStringVar, borderwidth=0, background="#DFE8F6", font=(None, 12), wraplength=150, justify=CENTER).grid(column=1, row=1, columnspan=2)
ttk.Button(taxadderframe, textvariable=copiedtexVar, command=lambda: copyname()).grid(column=3, row=1, sticky=S)
ttk.Button(taxadderframe, text="Recheck", command=lambda: taxupdate(0)).grid(column=3, row=2)
ttk.Label(taxadderframe, textvariable=taxonomicprogresstracker, borderwidth=0, background="#DFE8F6", font=(None, 8)).grid(column=3, row=1, sticky=N)
ttk.Label(taxadderframe, text="SIS Backbone", borderwidth=0, background="#DFE8F6").grid(column=0, row=2, sticky=NW)
ttk.Label(taxadderframe, text="Provided Data", borderwidth=0, background="#DFE8F6").grid(column=2, row=2, sticky=NW)
#taxlabel1 = ttk.Label(taxadderframe, font=(None, 10), background="#DFE8F6", textvariable=CombinationStringVar, wraplength=150, justify=CENTER)
#taxlabel1.grid(column=2, row=1, sticky=EW, columnspan=2)

# arrows in between labels
SolidDown = PhotoImage(file='%s\\images\\SolidDown.png' % filedir)
DownPossible = PhotoImage(file='%s\\images\\DownPossible.png' % filedir)
DownNo = PhotoImage(file='%s\\images\\DownNo.png' % filedir)
Blank = PhotoImage(file='%s\\images\\Blank.png' % filedir)
righttoleft = PhotoImage(file='%s\\images\\righttoleft.png' % filedir)
righttoleftpotential = PhotoImage(file='%s\\images\\righttoleftpotential.png' % filedir)
leftoright = PhotoImage(file='%s\\images\\leftoright.png' % filedir)
leftorightpotential = PhotoImage(file='%s\\images\\leftorightpotential.png' % filedir)

# first column for SIS data
# SIS arrows
SISKParrow = ttk.Label(taxadderframe, image=SolidDown, borderwidth=0, background="#DFE8F6")
SISPCarrow = ttk.Label(taxadderframe, image=SolidDown, borderwidth=0, background="#DFE8F6")
SISCOarrow = ttk.Label(taxadderframe, image=SolidDown, borderwidth=0, background="#DFE8F6")
SISOFarrow = ttk.Label(taxadderframe, image=SolidDown, borderwidth=0, background="#DFE8F6")
SISFGarrow = ttk.Label(taxadderframe, image=SolidDown, borderwidth=0, background="#DFE8F6")
SISGSarrow = ttk.Label(taxadderframe, image=SolidDown, borderwidth=0, background="#DFE8F6")

SISKParrow.grid(column=0, row=5)
SISPCarrow.grid(column=0, row=7)
SISCOarrow.grid(column=0, row=9)
SISOFarrow.grid(column=0, row=11)
SISFGarrow.grid(column=0, row=13)
SISGSarrow.grid(column=0, row=15)

SISKingdomSV = StringVar()
SISKingdomSV.set("SISKingdom")
SISPhylumSV = StringVar()
SISPhylumSV.set("SISPhylum")
SISClassSV = StringVar()
SISClassSV.set("SISClass")
SISOrderSV = StringVar()
SISOrderSV.set("SISOrder")
SISFamilySV = StringVar()
SISFamilySV.set("SISFamily")
SISGenusSV = StringVar()
SISGenusSV.set("SISGenus")
SISSpeciesSV = StringVar()
SISSpeciesSV.set("SISSpecies")
#userInfrarankSV = StringVar()
#userInfrarankSV.set("Infrarank")

# labels
taxlabel18 = ttk.Label(taxadderframe, textvariable=SISKingdomSV, background="#DFE8F6")
taxlabel19 = ttk.Label(taxadderframe, textvariable=SISPhylumSV, background="#DFE8F6")
taxlabel20 = ttk.Label(taxadderframe, textvariable=SISClassSV, background="#DFE8F6")
taxlabel21 = ttk.Label(taxadderframe, textvariable=SISOrderSV, background="#DFE8F6")
taxlabel22 = ttk.Label(taxadderframe, textvariable=SISFamilySV, background="#DFE8F6")
taxlabel23 = ttk.Label(taxadderframe, textvariable=SISGenusSV, background="#DFE8F6")
taxlabel24 = ttk.Label(taxadderframe, textvariable=SISSpeciesSV, background="#DFE8F6")
#taxlabel25 = ttk.Label(taxadderframe, textvariable=userInfrarankSV, background="#DFE8F6")

taxlabel18.grid(column=0, row=4)
taxlabel19.grid(column=0, row=6)
taxlabel20.grid(column=0, row=8)
taxlabel21.grid(column=0, row=10)
taxlabel22.grid(column=0, row=12)
taxlabel23.grid(column=0, row=14)
taxlabel24.grid(column=0, row=16)
#taxlabel25.grid(column=1, row=18)

# second column for the between column arrows
KPcrossarrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")
PCcrossarrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")
COcrossarrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")
OFcrossarrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")
FGcrossarrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")
GScrossarrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")

KPcrossarrow.grid(column=1, row=5, sticky=W)
PCcrossarrow.grid(column=1, row=7, sticky=W)
COcrossarrow.grid(column=1, row=9, sticky=W)
OFcrossarrow.grid(column=1, row=11, sticky=W)
FGcrossarrow.grid(column=1, row=13, sticky=W)
GScrossarrow.grid(column=1, row=15, sticky=W)
#SIarrow.grid(column=1, row=17)

# third column user data which is the base tree arrows between levels
# variables
userKingdomSV = StringVar()
userKingdomSV.set("Kingdom (K)")
userPhylumSV = StringVar()
userPhylumSV.set("Phylum (P)")
userClassSV = StringVar()
userClassSV.set("Class (C)")
userOrderSV = StringVar()
userOrderSV.set("Order (O)")
userFamilySV = StringVar()
userFamilySV.set("Family (F)")
userGenusSV = StringVar()
userGenusSV.set("Genus (G)")
userSpeciesSV = StringVar()
userSpeciesSV.set("Species (S)")
#userInfrarankSV = StringVar()
#userInfrarankSV.set("Infrarank")

# labels
taxlabel10 = ttk.Label(taxadderframe, textvariable=userKingdomSV, background="#DFE8F6")
taxlabel11 = ttk.Label(taxadderframe, textvariable=userPhylumSV, background="#DFE8F6")
taxlabel12 = ttk.Label(taxadderframe, textvariable=userClassSV, background="#DFE8F6")
taxlabel13 = ttk.Label(taxadderframe, textvariable=userOrderSV, background="#DFE8F6")
taxlabel14 = ttk.Label(taxadderframe, textvariable=userFamilySV, background="#DFE8F6")
taxlabel15 = ttk.Label(taxadderframe, textvariable=userGenusSV, background="#DFE8F6")
taxlabel16 = ttk.Label(taxadderframe, textvariable=userSpeciesSV, background="#DFE8F6")
#taxlabel17 = ttk.Label(taxadderframe, textvariable=userInfrarankSV, background="#DFE8F6")

taxlabel10.grid(column=2, row=4)
taxlabel11.grid(column=2, row=6)
taxlabel12.grid(column=2, row=8)
taxlabel13.grid(column=2, row=10)
taxlabel14.grid(column=2, row=12)
taxlabel15.grid(column=2, row=14)
taxlabel16.grid(column=2, row=16)
#taxlabel17.grid(column=1, row=18)

KParrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")
PCarrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")
COarrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")
OFarrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")
FGarrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")
GSarrow = ttk.Label(taxadderframe, image=Blank, borderwidth=0, background="#DFE8F6")

KParrow.grid(column=2, row=5)
PCarrow.grid(column=2, row=7)
COarrow.grid(column=2, row=9)
OFarrow.grid(column=2, row=11)
FGarrow.grid(column=2, row=13)
GSarrow.grid(column=2, row=15)
#SIarrow.grid(column=1, row=17)

# forth column for the add buttons
# string varoables for the details buttons
kingdomdetailstext = StringVar()
kingdomdetailstext.set('Details')
phylumdetailstext = StringVar()
phylumdetailstext.set('Details')
classdetailstext = StringVar()
classdetailstext.set('Details')
orderdetailstext = StringVar()
orderdetailstext.set('Details')
familydetailstext = StringVar()
familydetailstext.set('Details')
genusdetailstext = StringVar()
genusdetailstext.set('Details')
speciesdetailstext = StringVar()
speciesdetailstext.set('Details')

kingdomdetails = ttk.Button(taxadderframe, textvariable=kingdomdetailstext, command=lambda: detailbox("kingdom",kingdomdetailstext, 0))
phylumdetails = ttk.Button(taxadderframe, textvariable=phylumdetailstext, command=lambda: detailbox("phylum", phylumdetailstext, 2))
classdetails = ttk.Button(taxadderframe, textvariable=classdetailstext, command=lambda: detailbox("class", classdetailstext, 4))
orderdetails = ttk.Button(taxadderframe, textvariable=orderdetailstext, command=lambda: detailbox("order", orderdetailstext, 6))
familydetails = ttk.Button(taxadderframe, textvariable=familydetailstext, command=lambda: detailbox("family", familydetailstext, 8))
genusdetails = ttk.Button(taxadderframe, textvariable=genusdetailstext, command=lambda: detailbox("genus", genusdetailstext, 10))
speciesdetails = ttk.Button(taxadderframe, textvariable=speciesdetailstext, command=lambda: detailbox("species", speciesdetailstext, 12))

kingdomdetails.grid(column=3, row=4)
phylumdetails.grid(column=3, row=6)
classdetails.grid(column=3, row=8)
orderdetails.grid(column=3, row=10)
familydetails.grid(column=3, row=12)
genusdetails.grid(column=3, row=14)
speciesdetails.grid(column=3, row=16)

kingdomdetails.grid_forget()
phylumdetails.grid_forget()
classdetails.grid_forget()
orderdetails.grid_forget()
familydetails.grid_forget()
genusdetails.grid_forget()
speciesdetails.grid_forget()

# taxadder frame buttons
addtoworkingsetbutton = ttk.Button(taxadderframe, text="Add to Working Set?", command=lambda: addtoworkingset())
nextspeciestax = ttk.Button(taxadderframe, text=">", command=lambda: taxupdate(1))
previousspeciestax = ttk.Button(taxadderframe, text="<", command=lambda: taxupdate(-1))
taxreturntomain = ttk.Button(taxadderframe, text="Return to main menu", command=lambda: taxreturntomainspecial())
skiptoentry = ttk.Entry(taxadderframe, textvariable=skiptoentrySV, width=10)
skiptobuttontax = ttk.Button(taxadderframe, text="Skip to...", command=lambda: taxskipto())

addtoworkingsetbutton.grid(column=2, row=12, columnspan=3)
addtoworkingsetbutton.grid_forget()
previousspeciestax.grid(column=1, row=18, sticky=E, columnspan=2)
nextspeciestax.grid(column=3, row=18)
skiptoentry.grid(column=1, row=19, sticky=E, columnspan=2)
skiptobuttontax.grid(column=3, row=19)
taxreturntomain.grid(column=0, row=19, sticky=SW, columnspan=3)

# give weight to rows and columns
#taxadderframe.columnconfigure((0, 1, 2), weight=1)
taxadderframe.rowconfigure((2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18), weight=1)

# simplesearchframe (aka the review assistant)
# Simpleseachframe (aka the review assistant) images
ttk.Label(simplesearchframe, image=topbar, borderwidth=0).grid(column=0, row=0, sticky=EW, columnspan=8)
ttk.Label(simplesearchframe, image=sislogo, borderwidth=0).grid(column=0, row=1, sticky=NW, columnspan=2)

# Simpleseachframe (aka the review assistant) string variables
tablerownumber = IntVar()
nextspecies = StringVar()
previousspecies = StringVar()
currentspeciesname = StringVar()
skipto = IntVar()
candc = StringVar()
databaselength = StringVar()

tablerownumber.set(1)

# Simpleseachframe (aka the review assistant) labels
textlabel1 = ttk.Label(simplesearchframe, text="Current Species", font=(None, 10), background="#DFE8F6")
textlabel1.grid(column=1, row=1, sticky=N)
textlabel2 = ttk.Label(simplesearchframe, text="Previous Species", font=(None, 8), background="#DFE8F6")
textlabel2.grid(column=0, row=9)
textlabel3 = ttk.Label(simplesearchframe, text="Next Species", font=(None, 8), background="#DFE8F6")
textlabel3.grid(column=2, row=9)
previouspeciesvariable = ttk.Label(simplesearchframe, textvariable=previousspecies, font=(None, 8), background="#DFE8F6", wraplength=150)
previouspeciesvariable.grid(column=0, row=10)
currentspeciesnamelabel = ttk.Label(simplesearchframe, textvariable=currentspeciesname, font=(None, 10), background="#DFE8F6", wraplength=150, justify=CENTER)
currentspeciesnamelabel.grid(column=1, row=1)
candclabel = ttk.Label(simplesearchframe, textvariable=candc, font=(None, 10), background="#DFE8F6")
candclabel.grid(column=1, row=2)
nextspecieslabel= ttk.Label(simplesearchframe, textvariable=nextspecies, font=(None, 8), background="#DFE8F6", wraplength=150)
nextspecieslabel.grid(column=2, row=10)
textlabel4 = ttk.Label(simplesearchframe, text="Verification Checks?", font=(None, 8), background="#DFE8F6")
textlabel4.grid(column=0, row=4, sticky=E)
textlabel5 = ttk.Label(simplesearchframe, text="Criteria Checked?", font=(None, 8), background="#DFE8F6")
textlabel5.grid(column=0, row=5, sticky=E)
textlabel6 = ttk.Label(simplesearchframe, text="Maps Checked?", font=(None, 8), background="#DFE8F6")
textlabel6.grid(column=0, row=6, sticky=E)
textlabel7 = ttk.Label(simplesearchframe, text="Skip to ...", font=(None, 8), background="#DFE8F6")
textlabel7.grid(column=1, row=9)
entryvariable1 = ttk.Entry(simplesearchframe, width=20, textvariable=skipto, state=NORMAL)
entryvariable1.grid(column=1, row=10)
skiptobutton = ttk.Button(simplesearchframe, text="Skip to...", command=lambda: skiptofunction())
skiptobutton.grid(column=1, row=11)
assessmentnumber = ttk.Label(simplesearchframe, textvariable=databaselength, font=(None, 8), background="#DFE8F6")
assessmentnumber.grid(column=1, row=1)
reviewtoolsbutton = ttk.Button(simplesearchframe, text="Open Review Tools", command=lambda: createtoolwindow())
reviewtoolsbutton.grid(column=1, row=12)
hidetoolsbutton = ttk.Button(simplesearchframe, text="Hide Review Tools", command=lambda: hidetoolwindow())
hidetoolsbutton.grid(column=0, row=12)
reviewassistantmenu = ttk.Label(simplesearchframe, text="Review Assistant Menu", font=(None, 14), background="#DFE8F6")
reviewassistantmenu.grid(column=0, row=2, sticky=N, columnspan=3)

#notes box
notesbox = ScrolledText(simplesearchframe, height=5, width=47)
notesbox.grid(row=7, column=0, columnspan=5, rowspan=2, sticky=NSEW)

# check boxes
verified = StringVar()
verified.set("Not Passed")
criteria = StringVar()
criteria.set("Not Passed")
maps = StringVar()
maps.set("Not Passed")
verifiedcheck = ttk.Button(simplesearchframe, textvariable=verified, command=lambda: swapstate(verified, verifiedcheck))
criteriacheck = ttk.Button(simplesearchframe, textvariable=criteria, command=lambda: swapstate(criteria, criteriacheck))
mapscheck = ttk.Button(simplesearchframe, textvariable=maps, command=lambda: swapstate(maps, mapscheck))
criteriacheck.grid(column=1, row=4, sticky=E)
verifiedcheck.grid(column=1, row=5, sticky=E)
mapscheck.grid(column=1, row=6, sticky=E)

# simplesearchframe (aka the review assistant) buttons
continuewhereyouleft = ttk.Button(simplesearchframe, text="Continue Reviewing", command=lambda: (unhidereviewassistant()))
generatetemplatebutton = ttk.Button(simplesearchframe, text="Generate Template", command=lambda: generatetemplate())
populatebutton = ttk.Button(simplesearchframe, text="Load New Data From Excel", command=lambda: (loaddataandreadyreviewassistant()))

continuewhereyouleft.grid(column=0, row=3, sticky=N, rowspan=3)
populatebutton.grid(column=0, row=4, sticky=N, rowspan=3)
generatetemplatebutton.grid(column=0, row=5, sticky=N, rowspan=3)
returntomainmenu = ttk.Button(simplesearchframe, text="Return to main menu", command=lambda: specialreturntomain())
returntomainmenu.grid(column=0, row=12, sticky=SW)

goback = ttk.Button(simplesearchframe, text="<", command=lambda: update(-1))
goforward = ttk.Button(simplesearchframe, text=">", command=lambda: update(1))
goback.grid(column=1, row=6, sticky=E)
goforward.grid(column=1, row=6, sticky=E)

# simpleseachframe giving weight to the columns and rows
simplesearchframe.columnconfigure((0, 1, 2), weight=1)
simplesearchframe.rowconfigure((3, 4, 5, 6, 7, 8, 9, 10), weight=1)


# final buffer tidy up
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

for child in simplesearchframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

for child in taxadderframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

for child in taxadderassistantframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# hide the various menus to allow things to appear neatly.
hideall()

# problematic libaries loading these last as this seems to fix the pyimage not existing error
import pandas
import folium
import geopandas
import fiona

# panda databases have to be loaded after pandas for the above workaround to work
databasera = pandas.DataFrame(index=range(0, 4), columns=['Genus', 'Species', 'Criteria Passed?', 'Validity Passed?', 'Map Passed?', 'Notes']).astype('str')
databaseta = pandas.DataFrame(index=range(0, 4), columns=['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Taxonomic Reference', 'Working Set']).astype('str')
fastreviewdirections = pandas.DataFrame()

# mainloop and raise mainframe to top for start
mainframe.tkraise()
root.mainloop()
