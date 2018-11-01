# version 5.43

# import the libaries needed
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from collections import OrderedDict
from operator import itemgetter

import csv
import os
import time
import subprocess
from subprocess import call
import pip
import collections
import shutil
import copy
import json

import dropbox

import datetime
import webbrowser
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter.scrolledtext import ScrolledText

# problematic libaries loading these last as this seems to fix the pyimage not existing error
import pandas
import folium
import geopandas
from geopandas import GeoDataFrame
from shapely.geometry import Point
import shapely
from shapely import speedups
speedups.enable()
import fiona

# get the directory from which the python file is running
filedir = os.path.dirname(__file__)

print(filedir)

# function declarations
# setup the webdriver
options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : '{}'.format(os.path.expanduser("~\Desktop\AttachmentDownload"))}
options.add_experimental_option('prefs', prefs)
options.add_argument('--lang=en-GB')
options.add_argument('--disable-infobars')

driver = webdriver.Chrome(executable_path='%s\ChromeDriver\chromedriver.exe' % filedir, options=options)

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

        # deactivate the login button, and renable the other buttons
        loginbutton.configure(state=DISABLED)
        searchbyanythingbutton.configure(state=NORMAL)
        species_name_entry.configure(state=NORMAL)
        logoutbutton.configure(state=NORMAL)
        taxadderframebutton.configure(state=NORMAL)
        singlereviewbutton.configure(state=DISABLED)
        simplesearchbutton.configure(state=NORMAL)
        spatialdatatoolspagebutton.configure(state=NORMAL)

    except NoSuchElementException:
        messagebox.showerror("An Error Has Occurred", "Password or Username incorrect, please try again")
        pass

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
    spatialdatatoolspagebutton.configure(state=DISABLED)

# function to search for a species using ID
def searchbyanything(value):
    # if coming from the homepage then try to wipe the storage variable
    anyvariable.set("")

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
            for number, q in enumerate(potentiallist):
                # compare text with value searched (case sensitive) if found click, else pass
                if q.text == value:
                    while True:
                        try:
                            q.click()
                            return 1
                        except:
                            try:
                                potentiallist[number+1].click()
                            except:
                                pass
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
            check = driver.find_element_by_xpath("//*[contains(text(), '%s')]" % value)
            checktext = check.text
            if checktext == value:
                check.click()
            else:
                raise WebDriverException

        except WebDriverException:
            for x in range(2, 1000):
                try:
                    check2 = driver.find_element_by_xpath("(//*[contains(text(), '%s')])[position()='%d']" % (value, x))
                    checktext2 = check2.text
                    if checktext2 == value:
                        check2.click()
                        break

                except NoSuchElementException:
                    messagebox.showerror("An Error Has Occurred", "Unable to find species, please try again")
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
        messagebox.showerror("An Error Has Occurred", "Unable to reset to homepage, try again")
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
        messagebox.showerror("An Error Has Occurred", "Unable to get data from database, try again")
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

# function to save the map to a shapefile
def savemaptofile(locationtosave, speciesname):
    # get the schema from the file
    schema = geopandas.io.file.infer_schema(spatialdata)

    # check to see if freshwaterSV is yes then convert the hybas field to bigger int
    if freshwaterSV.get() == str(1):
        # check to see if it has hydrobasins in it, if it does then change that to be an int:64 and save
        # schema = {'geometry': 'Polygon', 'properties': OrderedDict([('HYBAS_ID', 'int:64'), ('BINOMIAL', 'str'), ('PRESENCE', 'int'), ('ORIGIN', 'int'), ('SEASONAL', 'int'), ('COMPILER', 'str'), ('YEAR', 'int'), ('CITATION', 'str'), ('SOURCE', 'str'), ('LEGEND', 'str')])}
        for x in schema["properties"]:
            if x == "HYBAS_ID" or x == "BASIN_ID":
                schema["properties"][x] = 'int:64'

    # save to file
    spatialdata.to_file(locationtosave, driver='ESRI Shapefile', layer=speciesname, schema=schema)
    return 0

# function to export the selected working set to excel
def exportworkingsettoexcel(rowinfo):
    # get the row selected from the user
    workingsetnameSV.set(rowinfo['text'])
    workingsetlocation = "%s\\WorkingSetStore\\%s.pkl" % (filedir, rowinfo['text'])

    # read the file from file
    databasera = pandas.read_pickle(workingsetlocation)

    # get save location from user
    locationtosaveto = filedialog.asksaveasfilename(initialdir="/", title="Select save location", filetypes=(("Excel Spreadsheet","*.xlsx"), ("all files", "*.*")))
    # create writer object and export to the specified location
    writer = pandas.ExcelWriter("%s.xlsx" % locationtosaveto, engine='xlsxwriter')
    databasera.to_excel(writer, sheet_name='Sheet 1')
    writer.save()

    # report success
    messagebox.showinfo(title="Export Successful" , message="Exported to %s" % locationtosaveto)
    return 0

# function to import SIS report and convert into internal database
def importsisrawandconvert():
    global linktable
    forbiddencharacters = r'/\?%*:|"<>. '

    # close the WS manager
    linkTL.destroy()

    try:
        filenamera.set(filedialog.askopenfilename())
        if filenamera.get() == "":
            openworkingsetmanager()
            return 1
        workingsetnameSV.set(simpledialog.askstring("What is the working set called", "Please provide working set name", parent=mainframe))
        if any(elem in workingsetnameSV.get() for elem in forbiddencharacters):
            raise Exception
    except:
        messagebox.showerror(title="Forbidden file name", message='Please don\'t use any of the following characters /\?%*:|"<>. in the file name')
        openworkingsetmanager()
        return 1

    if workingsetnameSV.get() == "None":
        messagebox.showerror(title="Failed to import", message="Please provide a name for the working set")
        return 1
    else:
        workingsetname = workingsetnameSV.get()
        
    # check the provided name against the linktable, if non unique ask user to provide a new one
    if workingsetname in linktable["WorkingSetName"].values:
        messagebox.showerror(title="Failed to import", message="Please provide a unqiue working set name, the one you have provided already exists")
        openworkingsetmanager()
        return 1

    print("Importing and converting SIS report to SISA format")
    # read in the CSV into a temporary dataframe
    tempdataframe = pandas.read_csv(filenamera.get(), header=None)
    # create the template for the database
    databasera = pandas.DataFrame(index=range(0, len(tempdataframe)), columns=['ID', 'Binomial', 'Threat Category', 'Criteria String', 'Criteria Passed?', 'Validity Passed?', 'Map Passed?', 'Notes', 'Assessment Passed?'])
    # iterate over the rows, check column 7, if it's an int then that's the ID (no subspecies) else use 8 as the ID
    for index, row in tempdataframe.iterrows():
        if str(row[7]).isdigit():
            # set the ID
            databasera.iat[index, 0] = int(tempdataframe.iat[index, 7])
            # set the binomial
            databasera.iat[index, 1] = tempdataframe.iat[index, 8]
            # set the Threat Category
            databasera.iat[index, 2] = tempdataframe.iat[index, 10]
            # set the criteria
            databasera.iat[index, 3] = tempdataframe.iat[index, 9]
        else:
            # set the ID
            databasera.iat[index, 0] = int(tempdataframe.iat[index, 8])
            # set the binomial
            databasera.iat[index, 1] = tempdataframe.iat[index, 9]
            # set the Threat Category
            databasera.iat[index, 2] = tempdataframe.iat[index, 11]
            # set the criteria
            databasera.iat[index, 3] = tempdataframe.iat[index, 10]

        # set the Criteria Passed Column
        databasera.iat[index, 4] = "Not Passed"
        # set the Validity Passed Column
        databasera.iat[index, 5] = "Not Passed"
        # set the Map Passed Column
        databasera.iat[index, 6] = "Not Passed"
        # set the Assessment Passed Column
        databasera.iat[index, 8] = '=NOT(OR(F%i="NOT PASSED",G%i="NOT PASSED",H%i="NOT PASSED"))' % (index + 2, index + 2, index + 2)
    # set the threat category column to a categorical series
    databasera.fillna("", axis=1, inplace=True)
    databasera['Threat Category'] = pandas.Categorical(databasera['Threat Category'], ["EX", "EW", "CR", "EN", "VU", "NT", "LC", "DD",""])
    databasera.sort_values('Threat Category', inplace=True, na_position='last', ascending=True, kind="mergesort")
    # save to workingset store in pickle format
    databasera.to_pickle(path="%s\\WorkingSetStore\\%s.pkl" % (filedir, workingsetname))
    # ask user if they have maps
    if messagebox.askyesno(title="Map Data Location", message="Do you have any maps for this working set"):
        maplocation = filedialog.askdirectory()
    else:
        maplocation = "FALSE"

    # create temporary dataframe to hold new data
    date = datetime.datetime.now()
    datestring = "%s-%s-%s" % (date.year, date.month, date.day)
    tempdf = pandas.Series([workingsetname, maplocation, datestring, 1], index=['WorkingSetName', 'MapLocation', 'Date', 'LeftAt'])

    # append to database
    linktable = linktable.append(tempdf, ignore_index=True)

    # save linktable
    linktable.to_pickle("%s\\WorkingSetStore\\WSMAPLinkTable.pkl" % filedir)

    # open the working set manager to allow them to select and load
    openworkingsetmanager()

# function to actually load the review information
def loadandreadyreviewinformation(rowinfo):
    global databasera
    global binomialnospaces

    workingsetnameSV.set(rowinfo['text'])
    workingsetlocation = "%s\\WorkingSetStore\\%s.pkl" % (filedir, rowinfo['text'])
    maplocation = rowinfo['values'][0]
    locationofmaps.set(maplocation)

    leftat = rowinfo['values'][2]

    try:
        # read the file from file
        databasera = pandas.read_pickle(workingsetlocation)

        # if map location == FALSE then this means the working set has no maps
        if maplocation != "FALSE":
            # test to see if map location is valid
            if not os.path.isdir(maplocation):
                messagebox.showerror("Unable to load", "Couldn't locate spatial data has it moved?")
                return 1

        # ask user if they want to carry on from where they left off?
        continuefromlastsession = messagebox.askyesno(title="Continue Review Sessions", message="Would you like to carry on from where you left last time?")

        # if yes then set to the value in the table minus 1 to get the row number
        if continuefromlastsession:
            tablerownumber.set(leftat - 1)
        # else set to 0 and continue as normal
        else:
            tablerownumber.set(0)

        # activate table button
        simplesearchbutton.configure(state=NORMAL)

        # undertake the special update function to setup the page ready for reviewing
        # get current value of the rowtracker
        rownumber = (tablerownumber.get())

        # Get the current species genus and name from the table and the species ID
        binomial = databasera.iat[rownumber, 1]
        try:
            binomialnospaces = binomial.replace(" ", "_")
        except:
            binomialnospaces = binomial

        speciesID = databasera.iat[rownumber, 0]

        # Get the correct Category and criteria from the table
        candcouput1 = databasera.iat[rownumber, 3]
        candcoutput2 = databasera.iat[rownumber, 4]

        # check to ensure that the database is still in the scope of the underlying database
        if rownumber - 1 < 0:
            previousspeciesbinomial = ""
            goback.config(state='disabled')
        else:
            previousspeciesbinomial = databasera.iat[rownumber - 1, 1]
            goback.config(state='normal')

        if rownumber + 1 >= len(databasera):
            nextspeciesbinomial = ""
            goforward.config(state='disabled')
        else:
            nextspeciesbinomial = databasera.iat[rownumber + 1, 1]
            goforward.config(state='normal')

        # then set the value of the external rowtracker to the new value
        currentspeciesname.set("%s" % binomial)
        previousspecies.set("%s" % previousspeciesbinomial)
        nextspecies.set("%s" % nextspeciesbinomial)
        candc.set("%s %s" % (candcouput1, candcoutput2))

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

        # finally go to page
        reviewassistantframe.tkraise()

        # destroy the working set manager
        linkTL.destroy()

    except:
        messagebox.showerror("Unable to load data from file", "Please contact the adminstrator")

# function to delete a working set
def deleteworkingset(tree):
    global linktable

    rowinfo = tree.item(tree.focus())

    # create an are you sure messagediaglogue
    if messagebox.askyesno(title="Confirm Delete", message="Are you sure you want to delete this file?") == "no":
        return 1

    # get the workingset name from the box
    workingsetnameSV.set(rowinfo['text'])
    workingsetlocation = "%s\\WorkingSetStore\\%s.pkl" % (filedir, rowinfo['text'])
    maplocation = rowinfo['values'][0]

    # delete the pkl file
    print("Deleting pickle file")
    os.remove(workingsetlocation)

    # remove the entry from WSMAPLinkTable
    workingsetname = workingsetnameSV.get()
    for row, value in enumerate(linktable['WorkingSetName']):
        if value == workingsetname and linktable['MapLocation'][row] == maplocation:
            linktable.drop(row, axis=0, inplace=True)

    # save the modified pickle to the folder
    linktable.to_pickle("%s\\WorkingSetStore\\WSMAPLinkTable.pkl" % filedir)

    # remove the row from the table and update the screen
    tree.delete(tree.focus())
    linkTL.update()
    linkTL.lift()

    # report success
    print("Working Set Successfully Deleted")

# function to allow the user to change the name of the working set
def changeworkingsetname(tree):
    global linktable
    global linkTL

    # get id of focused row
    ID = tree.focus()
    rownumber = (tablerownumber.get())
    rowinfo = tree.item(tree.focus())
    workingsetname = rowinfo['text']

    # get new name of working set from the user
    newwsname = simpledialog.askstring("Rename Working Set", "New Working set name: ", parent=linkTL)

    # get the index of the row with the name of the working set
    indexofrow = (linktable.index[linktable['WorkingSetName'] == workingsetname].tolist())

    # update the workingset name varaible for this working set in the Linktable
    linktable.iat[indexofrow[0], 0] = newwsname

    # save the linktable
    linktable.to_pickle("%s\\WorkingSetStore\\WSMAPLinkTable.pkl" % filedir)

    # rename the pickle file
    os.rename("%s\\WorkingSetStore\\%s.pkl" % (filedir, workingsetname), "%s\\WorkingSetStore\\%s.pkl" % (filedir, newwsname))

    # update the treeview to reflect these changes
    tree.item(ID, text=newwsname)
    linkTL.update()
    linkTL.lift()

# function to update the map location
def changemaplocation(tree):
    global linktable
    global linkTL

    # get id of focused row
    ID = tree.focus()

    # get the rownumber, current working set name and the new maplocation from the user
    rownumber = (tablerownumber.get())
    rowinfo = tree.item(tree.focus())
    workingsetname = rowinfo['text']
    newmaplocation = filedialog.askdirectory()

    # get the index of the row with the name of the working set
    indexofrow = (linktable.index[linktable['WorkingSetName'] == workingsetname].tolist())

    # update the maplocation variable for this working set in the Linktable
    linktable.iat[indexofrow[0], 1] = newmaplocation

    # save the linktable
    linktable.to_pickle("%s\\WorkingSetStore\\WSMAPLinkTable.pkl" % filedir)

    # update the treeview to reflect these changes
    tree.set(ID, 'Map Location', newmaplocation)
    linkTL.update()
    linkTL.lift()

# convert to lower case if possible,
def customsort(x):
    try:
        return x[0].lower()
    except AttributeError:
        return x[0]

# sort the tree view by the provided column
def sortlist(tree, columnname, reverse):
    # create a dictionary of all the ID's and first column text
    listofitems = []

    # if the root
    if columnname == "#0":
        for x in tree.get_children():
            listofitems.append([tree.item(x)["text"], x])

    elif columnname == "Map Location":
        for x in tree.get_children():
            listofitems.append([tree.item(x)["values"][0], x])

    elif columnname == "Created on":
        for x in tree.get_children():
            listofitems.append([tree.item(x)["values"][1], x])

    else:
        for x in tree.get_children():
            listofitems.append([tree.item(x)["values"][2], x])

    # sort list case insensitive
    listofitems.sort(key=customsort, reverse=reverse)

    # iterate over list using the item id to move it into the correct place (order of list)
    for index, value in enumerate(listofitems):
        tree.move(item=value[1], parent='', index=index)

    # modify the header for the column so that next time it will reverse
    if reverse:
        if columnname == "#0":
            tree.heading(columnname, text="Working Set Name ↓", command=lambda: sortlist(tree, columnname, False))
        else:
            tree.heading(columnname, text="%s ↓" % columnname, command=lambda: sortlist(tree, columnname, False))
    else:
        if columnname == "#0":
            tree.heading(columnname, text="Working Set Name ↑", command=lambda: sortlist(tree, columnname, True))
        else:
            tree.heading(columnname, text="%s ↑" % columnname, command=lambda: sortlist(tree, columnname, True))

    # update the page
    linkTL.update()

# load user selected review data and then ready the review assistant
def openworkingsetmanager():
    # prompt the user to open the csv they want to read from
    global databasera
    global fastreviewdirections
    global linkTL

    # create a top window to display the link table
    linkTL = Toplevel()
    linkTL.config(background="#DFE8F6")

    w = reviewassistantframe.winfo_width()
    h = reviewassistantframe.winfo_height()

    # place the top window
    linkTL.geometry('%dx%d+%d+%d' % (screen_width/2, h, screen_width/4, screen_height/2 - h/2))
    linkTL.resizable(0, 0)

    # Title
    ttk.Label(linkTL, text="Select Working Set To Continue Reviewing", background="#DFE8F6", font=(None, 15)).grid(column=0, row=0, sticky=W)

    # create the treeview table
    wsm = ttk.Treeview(linkTL)
    wsm['columns'] = ('Map Location', 'Created on', 'Left At #')
    wsm.heading("#0", text="Working Set Name", command=lambda: sortlist(wsm, "#0", False))
    wsm.column('#0', anchor="w")
    wsm.heading("Map Location", text="Map Location", command=lambda: sortlist(wsm, "Map Location", False))
    wsm.column('Map Location', anchor="center", width=200)
    wsm.heading("Created on", text="Created on", command=lambda: sortlist(wsm, "Created on", False))
    wsm.column('Created on', anchor="center", width=100)
    wsm.heading("Left At #", text="Left At #", command=lambda: sortlist(wsm, "Left At #", False))
    wsm.column('Left At #', anchor="center", width=50)

    # create buttons
    selectworkingset = ttk.Button(linkTL, text="Continue", command=lambda: loadandreadyreviewinformation(wsm.item(wsm.focus())))
    selectworkingset.grid(column=0, row=2, sticky=N)
    changemaplocationbutton = ttk.Button(linkTL, text="Update Map Location", command=lambda: changemaplocation(wsm))
    changemaplocationbutton.grid(column=0, row=2, sticky=NE)
    exporttoexcel = ttk.Button(linkTL, text="Export to Excel", command=lambda: exportworkingsettoexcel(wsm.item(wsm.focus())))
    exporttoexcel.grid(column=0,row=2, sticky=NW)
    importnewws = ttk.Button(linkTL, text="Import A New Working Set", command=lambda: importsisrawandconvert())
    importnewws.grid(column=0, row=3, sticky=NE)
    downloadallattachmentbutton = ttk.Button(linkTL, text="Download working set attachments", command=lambda: downloadallattachements(wsm.item(wsm.focus())))
    downloadallattachmentbutton.grid(column=0, row=3, sticky=NW)
    delete = ttk.Button(linkTL, text="Delete Working Set", command=lambda: deleteworkingset(wsm))
    delete.grid(column=0, row=4, sticky=SE)
    renameworkingsetbutton = ttk.Button(linkTL, text="Rename Working Set", command=lambda: changeworkingsetname(wsm))
    renameworkingsetbutton.grid(column=0, row=5, sticky=SE)
    quit = ttk.Button(linkTL, text="Quit", command=lambda: linkTL.destroy())
    quit.grid(column=0, row=5, sticky=SW)

    for index, row in linktable.iterrows():
        wsm.insert('', 'end', text=row['WorkingSetName'], values=(row['MapLocation'], row['Date'], row['LeftAt']))

    # add in scroll bar
    vsb = ttk.Scrollbar(linkTL, orient="vertical", command=wsm.yview)
    vsb.grid(row=1, column=0, sticky=('NSE'))
    wsm.configure(yscrollcommand=vsb.set)

    wsm.grid(column=0, row=1, sticky=EW)

    # give weight to the rows and column
    linkTL.columnconfigure(0, weight=1)
    linkTL.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

    # fill the remaing space.
    for child in linkTL.winfo_children():
        child.grid_configure(padx=5, pady=5)

    linkTL.update()

    linkTL.wait_window()

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

    # check if any preprocessing is required before anything
    if databaseta.iat[taxonomyrowtrackerIntVar.get(), 22] == 0:
        preprocess()
        taxsave()

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

# function to activate repopulate and return to the main menu
def specialreturntomain():
    global mainframe
    try:
        reviewsave()
    except:
        pass

    finally:
        # get the global rownumber and working set name
        rownumber = (tablerownumber.get())
        workingsetname = workingsetnameSV.get()
        # get the index of the row with the name of the working set
        indexofrow = (linktable.index[linktable['WorkingSetName'] == workingsetname].tolist())

        # update the left at varaible for this working set in the Linktable
        linktable.iat[indexofrow[0], 3] = rownumber + 1

        # save the linktable
        linktable.to_pickle("%s\\WorkingSetStore\\WSMAPLinkTable.pkl" % filedir)

        mainframe.tkraise()
        hidetoolwindow()
        # refresh the page by clicking the SIS logo
        driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel").click()

# this function saves the state of the species
def reviewsave():
    global databasera

    # get the global rownumber and working set name
    rownumber = (tablerownumber.get())
    workingsetname = workingsetnameSV.get()

    # write the current button values to the database
    databasera.iat[rownumber, 4] = criteria.get()
    databasera.iat[rownumber, 5] = verified.get()
    databasera.iat[rownumber, 6] = maps.get()

    # write the notes field to the database
    databasera.iat[rownumber, 7] = notesbox.get("1.0", "end-1c")

    # write the formula to the final column
    databasera.iat[rownumber, 8] = '=NOT(OR(G%i="NOT PASSED",H%i="NOT PASSED",I%i="NOT PASSED"))' % (rownumber + 2, rownumber + 2, rownumber + 2)

    # write database to the pkl file
    databasera.to_pickle(path="%s\\WorkingSetStore\\%s.pkl" % (filedir, workingsetname))

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
    criteria.set(databasera.iat[rownumber, 4])
    verified.set(databasera.iat[rownumber, 5])
    maps.set(databasera.iat[rownumber, 6])

    # get the correct notes from the database
    notesoutput = databasera.iat[rownumber, 7]

    # clear the notes box and then insert the next text
    notesbox.delete('1.0', END)
    notesbox.insert(INSERT, "%s" % notesoutput)

    try:
        dspchoice.destroy()
    except:
        pass

    # open the assessment chooser window
    assessmentlistchooser()

# advance/go back a row on the table
def update(advorgoback):
    global databasera
    global filedir
    global dspchoice
    global binomialnospaces


    # get the location of the maps from the global variable
    fp = locationofmaps.get()
    freshwater = freshwaterSV.get()
    temprownumber = tablerownumber.get()

    # if we know whether there should be hydrobasins or not then save
    if mapengineactive.get() == 1 and freshwater != "NoValue":
        savemaptofile(fp, "%s_%s" % (databasera.iat[temprownumber, 1], databasera.iat[temprownumber, 2]))

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
    binomial = databasera.iat[rownumber, 1]
    try:
        binomialnospaces = binomial.replace(" ", "_")
    except:
        binomialnospaces = binomial
    SpeciesID = databasera.iat[rownumber, 0]

    # Get the correct Category and criteria from the table
    candcouput1 = databasera.iat[rownumber, 2]
    candcoutput2 = databasera.iat[rownumber, 3]

    # check to ensure that the database is still in the scope of the underlying database
    if rownumber - 1 < 0:
        previousspeciesbinomial = ""
        goback.config(state='disabled')
    else:
        previousspeciesbinomial = databasera.iat[rownumber - 1, 1]
        goback.config(state='normal')

    if rownumber + 1 >= len(databasera):
        nextspeciesbinomial = ""
        goforward.config(state='disabled')
    else:
        nextspeciesbinomial = databasera.iat[rownumber + 1, 1]
        goforward.config(state='normal')

    # then set the value of the external rowtracker to the new value
    currentspeciesname.set("%s" % binomial)
    previousspecies.set("%s" % previousspeciesbinomial)
    nextspecies.set("%s" % nextspeciesbinomial)
    candc.set("%s %s" % (candcouput1, candcoutput2))

    # call the search function to look for that species ID
    species_ID.set(SpeciesID)
    tablesearch()

    # if the map viewer has been activated then create map else skip
    # Get the current species genus and name from the table
    if mapengineactive.get() == 1:
        freshwaterSV.set("NoValue")
        # first try to destroy the current windows (may not have appeared if no map for previous)
        try:
            maptestslevel.destroy()
        except:
            pass

        if (createmapfromscratch("%s" % binomialnospaces)) == 0:
            messagebox.showerror(title="Mysterious Rubber Duck", message="No map for this species could be found")
        else:
            # create the map
            webbrowser.open("%s\\SpatialDataStore\\%s.html" % (filedir, binomialnospaces))
            maptests("%s" % binomialnospaces)

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

    w = reviewassistantframe.winfo_width()
    h = reviewassistantframe.winfo_height()

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

    pre1 = ttk.Button(preprocesswindow, text="Preprocess 1", command=lambda: taxonomychecker(1))
    pre10 = ttk.Button(preprocesswindow, text="Preprocess 10", command=lambda: taxonomychecker(10))
    pre20 = ttk.Button(preprocesswindow, text="Preprocess 20", command=lambda: taxonomychecker(20))
    pre50 = ttk.Button(preprocesswindow, text="Preprocess 50", command=lambda: taxonomychecker(50))
    pre100 = ttk.Button(preprocesswindow, text="Preprocess 100", command=lambda: taxonomychecker(100))
    ttk.Button(preprocesswindow, text="Preprocess remaining (%i)" % numberleft, command=lambda: taxonomychecker(numberleft)).grid(column=0, row=8, sticky=EW)
    ttk.Button(preprocesswindow, text="Quit", command=lambda: preprocessreturn()).grid(column=1, row=9, sticky=EW)

    pre1.grid(column=0, row=3, sticky=EW)
    pre10.grid(column=0, row=4, sticky=EW)
    pre20.grid(column=0, row=5, sticky=EW)
    pre50.grid(column=0, row=6, sticky=EW)
    pre100.grid(column=0, row=7, sticky=EW)

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

    # get the number to skip to
    numbertoskipto = (skipto.get() - 1)
    skipto.set("")

    # check to make sure that you don't go out of bounds (i.e. can't go below 2 or above max length of list)
    if numbertoskipto < 0 or numbertoskipto > len(databasera):
        return 0

    # save the current data before making any changes
    reviewsave()

    # if valid then change the tracker for use in the function
    rownumber = numbertoskipto
    tablerownumber.set(numbertoskipto)

    # refresh the page by clicking the SIS logo
    driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel").click()

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
        goback.config(state='disabled')
    else:
        previousspeciesoutput = databasera.iat[rownumber - 1, 1]
        previousspeciesoutput2 = databasera.iat[rownumber - 1, 2]
        goback.config(state='normal')

    if rownumber + 1 >= len(databasera):
        nextspeciesoutput = ""
        nextspeciesoutput2 = ""
        goforward.config(state='disabled')
    else:
        nextspeciesoutput = databasera.iat[rownumber + 1, 1]
        nextspeciesoutput2 = databasera.iat[rownumber + 1, 2]
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
    w = reviewassistantframe.winfo_width()
    h = reviewassistantframe.winfo_height()

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

# Checks polygon shapefile against the required and standard attributes, returns a list of fields that are not in either first list = missing required, second = fields to remove
def checkpolygonfields():
    global mapchecks
    global spatialdata

    freshwater = freshwaterSV.get()

    # create container for the list of lists.
    returnlist = [[] for _ in range(2)]

    if freshwater == str(1):
        requiredpolygonfields = ['ID_NO', 'BASIN_ID', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION', 'geometry']
    else:
        requiredpolygonfields = ['ID_NO', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION', 'geometry']
    # create a list that contains all the required polygon attributes
    # create a list that contains all the optional polygon attributes
    optionalpolygonfields = ['SOURCE', 'DIST_COMM', 'ISLAND', 'SUBSPECIES', 'SUBPOP', 'TAX_COMM', 'DATA_SENS', 'SENS_COMM']

    # create an empty list to contain the attribute names from the test data
    datapolygonfields = []

    # first screen for essential fields
    # create list of attributes in the layer
    for x in spatialdata:
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

# Checks point shapefile against the required and standard attributes, returns a list of fields that are not in either first list = missing required, second = fields to remove
def checkpointfields():
    global mapchecks
    global spatialdata

    # create container for the list of lists.
    returnlist = [[] for _ in range(2)]

    # create the basic require points list
    requiredpointfields = ['TaxonID', 'Binomial', 'Presence', 'Origin', 'Seasonal', 'Compiler', 'Year', 'Citation', 'Dec_Lat', 'SpatialRef', 'Dec_Long', 'Event_Year', 'geometry']

    # create a list that contains all the optional polygon attributes
    optionalpointfields = ['Source', 'Dist_comm', 'Island', 'Subspecies', 'Subpop', 'Tax_comm', 'BasisOfRec', 'CatalogNo', 'collectID', 'recordNo', 'recordedBy', 'day', 'countryCode', 'minElev', 'maxElev', 'verbatLat', 'verbatLong', 'verbatCoord', 'verbatSRS', 'coordUncert', 'georefVeri', 'georefnotes', 'subgenus', 'obsYrQual', 'obsCompNot', 'adminError', 'adminFixed', 'adminSrcFix', 'adminChang']

    # create an empty list to contain the attribute names from the test data
    datapointfields = []

    # first screen for essential fields
    # create list of attributes in the layer
    for x in spatialdata:
        datapointfields.append(x)

    # check to see if DATA_SENS is present, if yes then test to see if SENS_COMM is necessary
    if "Data_sens" in spatialdata:
        # first add DATA_SENS to the
        requiredpointfields.append('Data_sens')
        # then loop through the column checking the values
        for y in spatialdata["Data_sens"]:
            # if any are yes then add the SENS_COMM to the list of required as well
            if y == "Yes" or "yes" or "y":
                requiredpointfields.append('Sens_comm')
                break

    # find the missing required fields and append to the first position in the list
    missingrequired = list(set(requiredpointfields)-set(datapointfields))
    for x in missingrequired:
        returnlist[0].append(x)

    # find what additional fields have been provided
    extrafields = list(set(datapointfields)-set(requiredpointfields))
    if len(extrafields) == 0:
        for y in extrafields:
            returnlist[1].append(y)
    # if additional fields, then test to see if they are in the optional list
    else:
        fieldstoberemoved = list(set(extrafields)-set(optionalpointfields))
        for z in fieldstoberemoved:
            returnlist[1].append(z)

    # return values
    return returnlist

# check a field against its inbuilt criteria
def checkfield(attributetoinspect):
    global spatialdata

    # prepare saving details
    fp = locationofmaps.get()
    rownumber = tablerownumber.get()
    speciesname = "%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2])

    # field checks
    if attributetoinspect == 'PRESENCE':
        presenceerrors = []
        try:
            if spatialdata['PRESENCE'].dtype == 'object':
                presenceerrors.append(['Presence Text Error'])
                return presenceerrors
            spatialdata['PRESENCE'] = spatialdata['PRESENCE'].astype('int32')
            for prow, pvalue in enumerate(spatialdata['PRESENCE']):
                if pvalue == 0 or pvalue > 6:
                    presenceerrors.append(['PRESENCE', prow])
                if pvalue == 2:
                    presenceerrors.append(['PRESENCE', prow])
            spatialdata.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
            return presenceerrors
        except:
            presenceerrors.append(['Presence Error'])
            return presenceerrors

    elif attributetoinspect == 'ORIGIN':
        originerrors = []
        try:
            if spatialdata['ORIGIN'].dtype == 'object':
                originerrors.append(['Origin Text Error'])
                return originerrors
            spatialdata['ORIGIN'] = spatialdata['ORIGIN'].astype('int32')
            for orow, ovalue in enumerate(spatialdata['ORIGIN']):
                if ovalue == 0 or ovalue > 6:
                    originerrors.append(['ORIGIN', orow])
            spatialdata.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
            return originerrors
        except:
            originerrors.append(['Origin Error'])
            return originerrors

    elif attributetoinspect == 'SEASONAL':
        seasonalerrors = []
        try:
            if spatialdata['SEASONAL'].dtype == 'object':
                seasonalerrors.append(['Seasonal Text Error'])
                return seasonalerrors
            spatialdata['SEASONAL'] = spatialdata['SEASONAL'].astype('int32')
            for srow, svalue in enumerate(spatialdata['SEASONAL']):
                if svalue == 0 or svalue > 5:
                    seasonalerrors.append(['SEASONAL', srow])
            spatialdata.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
            return seasonalerrors
        except:
            seasonalerrors.append(['Seasonal Error'])
            return seasonalerrors

    elif attributetoinspect == 'COMPILER':
        comperrors = []
        try:
            for comrow, comvalue in enumerate(spatialdata['COMPILER']):
                if comvalue == "" or comvalue == None or comvalue == "text":
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
            if spatialdata['YEAR'].dtype == 'object':
                yearerrors.append(['Year Text Error'])
                return yearerrors
            for yrow, yvalue in enumerate(spatialdata['YEAR']):
                if len(str(yvalue)) != 4 or isinstance(yvalue, str) or yvalue > int(time.strftime("%Y")):
                    yearerrors.append(['YEAR', yrow])
            return yearerrors
        except:
            yearerrors.append(['Year Error'])
            return yearerrors

    elif attributetoinspect == 'CITATION':
        citationerrors = []
        try:
            firstvalue = (spatialdata['CITATION'][0])
            for crow, cvalue in enumerate(spatialdata['CITATION']):
                if cvalue == "" or cvalue != firstvalue or cvalue == "text" or cvalue == None:
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
            for brow, bvalue in enumerate(spatialdata['BINOMIAL']):
                if bvalue != ("%s %s" % (output, output2)):
                    binomialerrors.append(['BINOMIAL', brow])
            return binomialerrors
        except:
            binomialerrors.append(['Binomial Error'])
            return binomialerrors

    # check to see if ID_NO matches the SIS ID that we have for the species return if single error found
    elif attributetoinspect == 'SISID':
        SISIDerrors = []
        # get the SIS ID from the spreadsheet
        correctID = databasera.iat[rownumber, 0]
        try:
            if spatialdata['ID_NO'].dtype == 'object':
                SISIDerrors.append(['SISID Text Error'])
                return SISIDerrors
            for SISIDrow, SISIDvalue in enumerate(spatialdata['ID_NO']):
                if SISIDvalue != correctID:
                    SISIDerrors.append(['ID_NO', SISIDrow])
                    return SISIDerrors
            return SISIDerrors
        except:
            SISIDerrors.append(['SISID Error'])
            return SISIDerrors

    else:
        print("Invalid attribute provided")

# check a field against its inbuilt criteria (points tests)
def checkfieldpoints(attributetoinspect):
    global spatialdata

    # prepare saving details
    fp = locationofmaps.get()
    rownumber = tablerownumber.get()
    speciesname = "%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2])

    if attributetoinspect == 'PRESENCE':
        presenceerrors = []
        try:
            if spatialdata['Presence'].dtype == 'object':
                presenceerrors.append(['Presence Text Error'])
                return presenceerrors
            spatialdata['Presence'] = spatialdata['Presence'].astype('int32')
            for prow, pvalue in enumerate(spatialdata['Presence']):
                if pvalue == 0 or pvalue > 6:
                    presenceerrors.append(['Presence', prow])
                if pvalue == 2:
                    presenceerrors.append(['Presence', prow])
            spatialdata.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
            return presenceerrors
        except:
            presenceerrors.append(['Presence Error'])
            return presenceerrors

    elif attributetoinspect == 'ORIGIN':
        originerrors = []
        try:
            if spatialdata['Origin'].dtype == 'object':
                originerrors.append(['Origin Text Error'])
                return originerrors
            spatialdata['Origin'] = spatialdata['Origin'].astype('int32')
            for orow, ovalue in enumerate(spatialdata['Origin']):
                if ovalue == 0 or ovalue > 6:
                    originerrors.append(['Origin', orow])
            spatialdata.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
            return originerrors
        except:
            originerrors.append(['Origin Error'])
            return originerrors

    elif attributetoinspect == 'SEASONAL':
        seasonalerrors = []
        try:
            if spatialdata['Seasonal'].dtype == 'object':
                seasonalerrors.append(['Seasonal Text Error'])
                return seasonalerrors
            spatialdata['Seasonal'] = spatialdata['Seasonal'].astype('int32')
            for srow, svalue in enumerate(spatialdata['Seasonal']):
                if svalue == 0 or svalue > 5:
                    seasonalerrors.append(['Seasonal', srow])
            spatialdata.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
            return seasonalerrors
        except:
            seasonalerrors.append(['Seasonal Error'])
            return seasonalerrors

    elif attributetoinspect == 'COMPILER':
        comperrors = []
        try:
            for comrow, comvalue in enumerate(spatialdata['Compiler']):
                if comvalue == "" or comvalue == None or comvalue == "text":
                    comperrors.append(['Compiler', comrow])
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
            if spatialdata['Year'].dtype == 'object':
                yearerrors.append(['Year Text Error'])
                return yearerrors
            for yrow, yvalue in enumerate(spatialdata['Year']):
                if len(str(yvalue)) != 4 or isinstance(yvalue, str) or yvalue > int(time.strftime("%Y")):
                    yearerrors.append(['Year', yrow])
            return yearerrors
        except:
            yearerrors.append(['Year Error'])
            return yearerrors

    elif attributetoinspect == 'CITATION':
        citationerrors = []
        try:
            firstvalue = (spatialdata['Citation'][0])
            for crow, cvalue in enumerate(spatialdata['Citation']):
                if cvalue == "" or cvalue != firstvalue or cvalue == "text" or cvalue == None:
                    citationerrors.append(['Citation', crow])
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
            for brow, bvalue in enumerate(spatialdata['Binomial']):
                if bvalue != ("%s %s" % (output, output2)):
                    binomialerrors.append(['Binomial', brow])
            return binomialerrors
        except:
            binomialerrors.append(['Binomial Error'])
            return binomialerrors

    elif attributetoinspect == "Event Year":
        eventyearerrors = []
        try:
            if spatialdata['Event_Year'].dtype == 'object':
                eventyearerrors.append(['Event_Year Text Error'])
                return eventyearerrors
            for eyrow, eyvalue in enumerate(spatialdata['Event_Year']):
                if (len(str(eyvalue)) != 4 and eyvalue != 0) or isinstance(eyvalue, str) or eyvalue > int(time.strftime("%Y")):
                    eventyearerrors.append(['Event_Year', eyrow])
            return eventyearerrors
        except:
            eventyearerrors.append(['Event_Year Error'])
            return eventyearerrors

    elif attributetoinspect == "SpatialRef":
        spatialreferrors = []
        try:
            for srrow, srvalue in enumerate(spatialdata['SpatialRef']):
                if srvalue != "WGS84":
                    spatialreferrors.append(['SpatialRef', srrow])
            return spatialreferrors
        except:
            spatialreferrors.append(['SpatialRef Error'])
            return spatialreferrors

    elif attributetoinspect == "Invalidlatorlong":
        declatandlongerrors = []
        try:
            # run through Dec_Lat field looking for invalid values
            for dlrow, dlvalue in enumerate(spatialdata['Dec_Lat']):
                # test lat values for validity
                if dlvalue != isinstance(dlvalue, float) or dlvalue > 90 or dlvalue < -90 or dlvalue == 0:
                    declatandlongerrors.append(['Dec_Lat', dlrow])
                # test to see if lat matches lat in the geometry
                temp = str(spatialdata["geometry"][dlrow])
                temp2 = temp.replace("(", "")
                temp3 = temp2.replace(")", "")
                xy = temp3.split(" ")
                geolat = float(xy[2])
                # tolerance of matching (currently exact match required) (also check validity of geofield)
                if dlvalue != geolat or geolat > 90 or geolat < -90 or geolat == 0:
                    declatandlongerrors.append(['Geo_Lat', dlrow])

            # run through Dec_Long field looking for invalid values
            for dlongrow, dllongvalue in enumerate(spatialdata['Dec_Lat']):
                if dllongvalue != isinstance(dllongvalue, float) or dllongvalue > 180 or dllongvalue < -180 or dllongvalue == 0:
                    declatandlongerrors.append(['Dec_Long', dlongrow])
                # test to see if lat matches lat in the geometry
                temp = str(spatialdata["geometry"][dlongrow])
                temp2 = temp.replace("(", "")
                temp3 = temp2.replace(")", "")
                xy = temp3.split(" ")
                geolong = float(xy[1])
                # tolerance of matching (currently exact match required) (also check validity of geofield)
                if dlvalue != geolong or geolong > 90 or geolong < -90 or geolong == 0:
                    declatandlongerrors.append(['Geo_Long', dlongrow])

            # finally return the errortable
            return declatandlongerrors
        except:
            declatandlongerrors.append(['Invalidlatorlong Error'])
            return declatandlongerrors

    elif attributetoinspect == "geolatdeclat":
        geolatdeclaterrors = []
        try:
            for geolatdeclatrow, geolatdeclatvalue in enumerate(spatialdata['Dec_Lat']):
                temp = str(spatialdata["geometry"][geolatdeclatrow])
                temp2 = temp.replace("(", "")
                temp3 = temp2.replace(")", "")
                xy = temp3.split(" ")
                if geolatdeclatvalue != float(xy[2]):
                    geolatdeclaterrors.append(['Dec_Lat', geolatdeclatrow])
            return geolatdeclaterrors
        except:
            geolatdeclaterrors.append('geolatdeclat Error')
            return geolatdeclaterrors

    elif attributetoinspect == "geolongdeclong":
        geolongdeclongerrors = []
        try:
            for geolongdeclongrow, geolongdeclongvalue in enumerate(spatialdata['Dec_Long']):
                temp = str(spatialdata["geometry"][geolongdeclongrow])
                temp2 = temp.replace("(", "")
                temp3 = temp2.replace(")", "")
                xy = temp3.split(" ")
                if geolongdeclongvalue != float(xy[1]):
                    geolongdeclongerrors.append(['Dec_Lat', geolongdeclongrow])
            return geolongdeclongerrors
        except:
            geolongdeclongerrors.append('geolongdeclong Error')
            return geolongdeclongerrors

    elif attributetoinspect == 'SISID':
        SISIDerrors = []
        # get the SIS ID from the spreadsheet
        correctID = databasera.iat[rownumber, 0]
        try:
            for SISIDrow, SISIDvalue in enumerate(spatialdata['TaxonID']):
                if SISIDvalue != correctID:
                    SISIDerrors.append(['ID_NO', SISIDrow])
                    return SISIDerrors
            return SISIDerrors
        except:
            SISIDerrors.append(['SISID Error'])
            return SISIDerrors
    else:
        print("Invalid attribute provided")

# check the order of the attributes returns 1 if correct, 0 if not
def checkattributeorder(pointorpoly):
    global spatialdata

    if pointorpoly == "Polygon":
        correctorder = ['ID_NO', 'BASIN_ID', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION', 'SOURCE', 'DIST_COMM', 'ISLAND', 'SUBSPECIES', 'SUBPOP', 'TAX_COMM', 'DATA_SENS', 'SENS_COMM', 'Shape_Leng', 'Shape_Area', 'geometry']
    else:
        correctorder = ['TaxonID', 'Binomial', 'Presence', 'Origin', 'Seasonal', 'Compiler', 'Year', 'Dec_Lat', 'Dec_Long', 'SpatialRef', 'Event_Year', 'Citation',  'Source', 'Dist_comm', 'Island', 'Subspecies', 'Subpop', 'Data_sens','Sens_comm',  'Tax_comm', 'BasisOfRec', 'CatalogNo', 'collectID', 'recordNo', 'recordedBy', 'day', 'countryCode', 'minElev', 'maxElev', 'verbatLat', 'verbatLong', 'verbatCoord', 'verbatSRS', 'coordUncert', 'georefVeri', 'georefnotes', 'subgenus', 'obsYrQual', 'obsCompNot', 'adminError', 'adminFixed', 'adminSrcFix', 'adminChange', 'geometry']

    finalorder=[]
    #first create the local correct order
    for x in correctorder:
        if x in spatialdata:
            finalorder.append(x)

    for x, y in enumerate(spatialdata):
        if finalorder[x] != y:
            return False
    return True

# collates and writes to file the changes for the required attribute changes
def commitchanges(correctorder, speciesname, sourcefunction, extrafields):
    global fixattributesTL
    global spatialdata

    # create a list to store the changes that need to be made
    listofchanges = []
    internalcounter = 3

    # if coming from the optional attributer fixer then need to swap the columns round
    if sourcefunction == "optional":
        for counter, combobox in enumerate(fixattributesTL.children.values()):
            if 'combobox' in str(combobox):
                if combobox.get() != "PRESENT" and combobox.get() != "Not Present":
                    listofchanges.append([combobox.get(), extrafields[counter - internalcounter]])
                internalcounter = internalcounter + 1
    else:
        # collate the changes to be made list original to what it should be
        for counter, combobox in enumerate(fixattributesTL.children.values()):
            if 'combobox' in str(combobox):
                if combobox.get() != "PRESENT" and combobox.get() != "Not Present":
                    listofchanges.append([correctorder[counter - internalcounter], combobox.get()])
                internalcounter = internalcounter + 1

    # loop through the list of changes and add columns as necessary
    for x in listofchanges:
        # if add as a new variable then add a new variable in with the correct type
        if x[1] == "Add as a new variable":
            # if number then 0 column, else put filler text
            if x[0] in ('BINOMIAL', 'COMPILER', 'CITATION', 'Binomial', 'Compiler', 'Citation'):
                spatialdata["%s" % x[0]] = "text"
            elif x[0] in ('Dec_Lat', 'Dec_Long'):
                spatialdata["%s" % x[0]] = 0.00
            else:
                spatialdata["%s" % x[0]] = 0
        # if not then copy the old column over to a new column with a new name, then drop old column
        else:
            spatialdata["%s" % x[0]] = spatialdata["%s" % x[1]]
            spatialdata.drop("%s" % x[1], axis=1, inplace=True)

    # destroy the toplevel
    fixattributesTL.destroy()

    # regenerate the map
    rownumber = (tablerownumber.get())
    createtableandaddtomap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    fixattributesTL.destroy()

    # instead of running the whole thing again, remember the f
    maptests(speciesname)

# Fix the required attributes field
def fixrequiredattributes(missingrequired, speciesname, pointorpoly):
    global fixattributesTL
    global spatialdata

    freshwater = freshwaterSV.get()

    if pointorpoly == "Polygon":
        if freshwater == str(1):
            correctorder = ['ID_NO', 'BASIN_ID', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION']
        else:
            correctorder = ['ID_NO', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION']
    else:
        correctorder = ['TaxonID', 'Binomial', 'Presence', 'Origin', 'Seasonal', 'Compiler', 'Year', 'Citation', 'Dec_Lat', 'SpatialRef', 'Dec_Long', 'Event_Year']

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
    for x in spatialdata:
        listofattributes.append(x)

    # drop the geometry so it doesn't cause problems
    listofattributes.remove("geometry")

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
            ttk.Label(fixattributesTL, text="%s" % y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x+1, sticky=NSEW)
            ttk.Combobox(fixattributesTL, state="disabled", values=listofattributes).grid(column=1, row=x+1, sticky=NSEW)

    # run through and for all blank ones write as PRESENT
    # collate the changes to be made list original to what it should be
    for counter, combobox in enumerate(fixattributesTL.children.values()):
        if 'combobox' in str(combobox):
            if combobox.instate([DISABLED, ]):
                combobox.set("PRESENT")
                combobox.config(state="readonly")
            else:
                combobox.set("Add as a new variable")

    # finally add the commit button to the bottom
    ttk.Button(fixattributesTL, text="Commit Changes", command=lambda: commitchanges(correctorder, speciesname, "normal", None)).grid(column=1, row=20, sticky=NSEW, columnspan=2)
    # status of each one can either be present, or a drop down menu with the full list of attributes remaining or an add button
    # at the end it deletes the current map and reopens the new one

    # give weight to the rows and column
    fixattributesTL.columnconfigure((0, 1), weight=1)
    fixattributesTL.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 ,15 ,16 ,17 ,18 ,19 ,20), weight=1)

    # fill the remaing space
    for child in fixattributesTL.winfo_children():
        child.grid_configure(padx=5, pady=5)

# Fix the required attributes field
def fixoptionalattributes(extrafields, speciesname, pointorpoly):
    global fixattributesTL
    global spatialdata

    if pointorpoly == "Polygon":
        correctorder = ['SOURCE', 'DIST_COMM', 'ISLAND', 'SUBSPECIES', 'SUBPOP', 'TAX_COMM', 'DATA_SENS', 'SENS_COMM']
    else:
        correctorder = ['Data_sens','Sens_comm','Source', 'Dist_comm', 'Island', 'SUBSPECIES', 'SUBPOP', 'Tax_comm', 'BasisOfRec', 'CatalogNo', 'collectID', 'recordNo', 'recordedBy', 'day', 'countryCode', 'minElev', 'maxElev', 'verbatLat', 'verbatLong', 'verbatCoord', 'verbatSRS', 'coordUncert', 'georefVeri', 'georefnotes', 'subgenus', 'obsYrQual', 'obsCompNot', 'adminError', 'adminFixed', 'adminSrcFix', 'adminChang']

    # create a top level in the middle of the screen
    # create the toplevel to house everything
    # dimensions of parent window
    x = root.winfo_screenwidth()
    y = root.winfo_screenheight()

    # set the width to the width of the
    fixattributesTL = Toplevel()
    fixattributesTL.config(background="#DFE8F6")
    fixattributesTL.geometry('%dx%d+%d+%d' % (500, 500, x/2 - 250, y/2 - 250))

    # add Not present to the start of the list
    correctorder.insert(0, "Not Present")

    # Create the table headers
    ttk.Label(fixattributesTL, text="Optional Attribute", font=(None, 15, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=0, sticky=NSEW)
    ttk.Label(fixattributesTL, text="Status", font=(None, 15, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=1, row=0, sticky=NSEW)
    # run through the required attributes, if the attribute exists in the list of missing then flag the options up
    for x, y in enumerate(extrafields):
        # if in the list of missing then create the label with the options
        if y in correctorder:
            ttk.Label(fixattributesTL, text="%s" % y, borderwidth=3, relief="solid", background="#DFE8F6", foreground="#828282").grid(column=0, row=x+1, sticky=NSEW)
            ttk.Combobox(fixattributesTL, state="disabled").grid(column=1, row=x+1, sticky=NSEW)
        else:
            ttk.Label(fixattributesTL, text="%s" % y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x+1, sticky=NSEW)
            ttk.Combobox(fixattributesTL, values=correctorder, state="readonly").grid(column=1, row=x+1, sticky=NSEW)

    # run through and for all blank ones write as PRESENT
    # collate the changes to be made list original to what it should be
    for counter, combobox in enumerate(fixattributesTL.children.values()):
        if 'combobox' in str(combobox):
            combobox.set("Not Present")

    # finally add the commit button to the bottom
    ttk.Button(fixattributesTL, text="Commit Changes", command=lambda: commitchanges(correctorder, speciesname, "optional", extrafields)).grid(column=1, row=50, sticky=NSEW, columnspan=2)
    # status of each one can either be present, or a drop down menu with the full list of attributes remaining or an add button
    # at the end it deletes the current map and reopens the new one

    # give weight to the rows and column
    fixattributesTL.columnconfigure((0, 1), weight=1)
    fixattributesTL.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,14,15,16,17,18,19,20), weight=1)

    # fill the remaing space
    for child in fixattributesTL.winfo_children():
        child.grid_configure(padx=5, pady=5)

# Reorder the attributes so that they are in the correct order
def reorganiseattributes(speciesname, pointorpoly):
    global spatialdata

    if pointorpoly == "Polygon":
        correctorder = ['ID_NO', 'BASIN_ID', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION', 'SOURCE', 'DIST_COMM', 'ISLAND', 'SUBSPECIES', 'SUBPOP', 'TAX_COMM', 'DATA_SENS', 'SENS_COMM', 'Shape_Leng', 'Shape_Area', 'geometry']
    else:
        correctorder = ['TaxonID', 'Binomial', 'Presence', 'Origin', 'Seasonal', 'Compiler', 'Year', 'Dec_Lat', 'Dec_Long', 'SpatialRef', 'Event_Year', 'Citation',  'Source', 'Dist_comm', 'Island', 'Subspecies', 'Subpop', 'Data_sens','Sens_comm', 'Tax_comm', 'BasisOfRec', 'CatalogNo', 'collectID', 'recordNo', 'recordedBy', 'day', 'countryCode', 'minElev', 'maxElev', 'verbatLat', 'verbatLong', 'verbatCoord', 'verbatSRS', 'coordUncert', 'georefVeri', 'georefnotes', 'subgenus', 'obsYrQual', 'obsCompNot', 'adminError', 'adminFixed', 'adminSrcFix', 'adminChange', 'geometry']

    finalorder=[]
    # first run through and remove all attributes not present
    for x in correctorder:
        if x in spatialdata:
            finalorder.append(x)

    # recreate the dataframe with the correct order
    spatialdata = spatialdata[finalorder]

    # recreate the map
    rownumber = (tablerownumber.get())
    createtableandaddtomap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname)

# Remove the extra fields that have been provided
def dropextrafields(speciesname, pointorpoly):
    global spatialdata

    # first rerun the extra fields to get the correct data
    if pointorpoly == "Polygon":
        fieldstodrop = checkpolygonfields()[1]
    else:
        fieldstodrop = checkpointfields()[1]

    for x in fieldstodrop:
        spatialdata.drop('%s' % x, axis=1, inplace=True)

    # recreate the map
    rownumber = (tablerownumber.get())
    createtableandaddtomap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname)

# commit citation field changes
def commitcitationfieldrepair(speciesname, value, pointorpoly):
    global spatialdata

    # replace all values in the BINOMIAL field with the correct name
    if pointorpoly == "Polygon":
        spatialdata["CITATION"] = str(value)
    else:
        spatialdata["Citation"] = str(value)

    # recreate the map
    rownumber = (tablerownumber.get())
    createtableandaddtomap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    citationrepairTL.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname)

# function to ask user what the correct citation should be and offer the functionality to repair it
def repaircitationfield(speciesname, pointorpoly):
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
    ttk.Button(citationrepairTL, text="Commit", command=lambda: commitcitationfieldrepair(speciesname, newcitationSV.get(), pointorpoly)).grid(column=0, row=3, sticky=NSEW, columnspan=3)

    # give weight to the rows and column
    citationrepairTL.columnconfigure((0, 1, 2), weight=1)
    citationrepairTL.rowconfigure((0, 1, 2), weight=1)

    # fill the remaing space
    for child in citationrepairTL.winfo_children():
        child.grid_configure(padx=2, pady=5)

# Repair binomial field by copying the SIS name into all the rows of the binomial column
def repairbinomialfield(speciesname, pointorpoly):
    global spatialdata

    rownumber = (tablerownumber.get())

    # get the correct name from the database
    correctname = "%s %s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2])

    if pointorpoly == "Polygon":
        # replace all values in the BINOMIAL field with the correct name
        spatialdata["BINOMIAL"] = correctname
    else:
        spatialdata["Binomial"] = correctname

    # recreate the map
    createtableandaddtomap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname)

# Repair the ID_NO field by copying the SIS ID into all the rows of the ID_NO column
def repairIDNOfield(speciesname, pointorpoly):
    global spatialdata

    rownumber = (tablerownumber.get())

    # get the correct name from the database
    SISID = databasera.iat[rownumber, 0]

    if pointorpoly == "Polygon":
        # replace all values in the BINOMIAL field with the correct name
        spatialdata["ID_NO"] = SISID
    else:
        spatialdata["TaxonID"] = SISID

    createtableandaddtomap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname)

# Gets edits made by the user for the POS repairs and commits them to the shapefile
def commitPOSchanges(errortable, speciesname, field):
    global repairPOSfieldsTL
    global citationsession
    global label_frame
    global spatialdata

    # first take the error table, add a new column which is the corrected data
    counter = 0
    if field == "compiler":
        for combobox in label_frame.children.values():
            if 'combobox' in str(combobox):
                # test to see if any invalid codes provided, cancel if so
                if combobox.get() == "Invalid Code":
                    messagebox.showerror(title="Error Duck", message="Invalid Presence code provided please fix before committing")
                    return 0
                else:
                    errortable[counter].append(combobox.get())
                    citationsession.append(combobox.get())
                    counter = counter + 1
    else:
        for combobox in label_frame.children.values():
            if 'combobox' in str(combobox):
                # test to see if any invalid codes provided, cancel if so
                if combobox.get() == "Invalid Code":
                    messagebox.showerror(title="Error Duck", message="Invalid Presence code provided please fix before committing")
                    return 0
                else:
                    errortable[counter].append(combobox.get())
                    counter = counter + 1
    # run through the compiler record list and remove any duplicates
    if field == "compiler":
        citationsession = list(set(citationsession))

    # loop through the corrections and fix the shapefile
    for x in errortable:
        spatialdata.at[x[1], x[0]] = x[2]

    # destroy the toplevel
    repairPOSfieldsTL.destroy()

    # create the new map
    rownumber = (tablerownumber.get())
    createtableandaddtomap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname)

# Gets edits made by the user for the POS text repairs and commits them to the shapefile
def commitPOStextchanges(correctiontable, speciesname, fieldname):
    global repairPOSfieldsTL
    global spatialdata
    # first take the error table, add a new column which is the corrected data
    counter = 0
    for combobox in repairPOSfieldsTL.children.values():
        if 'combobox' in str(combobox):
            # test to see if any invalid codes provided, cancel if so
            if combobox.get() == "Invalid Code":
                messagebox.showerror(title="Error Duck", message="Invalid code provided please fix before committing")
                return 0
            else:
                # add the matched code
                correctiontable[list(correctiontable.items())[counter][0]] = int(combobox.get())
                counter = counter + 1

    templist = []
    # loop through the corrections using the table to create a new column (of correct type)
    for x in spatialdata[fieldname]:
        templist.append(correctiontable[x])

    # drop exisiting column
    spatialdata.drop(fieldname, axis=1, inplace=True)
    # add in column with the same name and correct values
    spatialdata[fieldname] = pandas.Series(templist)

    # get the data from the designated location
    fp = locationofmaps.get()

    # save the file
    savemaptofile(fp, speciesname)

    # destroy the toplevel
    repairPOSfieldsTL.destroy()

    # create the new map
    rownumber = (tablerownumber.get())
    createmapfromscratch("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    repairPOSfieldsTL.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname)

# For the POS repair window, fills all rows with a number provided by the user
def fillallPOS(value, attribute):
    testvalue = value.get()

    if attribute == "presence":
        if testvalue in ["1", "3", "4", "5", "6"]:
            for combobox in label_frame.children.values():
                if 'combobox' in str(combobox):
                    combobox.set(testvalue)
                    value.delete(0, len(testvalue))
        else:
            messagebox.showerror(title="Error Duck", message="Invalid Presence code")
            value.delete(0, len(testvalue))
    elif attribute == "origin":
        if testvalue in ["1", "2", "3", "4", "5", "6"]:
            for combobox in label_frame.children.values():
                if 'combobox' in str(combobox):
                    combobox.set(testvalue)
                    value.delete(0, len(testvalue))
        else:
            messagebox.showerror(title="Error Duck", message="Invalid origin code")
            value.delete(0, len(testvalue))
    elif attribute == "seasonal":
        if testvalue in ["1", "2", "3", "4", "5"]:
            for combobox in label_frame.children.values():
                if 'combobox' in str(combobox):
                    combobox.set(testvalue)
                    value.delete(0, len(testvalue))
        else:
            messagebox.showerror(title="Error Duck", message="Invalid seasonality code")
            value.delete(0, len(testvalue))
    elif attribute == "compiler":
        for combobox in label_frame.children.values():
            if 'combobox' in str(combobox):
                combobox.set(testvalue)
                value.delete(0, len(testvalue))
    elif attribute == "ID_NO":
        for combobox in label_frame.children.values():
            if 'combobox' in str(combobox):
                combobox.set(testvalue)
                value.delete(0, len(testvalue))
    else:
        if len(testvalue) == 4 and int(testvalue) <= int(time.strftime("%Y")):
            for combobox in label_frame.children.values():
                if 'combobox' in str(combobox):
                    combobox.set(testvalue)
                    value.delete(0, len(testvalue))
        else:
            messagebox.showerror(title="Error Duck", message="Invalid year provided")
            value.delete(0, len(testvalue))

# Repair the presence field, convert all 2's to 1 and flag the rest for review
def repairPOSfields(speciesname, errortable, field):
    global repairPOSfieldsTL
    global spatialdata
    global citationsession
    global label_frame

    # create top level
    # create the toplevel to house everything
    # dimensions of parent window
    x = root.winfo_screenwidth()
    y = root.winfo_screenheight()

    # set the width to the width of the
    repairPOSfieldsTL = Toplevel()
    repairPOSfieldsTL.config(background="#DFE8F6")
    repairPOSfieldsTL.geometry('%dx%d+%d+%d' % (500, 500, x / 2 - 250, y / 2 - 250))
    repairPOSfieldsTL.columnconfigure((0, 1, 2), weight=1)
    repairPOSfieldsTL.rowconfigure((0), weight=1)
    repairPOSfieldsTL.resizable(width=False, height=False)

    # master frame to put it all in
    frame_main = ttk.Frame(repairPOSfieldsTL)
    frame_main.grid(row=0, column=0, sticky=NSEW, columnspan=3)
    frame_main.grid_columnconfigure(2, weight=1)
    frame_main.grid_rowconfigure(2, weight=1)

    # Create the table headers
    ttk.Label(frame_main, text="%s attribute errors" % field.capitalize(), font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=0, sticky=NSEW, columnspan=3)
    ttk.Label(frame_main, text="Error on row", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=1, sticky=NSEW)
    ttk.Label(frame_main, text="Current Value", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=1, row=1, sticky=NSEW)
    ttk.Label(frame_main, text="New Value", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=2, row=1, sticky=NSEW, columnspan=2)

    # add a frame to house everything below
    subframe = ttk.Frame(frame_main)
    subframe.grid(row=2, column=0, sticky=NSEW, columnspan=3)
    subframe.grid(row=2, column=0, sticky=NSEW)
    subframe.grid_rowconfigure(0, weight=1)
    subframe.grid_columnconfigure(0, weight=1)
    subframe.grid_propagate(False)

    # add canvas into this frame
    canvas = Canvas(subframe)
    canvas.grid(column=0, row=0, sticky=NSEW)
    canvas.config(background="#DFE8F6", highlightthickness=0)

    # add scroll bar
    vsb = ttk.Scrollbar(subframe, orient="vertical", command=canvas.yview)
    vsb.grid(row=0, column=1, sticky=NS)
    canvas.configure(yscrollcommand=vsb.set)

    # add frame on the canvas to contain the data
    label_frame = ttk.Frame(canvas)
    label_frame.grid(row=0, column=0, sticky=NSEW)

    canvas.create_window((0, 0), window=label_frame, anchor=NW)

    # set the parameters to fill in the table
    columns = 3
    rows = len(errortable)

    # create the blank dictionary to track all entities
    labels = [[ttk.Label(), ttk.Label(), ttk.Combobox] for j in range(rows)]

    if field == "presence":
        # run through the error table, create a new row for each error
        for i in range(0, rows):
            labels[i][0] = ttk.Label(label_frame, anchor="center", text="%s" % errortable[i][1], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][0].grid(column=0, row=i, sticky=NSEW)
            labels[i][1] = ttk.Label(label_frame, anchor="center", text="%s" % spatialdata[errortable[i][0]][errortable[i][1]], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][1].grid(column=1, row=i, sticky=NSEW)
            labels[i][2] = ttk.Combobox(label_frame, state="readonly", values=[1, 3, 4, 5, 6])
            labels[i][2].grid(column=2, row=i, sticky=NSEW)

        # run and convert all 2's to 1's (while leaving the option to change it to something else if wanted.
        counter = 0
        for combobox in label_frame.children.values():
            if 'combobox' in str(combobox):
                if spatialdata[errortable[counter][0]][errortable[counter][1]] == 2:
                    combobox.set(1)
                else:
                    combobox.set("Invalid Code")
                counter = counter + 1

    elif field == "origin":
        # run through the error table, create a new row for each error
        for i in range(0, rows):
            labels[i][0] = ttk.Label(label_frame, anchor="center", text="%s" % errortable[i][1], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][0].grid(column=0, row=i, sticky=NSEW)
            labels[i][1] = ttk.Label(label_frame, anchor="center", text="%s" % spatialdata[errortable[i][0]][errortable[i][1]], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][1].grid(column=1, row=i, sticky=NSEW)
            labels[i][2] = ttk.Combobox(label_frame, state="readonly", values=[1, 2, 3, 4, 5, 6])
            labels[i][2].grid(column=2, row=i, sticky=NSEW)

    elif field == "seasonal":
        # get the current code for this row
        for i in range(0, rows):
            labels[i][0] = ttk.Label(label_frame, anchor="center", text="%s" % errortable[i][1], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][0].grid(column=0, row=i, sticky=NSEW)
            labels[i][1] = ttk.Label(label_frame, anchor="center", text="%s" % spatialdata[errortable[i][0]][errortable[i][1]], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][1].grid(column=1, row=i, sticky=NSEW)
            labels[i][2] = ttk.Combobox(label_frame, state="readonly", values=[1, 2, 3, 4, 5])
            labels[i][2].grid(column=2, row=i, sticky=NSEW)

    elif field == "year":
        for i in range(0, rows):
            labels[i][0] = ttk.Label(label_frame, anchor="center", text="%s" % errortable[i][1], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][0].grid(column=0, row=i, sticky=NSEW)
            labels[i][1] = ttk.Label(label_frame, anchor="center", text="%s" % spatialdata[errortable[i][0]][errortable[i][1]], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][1].grid(column=1, row=i, sticky=NSEW)
            labels[i][2] = ttk.Combobox(label_frame, state="normal", values=["%s" % int(time.strftime("%Y"))])
            labels[i][2].grid(column=2, row=i, sticky=NSEW)

    elif field == "compiler":
        # run through the error table, create a new row for each error
        for i in range(0, rows):
            labels[i][0] = ttk.Label(label_frame, anchor="center", text="%s" % errortable[i][1], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][0].grid(column=0, row=i, sticky=NSEW)
            labels[i][1] = ttk.Label(label_frame, anchor="center", text="%s" % spatialdata[errortable[i][0]][errortable[i][1]], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][1].grid(column=1, row=i, sticky=NSEW)
            labels[i][2] = ttk.Combobox(label_frame, state="normal", values=citationsession)
            labels[i][2].grid(column=2, row=i, sticky=NSEW)

    else:
        # run through the error table, create a new row for each error
        for i in range(0, rows):
            labels[i][0] = ttk.Label(label_frame, anchor="center", text="%s" % errortable[i][1], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][0].grid(column=0, row=i, sticky=NSEW)
            labels[i][1] = ttk.Label(label_frame, anchor="center", text="%s" % spatialdata[errortable[i][0]][errortable[i][1]], borderwidth=3, relief="flat", background="#DFE8F6", width=18)
            labels[i][1].grid(column=1, row=i, sticky=NSEW)
            labels[i][2] = ttk.Combobox(label_frame, state="readonly", values=["%s" % spatialdata[errortable[i][0]][errortable[i][1]]])
            labels[i][2].grid(column=2, row=i, sticky=NSEW)

    # Update buttons frames idle tasks to let tkinter calculate buttons sizes
    label_frame.update()

    # first5columns_width = sum([labels[0][j].winfo_width() for j in range(0, columns)])
    first5rows_height = sum([labels[i][0].winfo_height() for i in range(0, rows)])

    # set the subframe width so that it matches the
    subframe.config(height=first5rows_height, width=canvas.winfo_width())

    # finally add the commit button to the bottom
    if field == "compiler":
        ttk.Button(repairPOSfieldsTL, text="Commit Changes", command=lambda: commitPOSchanges(errortable, speciesname, "compiler")).grid(row=3, column=2, sticky="SEW")
        test = ttk.Entry(repairPOSfieldsTL)
    else:
        ttk.Button(repairPOSfieldsTL, text="Commit Changes", command=lambda: commitPOSchanges(errortable, speciesname, "other")).grid(row=3, column=2, sticky="SEW")
        test = ttk.Entry(repairPOSfieldsTL)

    # Add a fill all button
    test.grid(row=3, column=1, sticky="SEW")
    ttk.Button(repairPOSfieldsTL, text="Fill All", command=lambda: fillallPOS(test, field)).grid(row=3, column=0, sticky="SEW")

    # Set the canvas scrolling region
    canvas.config(scrollregion=canvas.bbox("all"))

# Convert text field to numeric, giving the user manual input to change the fields
def convertandrepairtextPOSfields(speciesname, field, pointorpoly):
    global repairPOSfieldsTL
    global spatialdata

    # create the toplevel to house everything
    # dimensions of parent window
    x = root.winfo_screenwidth()
    y = root.winfo_screenheight()

    # set the width to the width of the
    repairPOSfieldsTL = Toplevel()
    repairPOSfieldsTL.config(background="#DFE8F6")
    repairPOSfieldsTL.geometry('%dx%d+%d+%d' % (500, 500, x/2 - 250, y/2 - 250))

    # Create the table headers
    ttk.Label(repairPOSfieldsTL, text="%s attribute errors (only showing unique values)" % field.capitalize(), font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=0, sticky=NSEW, columnspan=3)
    ttk.Label(repairPOSfieldsTL, text="Current value", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=1, sticky=NSEW)
    ttk.Label(repairPOSfieldsTL, text="New Value", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=1, row=1, sticky=NSEW)

    # create the list to hold correction map
    uniquetable = collections.OrderedDict()
    counter = 0

    if pointorpoly == "polygon":
        if field == "PRESENCE":
            # run through the shapefile and pick out unique values
            for x, y in enumerate(spatialdata["PRESENCE"]):
                if y not in uniquetable:
                    uniquetable[y] = counter
                    counter = counter + 1
            # run through the error table, create a new row for each error
            for x, y in enumerate(uniquetable):
                # get the current code for this row
                # if in the list of missing then create the label with the options
                ttk.Label(repairPOSfieldsTL, anchor="center", text=y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
                ttk.Combobox(repairPOSfieldsTL, state="readonly", values=[1, 3, 4, 5, 6]).grid(column=1, row=x + 2, sticky=NSEW)
        elif field == "ORIGIN":
            # run through the shapefile and pick out unique values
            for x, y in enumerate(spatialdata["ORIGIN"]):
                if y not in uniquetable:
                    uniquetable[y] = counter
                    counter = counter + 1
            # run through the error table, create a new row for each error
            for x, y in enumerate(uniquetable):
                # get the current code for this row
                # if in the list of missing then create the label with the options
                ttk.Label(repairPOSfieldsTL, anchor="center", text=y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
                ttk.Combobox(repairPOSfieldsTL, state="readonly", values=[1, 2, 3, 4, 5, 6]).grid(column=1, row=x + 2, sticky=NSEW)
        elif field == "SEASONAL":
            # run through the shapefile and pick out unique values
            for x, y in enumerate(spatialdata["SEASONAL"]):
                if y not in uniquetable:
                    uniquetable[y] = counter
                    counter = counter + 1
            # run through the error table, create a new row for each error
            for x, y in enumerate(uniquetable):
                # get the current code for this row
                # if in the list of missing then create the label with the options
                ttk.Label(repairPOSfieldsTL, anchor="center", text=y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
                ttk.Combobox(repairPOSfieldsTL, state="readonly", values=[1, 2, 3, 4, 5, 6]).grid(column=1, row=x + 2, sticky=NSEW)
        elif field == "YEAR":
            # run through the shapefile and pick out unique values
            for x, y in enumerate(spatialdata["YEAR"]):
                if y not in uniquetable:
                    uniquetable[y] = counter
                    counter = counter + 1
            # run through the error table, create a new row for each error
            for x, y in enumerate(uniquetable):
                # get the current code for this row
                # if in the list of missing then create the label with the options
                ttk.Label(repairPOSfieldsTL, anchor="center", text=y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
                ttk.Combobox(repairPOSfieldsTL, state="normal", values=["%s" % int(time.strftime("%Y"))]).grid(column=1, row=x + 2, sticky=NSEW)
        elif field == "ID_NO":
            # run through the shapefile and pick out unique values
            for x, y in enumerate(spatialdata["ID_NO"]):
                if y not in uniquetable:
                    uniquetable[y] = counter
                    counter = counter + 1
            # run through the error table, create a new row for each error
            for x, y in enumerate(uniquetable):
                # get the current code for this row
                # if in the list of missing then create the label with the options
                ttk.Label(repairPOSfieldsTL, anchor="center", text=y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
                ttk.Combobox(repairPOSfieldsTL, state="normal", values=[0]).grid(column=1, row=x + 2, sticky=NSEW)
        else:
            pass
    # points version
    else:
        if field == "Presence":
            # run through the shapefile and pick out unique values
            for x, y in enumerate(spatialdata["Presence"]):
                if y not in uniquetable:
                    uniquetable[y] = counter
                    counter = counter + 1
            # run through the error table, create a new row for each error
            for x, y in enumerate(uniquetable):
                # get the current code for this row
                # if in the list of missing then create the label with the options
                ttk.Label(repairPOSfieldsTL, anchor="center", text=y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
                ttk.Combobox(repairPOSfieldsTL, state="readonly", values=[1, 3, 4, 5, 6]).grid(column=1, row=x + 2, sticky=NSEW)
        elif field == "Origin":
            # run through the shapefile and pick out unique values
            for x, y in enumerate(spatialdata["Origin"]):
                if y not in uniquetable:
                    uniquetable[y] = counter
                    counter = counter + 1
            # run through the error table, create a new row for each error
            for x, y in enumerate(uniquetable):
                # get the current code for this row
                # if in the list of missing then create the label with the options
                ttk.Label(repairPOSfieldsTL, anchor="center", text=y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
                ttk.Combobox(repairPOSfieldsTL, state="readonly", values=[1, 2, 3, 4, 5, 6]).grid(column=1, row=x + 2, sticky=NSEW)
        elif field == "Seasonal":
            # run through the shapefile and pick out unique values
            for x, y in enumerate(spatialdata["Seasonal"]):
                if y not in uniquetable:
                    uniquetable[y] = counter
                    counter = counter + 1
            # run through the error table, create a new row for each error
            for x, y in enumerate(uniquetable):
                # get the current code for this row
                # if in the list of missing then create the label with the options
                ttk.Label(repairPOSfieldsTL, anchor="center", text=y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
                ttk.Combobox(repairPOSfieldsTL, state="readonly", values=[1, 2, 3, 4, 5, 6]).grid(column=1, row=x + 2, sticky=NSEW)
        elif field == "Year":
            # run through the shapefile and pick out unique values
            for x, y in enumerate(spatialdata["Year"]):
                if y not in uniquetable:
                    uniquetable[y] = counter
                    counter = counter + 1
            # run through the error table, create a new row for each error
            for x, y in enumerate(uniquetable):
                # get the current code for this row
                # if in the list of missing then create the label with the options
                ttk.Label(repairPOSfieldsTL, anchor="center", text=y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
                ttk.Combobox(repairPOSfieldsTL, state="normal", values=["%s" % int(time.strftime("%Y"))]).grid(column=1, row=x + 2, sticky=NSEW)
        elif field == "Event_Year":
            # run through the shapefile and pick out unique values
            for x, y in enumerate(spatialdata["Event_Year"]):
                if y not in uniquetable:
                    uniquetable[y] = counter
                    counter = counter + 1
            # run through the error table, create a new row for each error
            for x, y in enumerate(uniquetable):
                # get the current code for this row
                # if in the list of missing then create the label with the options
                ttk.Label(repairPOSfieldsTL, anchor="center", text=y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
                ttk.Combobox(repairPOSfieldsTL, state="normal", values=["%s" % int(time.strftime("%Y"))]).grid(column=1, row=x + 2, sticky=NSEW)
        elif field == "TaxonID":
            # run through the shapefile and pick out unique values
            for x, y in enumerate(spatialdata["TaxonID"]):
                if y not in uniquetable:
                    uniquetable[y] = counter
                    counter = counter + 1
            # run through the error table, create a new row for each error
            for x, y in enumerate(uniquetable):
                # get the current code for this row
                # if in the list of missing then create the label with the options
                ttk.Label(repairPOSfieldsTL, anchor="center", text=y, borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=x + 2, sticky=NSEW)
                ttk.Combobox(repairPOSfieldsTL, state="normal", values=[0]).grid(column=1, row=x + 2, sticky=NSEW)
        else:
            pass

    # finally add the commit button to the bottom
    ttk.Button(repairPOSfieldsTL, text="Commit Changes", command=lambda: commitPOStextchanges(uniquetable, speciesname, field)).grid(column=2, row=20, sticky=NSEW)

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

# display the lat and long errors, and give the drop down options
def repairlongandlat(speciesname, errortable):
    global spatialdata

    # create the toplevel to house everything
    # dimensions of parent window
    x = root.winfo_screenwidth()
    y = root.winfo_screenheight()

    # set the width to the width of the
    repairlongandlatTL = Toplevel()
    repairlongandlatTL.config(background="#DFE8F6")
    repairlongandlatTL.geometry('%dx%d+%d+%d' % (500, 500, x/2 - 250, y/2 - 250))

    # Create the table headers
    ttk.Label(repairlongandlatTL, text="Long Lat Errors", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=0, sticky=NSEW, columnspan=5)
    ttk.Label(repairlongandlatTL, text="Dec_Lat", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=1, sticky=NSEW)
    ttk.Label(repairlongandlatTL, text="Dec_Long", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=1, row=1, sticky=NSEW)
    ttk.Label(repairlongandlatTL, text="Geo_Lat", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=2, row=1, sticky=NSEW)
    ttk.Label(repairlongandlatTL, text="Geo_Long", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=3, row=1, sticky=NSEW)

    # loop through the error table
    for x, y in enumerate(errortable):
        # for each row create four entry boxes
        ttk.Label(repairlongandlatTL, text="Dec_lat", relief="solid", background="#DFE8F6").grid(row=x+2, column=0, sticky=NSEW)
        ttk.Label(repairlongandlatTL, text="Dec_lat", relief="solid", background="#DFE8F6").grid(row=x+2, column=1, sticky=NSEW)
        ttk.Label(repairlongandlatTL, text="Dec_lat", relief="solid", background="#DFE8F6").grid(row=x+2, column=2, sticky=NSEW)
        ttk.Label(repairlongandlatTL, text="Dec_lat", relief="solid", background="#DFE8F6").grid(row=x+2, column=3, sticky=NSEW)
        ttk.Combobox(repairlongandlatTL, state="normal", values=["Option1", "Option2", "Option3"]).grid(row=x+2, column=4)

# Take the exisiting CRS and convert to WGS 84
def changeCRS(speciesname, pointorpoly):
    global spatialdata

    # print the current CRS
    print(spatialdata.crs)

    if pointorpoly == "Polygon":
        try:
            spatialdata = spatialdata.to_crs({'init': 'epsg:4326'})
            # after all changes have occurred then save the file
            savemaptofile(locationofmaps.get(), speciesname)
        except:
            messagebox.showerror(title="An Error Has Occurred", message="Error transforming data")
    else:
        try:
            # concert the CRS if needed
            if spatialdata.crs['init'] != "epsg:4326":
                spatialdata = spatialdata.to_crs({'init': 'epsg:4326'})
            # mark all rows in the SpatialRef column as WGS84
            spatialdata["SpatialRef"] = "WGS84"
            # after all changes have occurred then save the file
            fp = locationofmaps.get()
            spatialdata.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
        except:
            messagebox.showerror(title="An Error Has Occurred", message="Error when transforming data")

    # print the new crs
    print(spatialdata.crs)

    # create the new map
    rownumber = (tablerownumber.get())
    createmapfromscratch("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))

    # destroy the maptests level and rerun
    maptestslevel.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname)

# merges polygons with their duplicate, duplicate based on all attributes except geometry
def mergeidenticalattributes(speciesname):
    global spatialdata

    # run through the list of ones to merge
    columns = list(spatialdata.columns)
    # get the iloc for the new column later
    duplicatemapiloc = len(columns)
    # remove the geometry column from the list to avoid it being used to match on
    columns.remove('geometry')
    # group by duplicates
    grouped = spatialdata.groupby(columns)
    # create a list to store the duplicate map in
    duplicatemap = []
    # create the duplicate maps
    for key, value in grouped.groups.items():
        duplicatemap.append(list(value.values))
    # create a new column marking the duplicates
    spatialdata["duplicatemap"] = 0
    # run through the dataframe using the duplicate map to assign duplicates to the correct group
    for setmarker, map in enumerate(duplicatemap):
        for y in map:
            spatialdata.iloc[y, duplicatemapiloc] = setmarker
    # perform union based on duplicate column
    final = spatialdata.dissolve(by="duplicatemap")
    # save the file
    # get the data from the designated location
    fp = locationofmaps.get()
    # after all changes have occurred then save the file
    final.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
    # create the new map
    rownumber = (tablerownumber.get())
    createtableandaddtomap("%s_%s" % (databasera.iat[rownumber, 1], databasera.iat[rownumber, 2]))
    # destroy the maptests level and rerun
    maptestslevel.destroy()
    # instead of running the whole thing again, remember the f
    maptests(speciesname)

# the shell for the map attributes testing
def maptests(speciesname):
    global maptestslevel
    global spatialdata

    # create the toplevel to house everything
    # position of parent window
    x = root.winfo_x()
    y = root.winfo_y()

    # screen height
    xh = root.winfo_screenheight()

    # size of parent window
    w = reviewassistantframe.winfo_width()
    h = reviewassistantframe.winfo_height()

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

    # get the value of the freshwater stringvar
    freshwater = freshwaterSV.get()

    # test to see if polygon or point tests are required
    # once data has loaded determine whether it is polygon or point
    if spatialdata.geom_type[0] == "Polygon" or spatialdata.geom_type[0] == "MultiPolygon":
        rowcounterpoly = 1
        print("Polygon Data Tests")
        # find out if freshwater species (only needed for polygons)
        if freshwater == "NoValue":
            freshwaterSV.set(messagebox.askyesno(message="Is this species mapped with hydrobasins?"))

        # check to see if already been backed up in pre-edits, if not then save it now
        if os.path.isfile("%s/originalfiles/%s.shp" % (fp, speciesname)) == False:
            savemaptofile(fp, "%s" % speciesname)

        # check that all required fields are present, and identify fields that need to be removed
        checkpoly = checkpolygonfields()
        freshwater = freshwaterSV.get()
        # if any required fields are missing then flag the error
        if len(checkpoly[0]) > 0:
            # check to see if this is a species that should be mapped with hydrobasins or not
            if "BASIN_ID" in checkpoly[0]:
                if freshwater == str(0):
                    # if yes then remove BASIN_ID from the results
                    while "BASIN_ID" in checkpoly[0]: checkpoly[0].remove("BASIN_ID")
                    # recheck length, if still greater than 0 then there multiple required missing so flag error
                    if len(checkpoly[0]) > 0:
                        ttk.Label(maptestslevel, text="Required attribute fields are missing", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                        ttk.Button(maptestslevel, text="Fix", command=lambda: fixrequiredattributes(checkpoly[0], speciesname, "Polygon")).grid(row=rowcounterpoly, column=1)
                        rowcounterpoly = rowcounterpoly + 1
                # if no then flag the message,
                else:
                    ttk.Label(maptestslevel, text="Required attribute fields are missing", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                    ttk.Button(maptestslevel, text="Fix", command=lambda: fixrequiredattributes(checkpoly[0], speciesname, "Polygon")).grid(row=rowcounterpoly, column=1)
                    rowcounterpoly = rowcounterpoly + 1
            else:
                ttk.Label(maptestslevel, text="Required attribute fields are missing", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: fixrequiredattributes(checkpoly[0], speciesname, "Polygon")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1

        # if extra fields present these could be misspelt optional fields
        if len(checkpoly[1]) > 0:
            ttk.Label(maptestslevel, text="Potential misspelt optional fields present", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: fixoptionalattributes(checkpoly[1], speciesname, "Polygon")).grid(row=rowcounterpoly, column=1)
            rowcounterpoly = rowcounterpoly + 1

        # check remaining against the optional, if any non valid attributes then flag this error
        if len(checkpoly[1]) > 0:
            ttk.Label(maptestslevel, text="Non required/optional attributes present", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: dropextrafields(speciesname, "Polygon")).grid(row=rowcounterpoly, column=1)
            rowcounterpoly = rowcounterpoly + 1

        # check the SIS ID column to see if it is correct or not
        SISerrors = checkfield('SISID')
        if len(SISerrors) > 0:
            if SISerrors[0][0] == "SISID Error":
                ttk.Label(maptestslevel, text="SIS Id attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=1, sticky=NSEW)
                rowcounterpoly = rowcounterpoly + 1
            elif SISerrors[0][0] == "SISID Text Error":
                ttk.Label(maptestslevel, text="SIS ID attribute is a text field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: convertandrepairtextPOSfields(speciesname, "ID_NO", "polygon")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1
            else:
                ttk.Label(maptestslevel, text="ID_NO attribute doesn't match SIS ID", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairIDNOfield(speciesname, "Polygon")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1

        # check to see if any errors have been detected in the BINOMIAL column
        binomerrors = checkfield('BINOMIAL')
        if len(binomerrors) > 0:
            if binomerrors[0][0] == "Binomial Error":
                ttk.Label(maptestslevel, text="Binomial attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=1, sticky=NSEW)
                rowcounterpoly = rowcounterpoly + 1
            else:
                ttk.Label(maptestslevel, text="Binomial attribute doesn't match SIS name", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairbinomialfield(speciesname, "Polygon")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1

        # check to see if any errors have been detected in the PRESENCE column
        perrors = checkfield('PRESENCE')
        if len(perrors) > 0:
            if perrors[0][0] == "Presence Error":
                ttk.Label(maptestslevel, text="Presence attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=1, sticky=NSEW)
                rowcounterpoly = rowcounterpoly + 1
            elif perrors[0][0] == "Presence Text Error":
                ttk.Label(maptestslevel, text="Presence attribute is a text field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: convertandrepairtextPOSfields(speciesname, "PRESENCE", "polygon")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1
            else:
                ttk.Label(maptestslevel, text="Presence code error detected", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(speciesname, perrors, "presence")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1

        # check to see if any errors have been detected in the ORIGIN column
        oerrors = checkfield('ORIGIN')
        if len(oerrors) > 0:
            if oerrors[0][0] == "Origin Error":
                ttk.Label(maptestslevel, text="Origin attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=1, sticky=NSEW)
                rowcounterpoly = rowcounterpoly + 1
            elif oerrors[0][0] == "Origin Text Error":
                ttk.Label(maptestslevel, text="Origin attribute is a text field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: convertandrepairtextPOSfields(speciesname, "ORIGIN", "polygon")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1
            else:
                ttk.Label(maptestslevel, text="Origin code error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(speciesname, oerrors, "origin")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1

        # check to see if any errors have been detected in the SEASONAL column
        serrors = checkfield('SEASONAL')
        if len(serrors) > 0:
            if serrors[0][0] == "Seasonal Error":
                ttk.Label(maptestslevel, text="Seasonal attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=1, sticky=NSEW)
                rowcounterpoly = rowcounterpoly + 1
            elif serrors[0][0] == "Seasonal Text Error":
                ttk.Label(maptestslevel, text="Seasonal attribute is a text field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: convertandrepairtextPOSfields(speciesname, "SEASONAL", "polygon")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1
            else:
                ttk.Label(maptestslevel, text="Seasonal code error detected", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(speciesname, serrors, "seasonal")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1

        # check to see if any duplicate rows exist
        try:
            test = spatialdata.copy(deep=True)
            test.drop("geometry", axis=1, inplace=True)
            if sum(test.duplicated(keep=False)) != 0:
                ttk.Label(maptestslevel, text="Identical rows found", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Merge", command=lambda: mergeidenticalattributes(speciesname)).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1
        except:
            ttk.Label(maptestslevel, text="Identical row checking error ", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
            ttk.Label(maptestslevel, text="Try again later", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=1, sticky=NSEW)
            rowcounterpoly = rowcounterpoly + 1

        # check to see if any errors have been detected in the COMPILER column
        cerrors = checkfield('COMPILER')
        if len(cerrors) > 0:
            if cerrors[0][0] == "Compiler Error":
                ttk.Label(maptestslevel, text="Compiler attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=1, sticky=NSEW)
                rowcounterpoly = rowcounterpoly + 1
            else:
                ttk.Label(maptestslevel, text="Compiler code error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(speciesname, cerrors, "compiler")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1

        # check to see if any errors have been detected in the COMPILER column
        yerrors = checkfield('YEAR')
        if len(yerrors) > 0:
            if yerrors[0][0] == "Year Error":
                ttk.Label(maptestslevel, text="Year attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=1, sticky=NSEW)
                rowcounterpoly = rowcounterpoly + 1
            elif yerrors[0][0] == "Year Text Error":
                ttk.Label(maptestslevel, text="Year attribute is a text field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: convertandrepairtextPOSfields(speciesname, "YEAR", "polygon")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1
            else:
                ttk.Label(maptestslevel, text="Year attribute error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(speciesname, yerrors, "year")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1

        # check to see if any errors have been detected in the COMPILER column
        citerrors = checkfield('CITATION')
        if len(citerrors) > 0:
            if citerrors[0][0] == "Citation Error":
                ttk.Label(maptestslevel, text="Citation attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=1, sticky=NSEW)
                rowcounterpoly = rowcounterpoly + 1
            else:
                ttk.Label(maptestslevel, text="Citation attribute error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repaircitationfield(speciesname, "Polygon")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1

        # check that the projection system being used is correct
        if spatialdata.crs['init'] != "epsg:4326":
            ttk.Label(maptestslevel, text="Coordinate Reference System Error", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: changeCRS(speciesname, "Polygon")).grid(row=rowcounterpoly, column=1)
            rowcounterpoly = rowcounterpoly + 1

        # if no attribute errors (i.e. all required present, and all extra removed) check the order
        if len(checkpoly[0]) == 0 and len(checkpoly[1]) == 0:
            if checkattributeorder("Polygon") == False:
                ttk.Label(maptestslevel, text="Attributes in Wrong Order", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: reorganiseattributes(speciesname, "Polygon")).grid(row=rowcounterpoly, column=1)
                rowcounterpoly = rowcounterpoly + 1
        else:
            ttk.Label(maptestslevel, text="Can't check order at the moment", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW)
            ttk.Label(maptestslevel, text="N/A", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=1,sticky=NSEW)
            rowcounterpoly = rowcounterpoly + 1

        # check to see if rownumber is equal to the number of tests (i.e. all have passed, in which case all tets passed result
        if rowcounterpoly == 1:
            ttk.Label(maptestslevel, text="All Spatial Tests Passed", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounterpoly, column=0, sticky=NSEW, columnspan=2)

        # give weight to the rows and column
        maptestslevel.columnconfigure((0, 1), weight=1)
        maptestslevel.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)

        # fill the remaing space
        for child in maptestslevel.winfo_children():
            child.grid_configure(padx=5, pady=2)
    # else run the point data tests
    else:
        # create point map
        print("Point Data Tests")
        rowcounter = 1

        # check to see if already been backed up in pre-edits, if not then save it now
        if os.path.isfile("%s/originalfiles/%s.shp" % (fp, speciesname)) == False:
            savemaptofile(fp, "%s" % speciesname)

        # check that all required fields are present, and identify fields that need to be removed
        checkpoint = checkpointfields()
        # if any required fields are missing if yes then prompt fix function
        if len(checkpoint[0]) > 0:
            ttk.Label(maptestslevel, text="Required attribute fields are missing", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: fixrequiredattributes(checkpoint[0], speciesname, "point")).grid(row=rowcounter, column=1)
            rowcounter = rowcounter + 1

        # if extra fields present these could be misspelt optional fields
        if len(checkpoint[1]) > 0:
            ttk.Label(maptestslevel, text="Potential misspelt optional fields present", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: fixoptionalattributes(checkpoint[1], speciesname, "Point")).grid(row=rowcounter, column=1)
            rowcounter = rowcounter + 1

        # check to see if any optional variables are present, if any non valid attributes then flag this error
        if len(checkpoint[1]) > 0:
            ttk.Label(maptestslevel, text="Non required/optional attributes present", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: dropextrafields(speciesname, "Point")).grid(row=rowcounter, column=1)
            rowcounter = rowcounter + 1

        # check the SIS ID column to see if it is correct or not
        SISerrors = checkfieldpoints('SISID')
        if len(SISerrors) > 0:
            if SISerrors[0][0] == "SISID Error":
                ttk.Label(maptestslevel, text="SIS Id attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=1, sticky=NSEW)
                rowcounter = rowcounter + 1
            elif SISerrors[0][0] == "SISID Text Error":
                ttk.Label(maptestslevel, text="TaxonID attribute is a text field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: convertandrepairtextPOSfields(speciesname, "TaxonID", "point")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1
            else:
                ttk.Label(maptestslevel, text="ID_NO attribute doesn't match SIS ID", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairIDNOfield(speciesname, "Point")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1

        # check to see if any errors have been detected in the BINOMIAL column
        binomerrors = checkfieldpoints('BINOMIAL')
        if len(binomerrors) > 0:
            if binomerrors[0][0] == "Binomial Error":
                ttk.Label(maptestslevel, text="Binomial attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=1, sticky=NSEW)
                rowcounter = rowcounter + 1
            else:
                ttk.Label(maptestslevel, text="Binomial attribute doesn't match SIS name", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairbinomialfield(speciesname, "Point")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1

        # check to see if any errors have been detected in the PRESENCE column
        perrors = checkfieldpoints('PRESENCE')
        if len(perrors) > 0:
            if perrors[0][0] == "Presence Error":
                ttk.Label(maptestslevel, text="Presence attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=1, sticky=NSEW)
                rowcounter = rowcounter + 1
            elif perrors[0][0] == "Presence Text Error":
                ttk.Label(maptestslevel, text="Presence attribute is a text field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: convertandrepairtextPOSfields(speciesname, "Presence", "point")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1
            else:
                ttk.Label(maptestslevel, text="Presence code error detected", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(speciesname, perrors, "presence")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1

        # check to see if any errors have been detected in the ORIGIN column
        oerrors = checkfieldpoints('ORIGIN')
        if len(oerrors) > 0:
            if oerrors[0][0] == "Origin Error":
                ttk.Label(maptestslevel, text="Origin attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=1, sticky=NSEW)
                rowcounter = rowcounter + 1
            elif oerrors[0][0] == "Origin Text Error":
                ttk.Label(maptestslevel, text="Origin attribute is a text field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: convertandrepairtextPOSfields(speciesname, "Origin", "point")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1
            else:
                ttk.Label(maptestslevel, text="Origin code error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(speciesname, oerrors, "origin")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1

        # check to see if any errors have been detected in the SEASONAL column
        serrors = checkfieldpoints('SEASONAL')
        if len(serrors) > 0:
            if serrors[0][0] == "Seasonal Error":
                ttk.Label(maptestslevel, text="Seasonal attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=1, sticky=NSEW)
                rowcounter = rowcounter + 1
            elif serrors[0][0] == "Seasonal Text Error":
                ttk.Label(maptestslevel, text="Seasonal attribute is a text field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: convertandrepairtextPOSfields(speciesname, "Seasonal", "point")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1
            else:
                ttk.Label(maptestslevel, text="Seasonal code error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(speciesname, serrors, "seasonal")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1

        # check to see if any errors have been detected in the COMPILER column
        cerrors = checkfieldpoints('COMPILER')
        if len(cerrors) > 0:
            if cerrors[0][0] == "Compiler Error":
                ttk.Label(maptestslevel, text="Compiler attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=1, sticky=NSEW)
                rowcounter = rowcounter + 1
            else:
                ttk.Label(maptestslevel, text="Compiler code error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(speciesname, cerrors, "compiler")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1

        # check to see if any errors have been detected in the COMPILER column
        yerrors = checkfieldpoints('YEAR')
        if len(yerrors) > 0:
            if yerrors[0][0] == "Year Error":
                ttk.Label(maptestslevel, text="Year attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=1, sticky=NSEW)
                rowcounter = rowcounter + 1
            elif yerrors[0][0] == "Year Text Error":
                ttk.Label(maptestslevel, text="Year attribute is a text field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: convertandrepairtextPOSfields(speciesname, "Year", "point")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1
            else:
                ttk.Label(maptestslevel, text="Year attribute error detected", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(speciesname, yerrors, "year")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1

        # check to see if any errors have been detected in the COMPILER column
        citerrors = checkfieldpoints('CITATION')
        if len(citerrors) > 0:
            if citerrors[0][0] == "Citation Error":
                ttk.Label(maptestslevel, text="Citation attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=1, sticky=NSEW)
                rowcounter = rowcounter + 1
            else:
                ttk.Label(maptestslevel, text="Citation attribute error detected", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repaircitationfield(speciesname, "Point")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1

        # check to see if any errors that have been detected in the Event_Year column
        eyerrors = checkfieldpoints('Event Year')
        if len(eyerrors) > 0:
            if eyerrors[0][0] == "Event_Year Error":
                ttk.Label(maptestslevel, text="Event Year attribute absent or mispelled", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=1, sticky=NSEW)
                rowcounter = rowcounter + 1
            elif eyerrors[0][0] == "Event_Year Text Error":
                ttk.Label(maptestslevel, text="Event Year attribute is a text field", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: convertandrepairtextPOSfields(speciesname, "Event_Year", "point")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1
            else:
                ttk.Label(maptestslevel, text="Event_Year error detected", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairPOSfields(speciesname, eyerrors, "Event_Year")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1

        # check that the projection system being used is correct
        if spatialdata.crs['init'] != "epsg:4326":
            ttk.Label(maptestslevel, text="Coordinate Reference System Error", background="#DFE8F6", borderwidth=3,relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
            ttk.Button(maptestslevel, text="Fix", command=lambda: changeCRS(speciesname, freshwater, "Point")).grid(row=rowcounter, column=1)
            rowcounter = rowcounter + 1

        # check that the SpatialRef column says the right thing
        SpatialReferrors = checkfieldpoints("SpatialRef")
        if len(SpatialReferrors) > 0:
            if SpatialReferrors[0][0] == "SpatialRef Error":
                ttk.Label(maptestslevel, text="SpatialRef attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid( row=rowcounter, column=1, sticky=NSEW)
                rowcounter = rowcounter + 1
            else:
                ttk.Label(maptestslevel, text="SpatialRef error detected", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: changeCRS(speciesname, "Point")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1

        # check to see if any errors in lat or long
        latlongerrors = checkfieldpoints("Invalidlatorlong")
        if len(SpatialReferrors) > 0:
            if latlongerrors[0][0] == "Invalidlatorlong Error":
                ttk.Label(maptestslevel, text="SpatialRef attribute absent or mispelled", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Label(maptestslevel, text="Field Required", background="#DFE8F6", borderwidth=3, relief="solid").grid( row=rowcounter, column=1, sticky=NSEW)
                rowcounter = rowcounter + 1
            else:
                ttk.Label(maptestslevel, text="Lat/Long errors detected", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: repairlongandlat(speciesname, latlongerrors)).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1

        # if no attribute errors (i.e. all required present, and all extra removed) check the order
        if len(checkpoint[0]) == 0 and len(checkpoint[1]) == 0:
            if checkattributeorder("Point") == False:
                ttk.Label(maptestslevel, text="Attributes in Wrong Order", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
                ttk.Button(maptestslevel, text="Fix", command=lambda: reorganiseattributes(speciesname, "Point")).grid(row=rowcounter, column=1)
                rowcounter = rowcounter + 1
        else:
            ttk.Label(maptestslevel, text="Can't check order at the moment", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW)
            ttk.Label(maptestslevel, text="N/A", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=1,sticky=NSEW)
            rowcounter = rowcounter + 1

        # check to see if rownumber is equal to the number of tests (i.e. all have passed, in which case all tets passed result
        if rowcounter == 1:
            ttk.Label(maptestslevel, text="All Spatial Tests Passed", background="#DFE8F6", borderwidth=3, relief="solid").grid(row=rowcounter, column=0, sticky=NSEW, columnspan=2)

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
    binomial = databasera.iat[rownumber, 1]
    binomialnospace = binomial.replace(" ", "_")

    if mapengineactive.get() == 0:
        # visual stuff to show loading
        mapenginetext.set("Loading...")
        root.update()
        # set the tracking variable to show that the mapengine is running
        mapengineactive.set(1)
        # create map for species, overwrite if already there
        if createmapfromscratch("%s" % binomialnospace) == 1:
            messagebox.showerror(title="Mysterious Rubber Duck", message="No map for this species could be found")
            mapenginetext.set("Stop Maps")
            return 0
        # create the map driver itself
        webbrowser.open("%s\\SpatialDataStore\\%s.html" % (filedir, binomialnospace), new=0)
        # then run the map checks required
        maptests("%s" % binomialnospace)
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
    global loggedin

    # first check if logged in globally, if not then login in via the validate function
    if loggedin == 0:
        currenturl = driver.current_url
        assessmentid = 4224
        driver.execute_script("window.open('http://%s:%s@sis.iucnsis.org/apps/org.iucn.sis.server.extensions.integrity/validate?id=%s&type=submitted_status')" % (usernamevariable, passwordvariable, assessmentid))
        driver.switch_to.window(driver.window_handles[1])
        try:
            element = WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'Click here to view')]")))
        finally:
            element.click()
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            loggedin = 1

    driver.find_element_by_xpath("//*[contains(text(), 'Attachments')]").click()
    driver.find_element_by_xpath("//*[contains(text(), 'Manage Attachments')]").click()
    driver.implicitly_wait(0.5)

    try:
        # find and click the ok button
        driver.find_element_by_xpath("//*[contains(text(), 'There are no attachments for this assessment.')]").find_element_by_xpath("//*[contains(text(), 'OK')]").click()
        messagebox.showinfo("Notification", "No Attachment found")
    except:
        llama = messagebox.askyesno(title="Notification", message="Attachment found, do you want to download it?", icon='question')
        listofdownloads = driver.find_elements_by_css_selector(".x-grid3-col.x-grid3-cell.x-grid3-td-publish")
        listofparents = []
        for x in listofdownloads:
            listofparents.append(x.find_element_by_xpath(".."))

        # for each row of the attachments file
        for x in listofparents:
            # check to see if the name contains a spatial data folder (testing for .geocat, .kml)
            if ".geocat" in list(x.text.splitlines())[0] or ".kml" in list(x.text.splitlines())[0]:
                print("Spatial File Found")
                # bring focus to the row
                x.click()
                # press download (need to change the default download location to the correct folder)
                driver.find_element_by_xpath("//*[contains(text(), 'Download')]").click()
                # close the attachements window

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
        messagebox.showinfo("Notification", "Template has been generated")

    except:
        messagebox.showerror("An Error Has Occurred", "Template has not been generated, please try again")

# event handler for when the user chooses the assessment they want to go to.
def gotooption(event):
    global dspchoice
    driver.implicitly_wait(2)
    # go to the option selected from the combo box
    actionChains = ActionChains(driver)
    actionChains.double_click(driver.find_element_by_xpath("//*[contains(text(), '%s')]" % assessmentvar.get())).perform()

    # hide the selection menu
    dspchoice.destroy()

# takes the provided shapefile and returns the area of the MCP around all data marked as Presence = 1 (cea projected)
def calculateeoobymcp(shapefile, pointorpoly):
    # create copy so as to not destroy the original
    copiedtable = copy.deepcopy(shapefile)

    if pointorpoly == "polygon":
        try:
            # define the equal area projection
            equalarea = {'proj': 'cea', 'lon_0': 0, 'lat_ts': 0, 'x_0': 0, 'y_0': 0, 'datum': 'WGS84', 'units': 'm', 'no_defs': True}

            # get the number of polygons
            nrofpoly = len(copiedtable)

            # go through and drop any polygons that don't have PRESENCE 1
            for x in range(0, nrofpoly):
                if copiedtable.loc[x, "PRESENCE"] != 1:
                    copiedtable.drop(x, axis=0, inplace=True)

            # calculate and report the area of the polygon
            rawdatatransform = copiedtable.to_crs(equalarea)

            final = rawdatatransform.dissolve(by="PRESENCE")

            mcp = final.convex_hull

            return "{} km²".format(float(round(mcp.area/10**6, 2)))
        except:
            return "EOO Couldn't be calculated"
    else:
        try:
            # define the equal area projection
            equalarea = {'proj': 'cea', 'lon_0': 0, 'lat_ts': 0, 'x_0': 0, 'y_0': 0, 'datum': 'WGS84', 'units': 'm', 'no_defs': True}

            # get the number of polygons
            nrofpoly = len(copiedtable)

            # go through and drop any polygons that don't have PRESENCE 1
            for x in range(0, nrofpoly):
                if copiedtable.loc[x, "Presence"] != 1:
                    copiedtable.drop(x, axis=0, inplace=True)

            # calculate and report the area of the polygon
            rawdatatransform = copiedtable.to_crs(equalarea)

            #final = rawdatatransform.dissolve(by="Presence")

            #mcp = final.convex_hull

            mcp = rawdatatransform.convex_hull

            return str("{} km²".format(float(round(mcp.area/10**6, 2))))
        except:
            return "EOO Couldn't be calculated"

# reads in a geocat file and converts into a ESRI shapefile
def convertGEOCAT(geocatfile):
    # the list of attributes to be searched
    attributestosearchfor = ["coordinateUncertaintyInMeters", "collector", "eventDate", "occurrenceRemarks", "latitude", "longitude", "collectionCode", "catalogNumber", "basisOfRecord", "country", "presence", "scientificName", "locality", "seasonal", "origin", "occurrenceDetails", "data_sens", "sens_comm", "compiler", "yrcompiled", "verbatimElevation"]

    # create a blank pandas data frame with the correct column names
    pointsdata = pandas.DataFrame(columns=["TaxonID"])
    pointsdata["TaxonID"] = 0

    # open the geopandas dataframe
    opentemp = open(geocatfile, "r", encoding='UTF-8')

    # read them into memory
    contents = opentemp.read()

    # get read of the head information only interested in information after the "points" section
    # try to split on analysis (if they have used geocat to calcuate AOO/EOO)
    try:
        stepone = contents.split(sep="analysis")[0]
    except:
        stepone = contents

    # user points are stored separatly to the GBIF points
    sourcelist = stepone.split(sep="points")
    # delete the header
    del sourcelist[0]

    # if the length of the list is 1, then just user information has been provided, greater than one means that GBIF data etc is included
    for source in sourcelist:
        # split the points section into data for each point (searching for everything between { and }
        individualspoints = re.findall('{(.+?)}', source)
        # for each point
        for x in individualspoints:
            key = []
            value = []
            # try and find each attribute, if found then add the key and value to the key or value libary
            for variable in attributestosearchfor:
                if variable == "coordinateUncertaintyInMeters":
                    try:
                        temp = re.search('coordinateUncertaintyInMeters":(.+?),', x).group(1)
                        if temp == "\"\"":
                            value.append(None)
                        else:
                            value.append(temp.strip("\""))
                        key.append("coordinateUncertaintyInMeters")
                    except AttributeError:
                        pass
                else:
                    try:
                        temp = re.search('%s":(.+?),' % variable, x).group(1)
                        if temp == "\"\"":
                            value.append(None)
                        else:
                            value.append(temp.strip("\""))
                        key.append(variable)
                    except AttributeError:
                        pass

            dictionary = dict(zip(key, value))

            # create a series from the dictionary
            tempdata = pandas.Series(dictionary)

            pointsdata = pointsdata.append(tempdata, ignore_index=True)

    # wiperth the data in a dataframe format, now do the first stage rough tidying up of data
    # create the dictionary to map geocat attributes to IUCN standards
    conversiondictionary = {"coordinateUncertaintyInMeters": "coordUncert", "collector": "recordedBy", "eventDate": "Event_Year", "latitude": "Dec_Lat", "longitude": "Dec_Long", "collectionCode": "collectID", "catalogNumber": "CatalogNo", "basisOfRecord": "BasisOfRec", "country": "countryCode", "presence": "Presence", "scientificName": "Binomial", "seasonal": "Seasonal", "origin": "Origin", "occurrenceDetails": "Source", "data_sens": "Data_sens", "sens_comm": "Sens_comm", "compiler": "Compiler", "yrcompiled": "Year"}
    presencemap = {"Extant": 1, "Probably Extant": 2, "Possibly Extant": 3, "Possibly Extinct": 4, "Extinct": 5, "Presence Uncertain": 6}
    originmap = {"Native": 1, "Reintroduced": 2, "Introduced": 3, "Vagrant": 4, "Origin Uncertain": 5, "Assisted Colonisation": 6}
    seasonalmap = {"Resident": 1, "Breeding Season": 2, "Non-breeding Season": 3, "Passage": 4, "Seasonal Occurrence Uncertain": 5}

    # run through and map the geocat variables to the IUCN point standards
    for x in pointsdata:
        try:
            if x in ("latitude", "longitude"):
                pointsdata[conversiondictionary[x]] = pointsdata[x].astype('float64')
                pointsdata.drop(x, axis=1, inplace=True)
            elif x in ("TaxonID", "coordUncer"):
                pointsdata[conversiondictionary[x]] = pointsdata[x].astype('int64')
                pointsdata.drop(x, axis=1, inplace=True)
            elif x == "presence":
                for row, y in enumerate(pointsdata["presence"]):
                    try:
                        pointsdata.at[row, "Presence"] = int(presencemap[y])
                    except:
                        pointsdata.at[row, "Presence"] = 0
                pointsdata["Presence"] = pointsdata["Presence"].astype("int32")
                pointsdata.drop(x, axis=1, inplace=True)
            elif x == "origin":
                for row, y in enumerate(pointsdata["origin"]):
                    try:
                        pointsdata.at[row, "Origin"] = int(originmap[y])
                    except:
                        pointsdata.at[row, "Origin"] = 0
                pointsdata["Origin"] = pointsdata["Origin"].astype("int32")
                pointsdata.drop(x, axis=1, inplace=True)
            elif x == "seasonal":
                for row, y in enumerate(pointsdata["seasonal"]):
                    try:
                        pointsdata.at[row, "Seasonal"] = int(seasonalmap[y])
                    except:
                        pointsdata.at[row, "Seasonal"] = 0
                pointsdata["Seasonal"] = pointsdata["Seasonal"].astype("int32")
                pointsdata.drop(x, axis=1, inplace=True)
            elif x in ("occurrenceRemarks", "catalogue_id", "institutionCode", "collectorNumber", "stateProvince", "county", "interpretedFrom", "identifiedBy"):
                pointsdata.drop(x, axis=1, inplace=True)
            elif x in "verbatimElevation":
                pointsdata["maxElev"] = pointsdata[x]
                pointsdata["minElev"] = pointsdata[x]
                pointsdata.drop(x, axis=1, inplace=True)
            else:
                pointsdata[conversiondictionary[x]] = pointsdata[x]
                pointsdata.drop(x, axis=1, inplace=True)
        except:
            pass

    # convert from pandas into geopandas format
    geometry = [Point(xy) for xy in zip(pointsdata.Dec_Long, pointsdata.Dec_Lat)]
    crs = {'init': 'epsg:4326'}
    gdf = GeoDataFrame(pointsdata, crs=crs, geometry=geometry)

    return gdf

# change the CSV columns to the correct names and then convert to geopandas
def inportandcovert(csvfile, speciesname):
    global spatialdata
    # create dictionary to store all conversions
    try:
        conversiontable = []
        for counter, combobox in enumerate(CSVdetails.children.values()):
            if 'combobox' in str(combobox):
                conversiontable.append(combobox.get())

        # test to see if any are Not Present
        if conversiontable[0] == "Not Present":
            messagebox.showerror(title="An Error Has Occurred", message="No Dec_Lat column defined, define to continue")
        if conversiontable[1] == "Not Present":
            messagebox.showerror(title="An Error Has Occurred", message="No Dec_Long column defined, define to continue")
        if conversiontable[2] == "Not Present":
            messagebox.showerror(title="An Error Has Occurred", message="No CRS definined, creating and defaulting to WGS84")
            csvfile["SpatialRef"] = "WGS84"
            conversiontable[2] = "SpatialRef"

        # if already corect then don't rename column
        if conversiontable[0] != "Dec_Lat":
            csvfile["Dec_Lat"] = csvfile[conversiontable[0]]
            csvfile.drop("%s" % conversiontable[0], axis=1, inplace=True)
        if conversiontable[1] != "Dec_Long":
            csvfile["Dec_Long"] = csvfile[conversiontable[1]]
            csvfile.drop("%s" % conversiontable[1], axis=1, inplace=True)
        if conversiontable[2] != "SpatialRef":
            csvfile["SpatialRef"] = csvfile[conversiontable[2]]
            csvfile.drop("%s" % conversiontable[2], axis=1, inplace=True)

        # look into the CRS, if not WGS84 raise box asking for what the EPSG code is
        if csvfile["SpatialRef"][0] == "WGS84" or csvfile["SpatialRef"][0] == "WGS 84":
            crs = {'init': 'epsg:4326'}
        else:
            crsdefine = simpledialog.askstring("CRS Define", "Four digit EPSG code required type CRS into (http://epsg.io/)")
            crs = {'init': 'epsg:%s' % crsdefine}

        # check the POS columns to make sure valid input,
        geometry = [Point(xy) for xy in zip(csvfile.Dec_Long, csvfile.Dec_Lat)]
        crs = {'init': 'epsg:4326'}
        spatialdata = GeoDataFrame(csvfile, crs=crs, geometry=geometry)

        # if crs is not WGS 84 then convert the points
        if crs != {'init': 'epsg:4326'}:
            print("Data supplied is not in WGS84 reprojecting...")
            spatialdata = spatialdata.to_crs({'init': 'epsg:4326'})

        # destroy topwindow
        CSVdetails.destroy()
    except:
        print("Error in convering CSV to ESRI feature class")
        messagebox.showerror(title="An Error Has Occurred", message="Error in CSV to feature class conversion")
        return 1

# reads in csv file and coverts into a ESRI shapefile
def convertCSV(csvfile, speciesname):
    global CSVdetails
    global spatialdata

    # create the outline of the toplevel
    CSVdetails = Toplevel()
    CSVdetails.config(background="#DFE8F6")
    # position of parent window
    x = root.winfo_screenwidth()
    y = root.winfo_screenheight()

    CSVdetails.geometry('%dx%d+%d+%d' % (500, 500, x / 2 - 250, y / 2 - 250))

    # create TopLevel labels
    ttk.Label(CSVdetails, text="CSV Import", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6", anchor=N).grid(column=0, row=0, columnspan=3, sticky=NSEW)
    ttk.Label(CSVdetails, text="Pick Dec_Lat (Y) Column", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=1, columnspan=3, sticky=EW)
    ttk.Label(CSVdetails, text="Pick Dec_Long (X) Column", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=3, columnspan=3, sticky=EW)
    ttk.Label(CSVdetails, text="Pick SpatialRef (if None will assume WGS84)", font=(None, 13, "bold"), borderwidth=3, relief="solid", background="#DFE8F6").grid(column=0, row=5, columnspan=3, sticky=EW)

    # load in the csv into a pandas dataframe
    pandascsvdf = pandas.read_csv(csvfile, encoding='ISO-8859-1')
    # run through and get all headers
    attributenames = []
    attributenames.append("Not Present")
    for x in pandascsvdf:
        attributenames.append(x)

    # present them to user and ask which is the long, lat and CRS column
    Latitude = ttk.Combobox(CSVdetails, state="readonly", values=attributenames)
    Longitude = ttk.Combobox(CSVdetails, state="readonly", values=attributenames)
    CRS = ttk.Combobox(CSVdetails, state="readonly", values=attributenames)

    Latitude.grid(column=0, row=2, columnspan=3, sticky=NSEW)
    Longitude.grid(column=0, row=4, columnspan=3, sticky=NSEW)
    CRS.grid(column=0, row=6, columnspan=3, sticky=NSEW)

    # smart search
    # lat Search
    if "Dec_Lat" in attributenames:
        Latitude.set("Dec_Lat")
    elif "Latitude" in attributenames:
        Latitude.set("Latitude")

    # long search
    if "Dec_Long" in attributenames:
        Longitude.set("Dec_Long")
    elif "Longitude" in attributenames:
        Longitude.set("Longitude")

    # crs search
    if "SpatialRef" in attributenames:
        CRS.set("SpatialRef")
    elif "CRS" in attributenames:
        CRS.set("CRS")

    # run through all columns, if any of type bool then convert
    for x in attributenames:
        try:
            if pandascsvdf[x].dtype == "bool":
                pandascsvdf[x] = pandascsvdf[x] * 1
        except:
            pass

    # Import button (this will trigger the columns to be renamed and will transform the pandas into a geopandas dataframe
    ttk.Button(CSVdetails, text="Import", command=lambda: inportandcovert(pandascsvdf, speciesname)).grid(column=1, row=7, sticky=NSEW)

    # give weight to everything to fill it out
    CSVdetails.columnconfigure((0, 1, 2), weight=1)
    CSVdetails.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

    CSVdetails.wait_window()

# function to create the map for the current species
def createmapfromscratch(speciesname):
    global filedir
    global htmlmapstore
    global spatialdata
    global maptype

    # get the location of the maps from the global variable
    fp = locationofmaps.get()

    # first test to see if shapefile for this species exists if not then word down the list
    # create all the supported versions of the file
    shapefiletest = "%s/%s.shp" % (fp, speciesname)
    geocattestfile = "%s/%s.geocat" % (fp, speciesname)
    csvtestfile = "%s/%s.csv" % (fp, speciesname)

    # check to see if backupfolder exists if not then create it
    if os.path.isdir("%s/originalfiles" % fp) == False:
        os.makedirs("%s/originalfiles" % fp)

    # check to see if shapefilespreediting exists if not then create it
    if os.path.isdir("%s/shapefilespreediting" % fp) == False:
        os.makedirs("%s/shapefilespreediting" % fp)

    if os.path.isfile(shapefiletest):
        # check to see if see if this is in the original files
        if os.path.isfile("%s/shapefilespreediting/%s.shp" % (fp, speciesname)) is False:
            # if yes then check to see if in the preediting files
            shutil.copy("%s/%s.cpg" % (fp, speciesname), "%s/shapefilespreediting/%s.cpg" % (fp, speciesname))
            shutil.copy("%s/%s.dbf" % (fp, speciesname), "%s/shapefilespreediting/%s.dbf" % (fp, speciesname))
            shutil.copy("%s/%s.prj" % (fp, speciesname), "%s/shapefilespreediting/%s.prj" % (fp, speciesname))
            shutil.copy("%s/%s.shp" % (fp, speciesname), "%s/shapefilespreediting/%s.shp" % (fp, speciesname))
            shutil.copy("%s/%s.shx" % (fp, speciesname), "%s/shapefilespreediting/%s.shx" % (fp, speciesname))
            print("Shapefile detected")
            # create the spatial data file
        spatialdata = geopandas.read_file(fp, driver='ESRI Shapefile', layer=speciesname)

    # if shapefile doesn't exist then try to look for a geocat
    elif os.path.isfile(geocattestfile):
        spatialdata = convertGEOCAT(geocattestfile)
        # save the resulting shapefile to file
        spatialdata.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
        # save the resulting shapefile to preedits file
        spatialdata.to_file("%s/shapefilespreediting" % fp, driver='ESRI Shapefile', layer=speciesname)
        # move the geocat to the original files folder
        os.rename(geocattestfile, "%s/originalfiles/%s.geocat" % (fp, speciesname))
        # print success to screen
        print("Geocat file detected and successfully converted")

    # if geocat doesn't exist then check to see if it's a csv
    elif os.path.isfile(csvtestfile):
        # convert the CSV into a shapefile
        convertCSV(csvtestfile, speciesname)
        # save to file
        spatialdata.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
        # save to backupfile
        spatialdata.to_file("%s/shapefilespreediting", driver='ESRI Shapefile', layer=speciesname)
        # move original file to originals folder
        os.rename(csvtestfile, "%s/originalfiles/%s.csv" % (fp, speciesname))
        # print success to screen
        print("CSV file detected and successfully converted")

    # else through a warning that file couldn't be found, and ask user to find
    else:
        messagebox.showerror(title="An Error Has Occurred", message="Shapefile for this species could not be found, please select manually")
        # open the file dialogue and ask user to find the correct file
        newname = filedialog.askopenfilename(filetypes=[("All files","*.*"),("Shapefile files", "*.shp"),("Geocat files", "*.geocat"),("csv files", "*.csv")])
        if newname == "":
            return 1
        # take the new name
        actualfilenamelist = newname.split("/")
        actualfilename = "text"
        for part in actualfilenamelist:
            if ".shp" in part:
                actualfilename = part.replace(".shp","")
            elif ".geocat" in part:
                actualfilename = part.replace(".geocat","")
            elif ".csv" in part:
                actualfilename = part.replace(".csv","")

        shapefiletest = "%s/%s.shp" % (fp, actualfilename)
        geocattestfile = "%s/%s.geocat" % (fp, actualfilename)
        csvtestfile = "%s/%s.csv" % (fp, actualfilename)

        # test to see what type of file this is
        if os.path.isfile(shapefiletest):
            # copy the original to the originalfiles folder
            shutil.copy("%s/%s.cpg" % (fp, actualfilename), "%s/originalfiles/%s.cpg" % (fp, actualfilename))
            shutil.copy("%s/%s.dbf" % (fp, actualfilename), "%s/originalfiles/%s.dbf" % (fp, actualfilename))
            shutil.copy("%s/%s.prj" % (fp, actualfilename), "%s/originalfiles/%s.prj" % (fp, actualfilename))
            shutil.copy("%s/%s.shp" % (fp, actualfilename), "%s/originalfiles/%s.shp" % (fp, actualfilename))
            shutil.copy("%s/%s.shx" % (fp, actualfilename), "%s/originalfiles/%s.shx" % (fp, actualfilename))
            print("Shapefile detected")

            # rename the file within the folder
            os.rename("%s/%s.cpg" % (fp, actualfilename), "%s/%s.cpg" % (fp, speciesname))
            os.rename("%s/%s.dbf" % (fp, actualfilename), "%s/%s.dbf" % (fp, speciesname))
            os.rename("%s/%s.prj" % (fp, actualfilename), "%s/%s.prj" % (fp, speciesname))
            os.rename("%s/%s.shp" % (fp, actualfilename), "%s/%s.shp" % (fp, speciesname))
            os.rename("%s/%s.shx" % (fp, actualfilename), "%s/%s.shx" % (fp, speciesname))

            # copy this to pre-edit location
            shutil.copy("%s/%s.cpg" % (fp, speciesname), "%s/shapefilespreediting/%s.cpg" % (fp, speciesname))
            shutil.copy("%s/%s.dbf" % (fp, speciesname), "%s/shapefilespreediting/%s.dbf" % (fp, speciesname))
            shutil.copy("%s/%s.prj" % (fp, speciesname), "%s/shapefilespreediting/%s.prj" % (fp, speciesname))
            shutil.copy("%s/%s.shp" % (fp, speciesname), "%s/shapefilespreediting/%s.shp" % (fp, speciesname))
            shutil.copy("%s/%s.shx" % (fp, speciesname), "%s/shapefilespreediting/%s.shx" % (fp, speciesname))

            # create the spatial data file
            spatialdata = geopandas.read_file(fp, driver='ESRI Shapefile', layer=speciesname)

        # if shapefile doesn't exist then try to look for a geocat
        elif os.path.isfile(geocattestfile):
            spatialdata = convertGEOCAT(geocattestfile)
            # save the resulting shapefile to file
            spatialdata.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
            # save to backup
            spatialdata.to_file("%s/shapefilespreediting" % fp, driver='ESRI Shapefile', layer=speciesname)
            # move the original file to the originals folder
            os.rename(geocattestfile, "%s/originalfiles/%s.geocat" % (fp, actualfilename))
            # print success to screen
            print("Geocat file detected and successfully converted")

        elif os.path.isfile(csvtestfile):
            convertCSV(csvtestfile, actualfilename)
            # save to file
            spatialdata.to_file(fp, driver='ESRI Shapefile', layer=speciesname)
            # save to backup
            spatialdata.to_file("%s/shapefilespreediting" % fp, driver='ESRI Shapefile', layer=speciesname)
            # move original file to originals folder
            os.rename("%s/%s.csv" % (fp, actualfilename), "%s/originalfiles/%s.csv" % (fp, actualfilename))
            # print success to screen
            print("CSV file detected and successfully converted")

        # delete the old files
        for file in os.listdir(fp):
            if actualfilename == file.split(".")[0]:
                os.remove("%s/%s" % (fp, file))

    # create map object
    maporiginal = folium.Map([0, 0], tiles='Stamen Terrain')
    # set the default zoom to the current extent of the map
    bounds = spatialdata.total_bounds
    maporiginal.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    attributelist = []
    for attributename in spatialdata:
        attributelist.append(attributename)

    # with data in geopandas database now check to see if you have polygon or point data (as different methods)
    if spatialdata.geom_type[0] == "Polygon" or spatialdata.geom_type[0] == "MultiPolygon":
        print("Polygon Data")
        # unique part of creating a polygon map
        # transform the data into a json format for the folium engine
        jsondata = spatialdata.to_json()
        # screen data to ensure that the POS fields are in there correctly to allow styling on them to occur, if any aren't then map without style
        # create list of all attribues

        # then test to see if all are in there
        if "PRESENCE" in attributelist and "ORIGIN" in attributelist and "SEASONAL" in attributelist:
            polygon = folium.features.GeoJson(jsondata, style_function=lambda feature: {'fillColor': '#ff0000' if feature['properties']['PRESENCE'] == 1 else '#ff9d00' if feature['properties']['PRESENCE'] == 2 else '#fffa00' if feature['properties']['PRESENCE'] == 3 else '#37ff00' if feature['properties']['PRESENCE'] == 4 else '#003fff' if feature['properties']['PRESENCE'] == 5 else '#e900ff', 'color': '#ff0000' if feature['properties']['ORIGIN'] == 1 else '#ff9d00' if feature['properties']['ORIGIN'] == 2 else '#fffa00' if feature['properties']['ORIGIN'] == 3 else '#37ff00' if feature['properties']['ORIGIN'] == 4 else '#003fff' if feature['properties']['ORIGIN'] == 5 else '#e900ff', 'fillOpacity': '0.6'})
        else:
            polygon = folium.features.GeoJson(jsondata)

        maporiginal.add_child(polygon)
    else:
        print("Point Data")
        # unique part of creating a point map
        # create colour dictionary for the point markers
        presencestyledict = ["red", "orange", "yellow", "green", "blue", "purple"]
        # loop through each of the points
        for x in range(0, len(spatialdata)):
            # get coordinates, stripping away unnecessary data
            temp = str(spatialdata["geometry"][x])
            temp2 = temp.replace("(", "")
            temp3 = temp2.replace(")", "")
            xy = temp3.split(" ")
            # add to the map
            if "Presence" in attributelist and "Origin" in attributelist and "Seasonal" in attributelist:
                try:
                    folium.Marker([float(xy[2]), float(xy[1])], icon=folium.Icon(color=presencestyledict[spatialdata["Presence"][x]-1], icon="cloud"), popup="P=%s, O=%s, S=%s\n" % (spatialdata["Presence"][x], spatialdata["Origin"][x], spatialdata["Seasonal"][x])).add_to(maporiginal)
                except:
                    folium.Marker([float(xy[2]), float(xy[1])], icon=folium.Icon(color='white'), popup="Invalidily Named POS Fields").add_to(maporiginal)

            else:
                folium.Marker([float(xy[2]), float(xy[1])], icon=folium.Icon(color='white'), popup="Invalidily Named POS Fields").add_to(maporiginal)

    #convert the map into a html string which can be deep copied
    htmlmapstore = maporiginal.get_root().render()

    # create the attribute table for the shapefile via the regeneratemap function
    createtableandaddtomap(speciesname)

# function to regenerate the map for the current species (leaves the map data intact, just recreates the attribute table)
def createtableandaddtomap(speciesname):
    global filedir
    global spatialdata
    global htmlmapstore

    # get the location of the maps from the global variable
    fp = locationofmaps.get()

    mapcopy = copy.deepcopy(htmlmapstore)

    attributelist = []
    for attributename in spatialdata:
        attributelist.append(attributename)

    # convert the attribute table data for this species into a html table for this species
    # first drop the geometry column, for aesthetic purposes
    table = spatialdata.drop("geometry", axis=1)
    # convert table to html format
    table.to_html("%s\\TempFiles\\temptabledata.txt" % filedir, border=0, float_format=lambda x: '%.2f' % x)
    # open up the table outline
    tableoutline = open("%s\\HTMLFiles\\TableOutline.txt" % filedir)
    # open up the html table
    tocopyin = open("%s\\TempFiles\\temptabledata.txt" % filedir)
    # define the stylesheet location for writing
    location = "%s/HTMLFiles/stylesheet.css" % filedir
    # define the location to save the table html
    finalfile = open("%s\\TempFiles\\%s_temp.html" % (filedir, speciesname), "w+")

    # check if the PRESENCE attribute is present and that the data is of the right type if it is then calculate EOO and insert
    if "PRESENCE" in attributelist:
        # check that the PRESENCE column is of type int
        if spatialdata["PRESENCE"].dtype != "int64" or spatialdata["PRESENCE"].dtype != "int32":
            MCP = calculateeoobymcp(spatialdata, "polygon")
        # check that none are 0
        for line in tableoutline:
            finalfile.write(line)
            if 'href=' in line:
                finalfile.write("\"%s\">" % location)
            if '<div class="fixed">' in line:
                for line2 in tocopyin:
                    finalfile.write("%s" % line2)
            if '<div class="EOOCMP">' in line:
                finalfile.write("<p>EOO(MCP) = %s</p>" % MCP)

    elif "Presence" in attributelist:
        if spatialdata["Presence"].dtype != "int64" or spatialdata["Presence"].dtype != "int32":
            MCP = calculateeoobymcp(spatialdata, "point")
        # check that none are 0
        for line in tableoutline:
            finalfile.write(line)
            if 'href=' in line:
                finalfile.write("\"%s\">" % location)
            if '<div class="fixed">' in line:
                for line2 in tocopyin:
                    finalfile.write("%s" % line2)
            if '<div class="EOOCMP">' in line:
                finalfile.write("<p>EOO(MCP) = %s</p>" % MCP)

    # else run through as usual
    else:
        # loop through the html and insert the created html text and the local location of the stylesheet
        for line in tableoutline:
            finalfile.write(line)
            if 'href=' in line:
                finalfile.write("\"%s\">" % location)
            if '<div class="fixed">' in line:
                for line2 in tocopyin:
                    finalfile.write("%s" % line2)
            if '<div class="EOOCMP">' in line:
                finalfile.write("<p>EOO couldn't be calculated</p>")
    # once looped close open files, and tidy up the temp files
    tableoutline.close()
    tocopyin.close()
    finalfile.close()

    os.remove("%s\\TempFiles\\temptabledata.txt" % filedir)

    # run through the html representation of the map
    index = mapcopy.find('<body>')
    with open("%s\\TempFiles\\%s_temp.html" % (filedir, speciesname), "r") as myfile:
        contents = myfile.read().replace('\n', '')
    output = mapcopy[:index] + contents + mapcopy[index:]

    # export the map so that it can be opened by the program
    testing1 = open("%s\\SpatialDataStore\\%s.html" % (filedir, speciesname),"w+")
    testing1.write(output)
    testing1.close()
    # delete the temp file

    os.remove("%s/TempFiles/%s_temp.html" % (filedir, speciesname))

# prototype function to allow selection of the available assessments on the taxon page
def assessmentlistchooser():
    global dspchoice

    dspchoice = Toplevel()
    dspchoice.config(background="#DFE8F6")

    assessmentvar.set("Click to choose assessment")
    list2 = []

    # set the size and position of the box to appear
    # position of parent window
    x = root.winfo_x()
    y = root.winfo_y()

    # size of parent window
    w = reviewassistantframe.winfo_width()
    h = reviewassistantframe.winfo_height()

    # place the top window
    dspchoice.geometry('%dx%d+%d+%d' % (w/2, h/6, x + w/7, y + h/2))
    dspchoice.resizable(0, 0)

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
    global loggedin

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
            loggedin = 1

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
        messagebox.showinfo("Notification", "Template has been generated")

    except:
        messagebox.showerror("An Error Has Occurred", "Template has not been generated because of some error")

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
            messagebox.showerror("An Error Has Occurred", "Error finding species, try again")
            return 1

        # open taxomatic tools, and open new child taxon
        try:
            driver.find_element_by_xpath("//*[contains(text(), 'Taxomatic Tools')]").click()
            driver.find_element_by_xpath("//*[contains(text(), 'Add New Child Taxon')]").click()
        except:
            messagebox.showerror("An Error Has Occurred", "Error adding new species, try again")
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
            messagebox.showerror("An Error Has Occurred", "Error adding new data to SIS form")
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
            messagebox.showerror("An Error Has Occurred", "Unable to add to working set, manually add")
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
                messagebox.showerror("An Error Has Occurred", "Error searching for name")
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
                messagebox.showerror("An Error Has Occurred", "Unable to attach new reference")
                return 1

        # if it's got this far then all is good, save the species to the database
        try:
            # save the current name, taxonomic authority, taxonomic reference and workingset to the database (as user may have altered)
            databaseta.iat[rownumber, 12] = speciesvalue
            databaseta.iat[rownumber, 16] = taxauthvalue
            databaseta.iat[rownumber, 17] = taxrefvalue
            databaseta.iat[rownumber, 18] = workingsetvalue
            databaseta.iat[rownumber, 21] = int(gettaxonID())
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
            messagebox.showerror("An Error Has Occurred", "Unable to Save to file")
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
            messagebox.showerror("An Error Has Occurred", "Error finding taxlevel, try again")
            return 1

        # open taxomatic tools, and open new child taxon
        try:
            driver.find_element_by_xpath("//*[contains(text(), 'Taxomatic Tools')]").click()
            driver.find_element_by_xpath("//*[contains(text(), 'Add New Child Taxon')]").click()
        except:
            messagebox.showerror("An Error Has Occurred", "Error adding new taxlevel, try again")
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
            messagebox.showerror("An Error Has Occurred", "Error adding new data to SIS form")
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
                messagebox.showerror("An Error Has Occurred", "Error searching for name")
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
                messagebox.showerror("An Error Has Occurred", "Unable to attach new reference")
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
            messagebox.showerror("An Error Has Occurred", "Unable to Save to file")
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
    w = reviewassistantframe.winfo_width()
    h = reviewassistantframe.winfo_height()

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
        w = reviewassistantframe.winfo_width()
        h = reviewassistantframe.winfo_height()

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
def synonymchecker(speciestocheck, level):
    # go back to the homepage
    resetimage = driver.find_element_by_css_selector(".gwt-HTML.x-component.x-border-panel")
    driver.execute_script("arguments[0].click();", resetimage)
    # set implicit wait to 1
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
        # find all search results on this page
        synonymresults = driver.find_elements_by_css_selector(".search_result_taxon_default")
        synonymlevelresults = driver.find_elements_by_css_selector(".x-grid3-cell-inner.x-grid3-col-level")
        # if length 0 list then raise exception and leave
        if len(synonymresults) == 0:
            raise NameError("LlamaNoise")
        for number, x in enumerate(synonymresults):
            if synonymlevelresults[number].text == level:
                testtext = driver.find_elements_by_css_selector(".search_result_taxon_default")[0].text
                driver.find_elements_by_css_selector(".search_result_taxon_default")[0].click()
                return testtext
        raise NameError("LlamaNoise")
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
    time.sleep(1)

# main algorithm for the taxonomy checker
def taxonomychecker(numbertoprocess):
    global databaseta
    global preprocesswindow

    for x in range(0, numbertoprocess):
        rownumber = taxonomyrowtrackerIntVar.get() + x
        try:
            # first search for the genus+species combination
            genusandspecies = searchbyanything("%s %s" % (databaseta.iat[rownumber, 10], databaseta.iat[rownumber, 12]))
            if genusandspecies != 0:
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
                genusandspeciessyn = synonymchecker("%s %s" % (databaseta.iat[rownumber, 10], databaseta.iat[rownumber, 12]), "Species")
                if genusandspeciessyn != 0:
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
                    genusalonessyn = synonymchecker("%s" % (databaseta.iat[rownumber, 10]), "Genus")
                    if genusalonessyn != 0:
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
                familyalonesyn = synonymchecker("%s" % (databaseta.iat[rownumber, 8]), "Family")
                if familyalonesyn != 0:
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
                orderalonesyn = synonymchecker("%s" % (databaseta.iat[rownumber, 6]), "Order")
                if orderalonesyn != 0:
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
                classalonesyn = synonymchecker("%s" % (databaseta.iat[rownumber, 4]), "Class")
                if classalonesyn != 0:
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
                phylumalonesyn = synonymchecker("%s" % (databaseta.iat[rownumber, 2]), "Phylum")
                if phylumalonesyn != 0:
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
                kingdomalonesyn = synonymchecker("%s" % (databaseta.iat[rownumber, 0]), "Kingdom")
                if kingdomalonesyn != 0:
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

        elif y.text == databaseta.iat[rownumber, x * 2]:
            buttonchanger("%s" % SISList[x], y.text)
            # mark the species check as good
            databaseta.iat[rownumber, (x * 2) + 1] = "M"
        else:
            pass

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

# script to update all python packages currently installed
def UpdatePackages():
    packages = pip.get_installed_distributions()
    n_packages = len(packages)

    for i, package in enumerate(packages):
        name = package.project_name
        if name == "fiona" or name == "gdal" or name == "shapely":
            pass
        else:
            print('Updating ' + str(i + 1) + ' of ' + str(n_packages) + ': ' + name)
            call('pip install --upgrade ' + name, shell=True)

    # at the end reinstall the three precompiled libaries files from dependencies
    # then install GDAL
    print("Install GDAL")
    subprocess.Popen('cmd.exe /C pip install %s/Dependencies/GDAL-2.2.4-cp37-cp37m-win32.whl' % filedir)

    # then install Fiona
    print("Install Fiona")
    subprocess.Popen('cmd.exe /C pip install %s/Dependencies/Fiona-1.7.13-cp37-cp37m-win32.whl' % filedir)

    # then install Shapely
    print("Install Shapely")
    subprocess.Popen('cmd.exe /C pip install %s/Dependencies/Shapely-1.6.4.post1-cp37-cp37m-win32.whl' % filedir)

    # install Pyroj
    print("Install Pyroj")
    subprocess.Popen('cmd.exe /C pip install %s/Dependencies/pyproj-1.9.5.1-cp37-cp37m-win32.whl' % filedir)

    time.sleep(3)

    # restart python application
    print("Restarting Program")
    subprocess.Popen('cmd.exe /C  python %s\ReviewAssistant.py' % filedir)
    # close the current version
    quit()

# downloads manifest from dropbox update folder and checks for what needs to be downloaded and updated
def UpdateSISA():
    global filedir
    global APIkey
    global dbx

    # create a list of the system folders
    systemfolders = []
    for root, dirs, files in os.walk(filedir):
        for name in dirs:
            systemfolders.append(name)

    # create a list of the dropbox folders
    dropboxfolders = []

    for x in dbx.files_list_folder("").entries:
        # strip out the files so only the directories are left
        if "." not in x.name:
            dropboxfolders.append(x.name)

    # check to see if the system has any folders that need to be deleted
    systemextra = set(systemfolders) - set(dropboxfolders)
    todelete = []
    for x in systemextra:
        todelete.append(x)

    if len(todelete) > 0:
        print("Deleting unnecessary folders")
        # run through the list above and delete any extra files
        for file in todelete:
            # delete all subfiles
            for subfile in os.listdir("%s\%s" % (filedir, file)):
                os.remove("%s\%s\%s" % (filedir, file, subfile))

            # once empty delete the main folder
            os.rmdir("%s\%s" % (filedir, file))

    # check to see if dropbox has any folders that need to be created
    dropboxextra = set(dropboxfolders) - set(systemfolders)
    tocreate = []
    for x in dropboxextra:
        tocreate.append(x)

    if len(tocreate) > 0:
        print("Creating additional required folders")
        # run through the above list and create the folders needed
        for x in tocreate:
            os.makedirs("%s/%s" % (filedir, x))

    # create a list of all files currently on the system
    systemfiles = []
    for root, dirs, files in os.walk(filedir):
        for name in files:
            systemfiles.append(os.path.join(root, name).split("SISA")[1].replace("\\", "/"))

    # run through all the files on the dropbox to see if the system ones need replacing
    dropboxfiles = []
    dbnamesonly = []
    for files in dbx.files_list_folder("", recursive=True).entries:
        # strip out the files so only the directories are left
        if "." in files.name:
            dropboxfiles.append([files.path_display, files.size, files.server_modified])
            dbnamesonly.append(files.path_display)

    # compare all system files to dropbox, comparing name and size, if different then replace
    for dropboxfile in dropboxfiles:
        # first check to see if the file exists on the system
        if dropboxfile[0] in systemfiles:
            # get time of the creation of the system file
            systemunixtime = os.path.getmtime("%s/%s" % (filedir, dropboxfile[0]))
            # convert to time in timestamp
            convertedsystemtime = datetime.datetime.fromtimestamp(systemunixtime)
            # if daylight savings then convert appropriatly
            if time.tzname[time.daylight] == "GMT Daylight Time":
                convertedsystemtime = convertedsystemtime - datetime.timedelta(hours=1)
            # get the dropbox timestamp and convert into format
            dropboxtimetest = datetime.datetime.strptime(str(dropboxfile[2]), '%Y-%m-%d %H:%M:%S')

            # if it does then compare the size and date of the file, if different the download and replace
            if dropboxtimetest > convertedsystemtime:
                print("Updating %s" % dropboxfile[0])
                dbx.files_download_to_file(path=dropboxfile[0], download_path="%s%s" % (filedir, dropboxfile[0]))
        else:
            print("Downloading %s" % dropboxfile[0])
            dbx.files_download_to_file(path=dropboxfile[0], download_path="%s%s" % (filedir, dropboxfile[0]))

    # check to see if any extra system files that need to be deleted
    provosionalfilestodelete = set(systemfiles) - set(dbnamesonly)
    filestodelete = []

    for x in provosionalfilestodelete:
        if "WorkingSetStore" not in x:
            filestodelete.append(x)

    if len(filestodelete) > 0:
        print("Removing any uncessary files")
        # run through the extra files and delete them
        for x in filestodelete:
            os.remove(filedir + x)

    # report completion
    print("Update Complete")
    messagebox.showinfo(title="Notification", message="Update Successful Restarting")

    # restart python application
    subprocess.Popen('cmd.exe /C  python %s\ReviewAssistant.py' % filedir)
    # close the current version
    quit()

# lets the user set a folder and updates the screen to reflect the choices
def choosefolder():
    sourcefolder = filedialog.askdirectory()
    folderforbulkconversion.set(sourcefolder)
    foldertoplaceconverted.set("%s/convertedfiles" % sourcefolder)

    # Run through provided folder and detect file types
    listoffiletypes = {}
    for x in os.listdir(sourcefolder):
        listoffiletypes[str(os.path.splitext(x)[1]).replace(".","")] = 0

    # get rid of '' which comes from folders
    if '' in listoffiletypes:
        del listoffiletypes['']

    # Run through the list and place a 1 by all supported file types
    supportedfiletypes = ["geocat", "csv"]
    for type in supportedfiletypes:
        if type in listoffiletypes:
            listoffiletypes[type] = 1

    # run through and create a string of accepted file types
    acceptedfiletypes = ""
    notacceptedfiletypes = ""
    for key, value in listoffiletypes.items():
        if value == 1:
            acceptedfiletypes += str("%s, " % key)
        else:
            notacceptedfiletypes += str("%s, " % key)

    acceptedvariablesfound.set(acceptedfiletypes)
    notacceptedvaraiblesfound.set(notacceptedfiletypes)

# runs through the provided folder, reads file type and attempts to convert to esri shapefile
def bulkconvert(locations):
    for x in os.listdir(locations):
        print(x)

# runs through a working set download all attachments that it encounters.
def downloadallattachements(rowinfo):
    global loggedin

    downloadpath = os.path.expanduser("~\Desktop\AttachmentDownload")

    # check if folder on desktop to download things exists if not then create it
    if not os.path.exists(downloadpath):
        os.makedirs(downloadpath)

    # create a list to contain report information
    haveassessments = []

    # get the row selected from the user
    workingsetnameSV.set(rowinfo['text'])
    workingsetlocation = "%s\\WorkingSetStore\\%s.pkl" % (filedir, rowinfo['text'])

    # load the dataframe into memory
    database = pandas.read_pickle(workingsetlocation)

    # get the id for the first one
    id = str(database.iat[0,0])

    # get the binomial
    binomial = str(database.iat[0,1])

    # log the user in if needed to allow downloads to occur
    if loggedin == 0:
        currenturl = driver.current_url
        assessmentid = 4224
        driver.execute_script("window.open('http://%s:%s@sis.iucnsis.org/apps/org.iucn.sis.server.extensions.integrity/validate?id=%s&type=submitted_status')" % (usernamevariable, passwordvariable, assessmentid))
        driver.switch_to.window(driver.window_handles[1])
        try:
            element = WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'Click here to view')]")))
        finally:
            element.click()
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            loggedin = 1

    # navigate to the page
    searchbyanything(id)

    # create the current data and global tag
    date = datetime.datetime.now()
    datestring = "%s-%s-%s --- Global" % (date.year, date.month, date.day)

    # click the option with the current date and global (indicating the submitted assessment).
    actionChains = ActionChains(driver)
    actionChains.double_click(driver.find_element_by_xpath("//*[contains(text(), '%s')]" % datestring)).perform()

    # click the attachments button and then the manage attachments button
    driver.find_element_by_xpath("//*[contains(text(), 'Attachments')]").click()
    driver.find_element_by_xpath("//*[contains(text(), 'Manage Attachments')]").click()
    driver.implicitly_wait(0.5)

    # try to find the ok button which appears if no attachments if this fails then there are attachments
    try:
        # find and click the ok button
        driver.find_element_by_xpath("//*[contains(text(), 'There are no attachments for this assessment.')]").find_element_by_xpath("//*[contains(text(), 'OK')]").click()
        print("No attachement for {}".format(binomial))
    except:
        # add binomial to a list, so that you know which ones had assessments
        haveassessments.append(binomial)
        # download all the assessments for this species
        listofdownloads = driver.find_elements_by_css_selector(".x-grid3-col.x-grid3-cell.x-grid3-td-publish")
        listofparents = []
        for x in listofdownloads:
            listofparents.append(x.find_element_by_xpath(".."))

        print(listofparents)

        # for each row of the attachments file
        for x in listofparents:
            # check to see if the name contains a spatial data folder (testing for .geocat, .kml)
            if ".geocat" in list(x.text.splitlines())[0] or ".kml" in list(x.text.splitlines())[0]:
                print("Spatial File Found")
                # bring focus to the row
                x.click()
                # press download (need to change the default download location to the correct folder)
                driver.find_element_by_xpath("//*[contains(text(), 'Download')]").click()
                # close the attachements window

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
citationsession = []
citationsession.append("None")
citationsession.append("IUCN")
loggedin = 0
folderforbulkconversion = StringVar()
foldertoplaceconverted = StringVar()
acceptedvariablesfound = StringVar()
notacceptedvaraiblesfound = StringVar()
freshwaterSV = StringVar()
freshwaterSV.set("NoValue")
workingsetnameSV = StringVar()


# load and setup version number
versionnumbertext = StringVar()
versionfile = open("%s/VersionNumber.txt" % filedir, 'r')
versionnumber = versionfile.read()
versionnumbertext.set("SISA Version %s" % versionnumber)
versionfile.close()

# load up WS-MAP link table
linktable = pandas.read_pickle("%s\\WorkingSetStore\\WSMAPLinkTable.pkl" % filedir)

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

# options page
optionsframe = ttk.Frame(root, padding="0 0 0 0")
optionsframe.grid(column=0, row=0, sticky=N+S+E+W)
optionsframe.master.minsize(width=510, height=510)

# reviewassistantframe
reviewassistantframe = ttk.Frame(root, padding="0 0 0 0")
reviewassistantframe.grid(column=0, row=0, sticky=N+S+E+W)
reviewassistantframe.master.minsize(width=510, height=510)

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

# spatialdatatoolmenuframe
spatialdatatoolmenuframe = ttk.Frame(root, padding="0 0 0 0")
spatialdatatoolmenuframe.grid(column=0, row=0, sticky=N+S+E+W)
spatialdatatoolmenuframe.master.minsize(width=510, height=510)

# bulkconvertframe
bulkconvertframe = ttk.Frame(root, padding="0 0 0 0")
bulkconvertframe.grid(column=0, row=0, sticky=N+S+E+W)
bulkconvertframe.master.minsize(width=510, height=510)

# main frame
# main frame images
sislogo = PhotoImage(file="%s\\Images\\sislogo.png" % filedir)
topbar = PhotoImage(file="%s\\Images\\topbar.png" % filedir)

ttk.Label(mainframe, image=sislogo, borderwidth=0).grid(column=0, row=2, sticky=NW)
ttk.Label(mainframe, image=topbar, borderwidth=0).grid(column=0, row=1, columnspan=7)

# main frame labels
ttk.Label(mainframe, textvariable=versionnumbertext, font=(None, 10), background="#DFE8F6").grid(column=6, row=2, sticky=NE)
ttk.Label(mainframe, text="Main Menu", font=(None, 15), background="#DFE8F6").grid(column=0, row=3, columnspan=8)
ttk.Label(mainframe, text="Taxon ID, or Binomial", font=(None, 10), background="#DFE8F6").grid(column=0, row=5, sticky=(S, W, E))

# update button (only show if an update is available (if fail then show can't check text)
try:
    # get API key from files
    APIkeyfile = open("%s/APIkey.txt" % filedir, 'r')
    APIkey = APIkeyfile.read()
    APIkeyfile.close()

    # create dropbox object
    dbx = dropbox.Dropbox('%s' % APIkey)

    # download the version number to see if it needs to be downloaded
    dbx.files_download_to_file(path="/VersionNumber.txt", download_path="%s/VersionNumber.txt" % filedir)

    # open the txt file and check the version number
    versionfile = open("%s/VersionNumber.txt" % filedir, 'r')
    version = versionfile.read()
    versionfile.close()
    # check to see if version matches
    if version > versionnumber:
        ttk.Button(mainframe, text="Update Available", command=lambda: UpdateSISA()).grid(column=6, row=2, sticky=SE)

    else:
        ttk.Button(mainframe, text="Options", command=optionsframe.tkraise).grid(column=6, row=2, sticky=SE)

except:
    ttk.Label("Update Offline").grid(column=6, row=2, sticky=SE)


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
simplesearchbutton = ttk.Button(mainframe, text="Review Assistant", command=lambda: openworkingsetmanager(), state=DISABLED)
simplesearchbutton.grid(column=0, row=8, sticky=(N, S, W, E))
spatialdatatoolspagebutton = ttk.Button(mainframe, text="Bulk S.D Tools", command=spatialdatatoolmenuframe.tkraise, state=DISABLED)
spatialdatatoolspagebutton.grid(column=1, row=8, sticky=(N, S, W, E))
taxadderframebutton = ttk.Button(mainframe, text="Taxonomy Assistant", command=taxadderassistantframe.tkraise, state=DISABLED)
taxadderframebutton.grid(column=0, row=9, sticky=(N, S, W, E))
logoutbutton = ttk.Button(mainframe, text="Log Out", command=lambda: logout(), state=DISABLED)
logoutbutton.grid(column=0, row=11, sticky=(N, S, W))

ttk.Button(mainframe, text="Quit", command=quit).grid(column=0, row=12, sticky=(N, S, W))

mainframe.columnconfigure((0, 1, 2), weight=1)
mainframe.rowconfigure((3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

# Options Frame
ttk.Label(optionsframe, image=topbar, borderwidth=0).grid(column=0, row=0, sticky=EW)
ttk.Label(optionsframe, image=sislogo, borderwidth=0).grid(column=0, row=1, sticky=NW)
ttk.Label(optionsframe, text="Options Menu", font=(None, 15), background="#DFE8F6").grid(column=0, row=2, sticky=EW)

# buttons
ttk.Button(optionsframe, text="Integrity Checker", command=lambda: UpdateSISA()).grid(column=0, row=3, sticky=SW)
ttk.Button(optionsframe, text="Update Python Packages", command=lambda: UpdatePackages()).grid(column=0, row=4, sticky=SW)
ttk.Button(optionsframe, text="Return to main menu", command=mainframe.tkraise).grid(column=0, row=10, sticky=SW)

optionsframe.columnconfigure((0, 1, 2), weight=1)
optionsframe.rowconfigure((2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

# bulkconvertframe
# top bar and logo
ttk.Label(bulkconvertframe, image=topbar, borderwidth=0).grid(column=0, row=0, sticky=EW)
ttk.Label(bulkconvertframe, image=sislogo, borderwidth=0).grid(column=0, row=1, sticky=NW)

# labels
ttk.Label(bulkconvertframe, text="Bulk Spatial Data Conversion", font=(None, 15), background="#DFE8F6").grid(column=0, row=1, sticky=E)
ttk.Label(bulkconvertframe, text="Please select folder containing the spatial data", background="#DFE8F6").grid(column=0, row=3, sticky=EW)
ttk.Label(bulkconvertframe, text="Folder Selected", background="#DFE8F6", font=(None, 11)).grid(column=0, row=4, sticky=EW)
ttk.Label(bulkconvertframe, textvariable=folderforbulkconversion, background="#DFE8F6", wraplength=550, font=(None, 7)).grid(column=0, row=5, sticky=EW)
ttk.Label(bulkconvertframe, text="Converted data will be saved at", background="#DFE8F6", font=(None, 11)).grid(column=0, row=6, sticky=EW)
ttk.Label(bulkconvertframe, textvariable=foldertoplaceconverted, background="#DFE8F6", wraplength=550, font=(None, 7)).grid(column=0, row=7, sticky=EW)
ttk.Label(bulkconvertframe, text="Accepted file types: ", background="#DFE8F6", wraplength=550, font=(None, 11)).grid(column=0, row=8, sticky=EW)
ttk.Label(bulkconvertframe, textvariable=acceptedvariablesfound, background="#DFE8F6").grid(column=0, row=9, sticky=EW)
ttk.Label(bulkconvertframe, text="Non Accepted file types: ", background="#DFE8F6", wraplength=550, font=(None, 11)).grid(column=0, row=10, sticky=EW)
ttk.Label(bulkconvertframe, textvariable=notacceptedvaraiblesfound, background="#DFE8F6").grid(column=0, row=11, sticky=EW)


# buttons
ttk.Button(bulkconvertframe, text="Select", command=lambda: choosefolder()).grid(column=0, row=3, sticky=E)
ttk.Button(bulkconvertframe, text="Convert", command=lambda: bulkconvert(folderforbulkconversion.get())).grid(column=0, row=12)
ttk.Button(bulkconvertframe, text="Return to tool menu", command=spatialdatatoolmenuframe.tkraise).grid(column=0, row=13, sticky=SW)

# give weight
bulkconvertframe.columnconfigure((0, 1, 2), weight=1)
bulkconvertframe.rowconfigure((2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

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
# string variables for the details buttons
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

# reviewassistantframe
# reviewassistantframe images
ttk.Label(reviewassistantframe, image=topbar, borderwidth=0).grid(column=0, row=0, sticky=EW, columnspan=8)
ttk.Label(reviewassistantframe, image=sislogo, borderwidth=0).grid(column=0, row=1, sticky=NW, columnspan=2)

# review assistant frame string variables
tablerownumber = IntVar()
nextspecies = StringVar()
previousspecies = StringVar()
currentspeciesname = StringVar()
skipto = IntVar()
candc = StringVar()
databaselength = StringVar()

tablerownumber.set(1)

# review assistant frame labels
textlabel2 = ttk.Label(reviewassistantframe, text="Previous Species", font=(None, 8), background="#DFE8F6")
textlabel2.grid(column=0, row=9)
textlabel3 = ttk.Label(reviewassistantframe, text="Next Species", font=(None, 8), background="#DFE8F6")
textlabel3.grid(column=2, row=9)
previouspeciesvariable = ttk.Label(reviewassistantframe, textvariable=previousspecies, font=(None, 8), background="#DFE8F6", wraplength=150)
previouspeciesvariable.grid(column=0, row=10)
currentspeciesnamelabel = ttk.Label(reviewassistantframe, textvariable=currentspeciesname, font=('arial bold', 10), background="#DFE8F6", wraplength=150, justify=CENTER)
currentspeciesnamelabel.grid(column=1, row=1, sticky=N)
candclabel = ttk.Label(reviewassistantframe, textvariable=candc, font=('aerial bold', 10), background="#DFE8F6")
candclabel.grid(column=1, row=1, sticky=S)
nextspecieslabel= ttk.Label(reviewassistantframe, textvariable=nextspecies, font=(None, 8), background="#DFE8F6", wraplength=150)
nextspecieslabel.grid(column=2, row=10)
textlabel4 = ttk.Label(reviewassistantframe, text="Verification Checks?", font=(None, 8), background="#DFE8F6")
textlabel4.grid(column=0, row=4, sticky=E)
textlabel5 = ttk.Label(reviewassistantframe, text="Criteria Checked?", font=(None, 8), background="#DFE8F6")
textlabel5.grid(column=0, row=5, sticky=E)
textlabel6 = ttk.Label(reviewassistantframe, text="Maps Checked?", font=(None, 8), background="#DFE8F6")
textlabel6.grid(column=0, row=6, sticky=E)
textlabel7 = ttk.Label(reviewassistantframe, text="Skip to ...", font=(None, 8), background="#DFE8F6")
textlabel7.grid(column=1, row=9)
entryvariable1 = ttk.Entry(reviewassistantframe, width=20, textvariable=skipto, state=NORMAL)
entryvariable1.grid(column=1, row=10)
skiptobutton = ttk.Button(reviewassistantframe, text="Skip to...", command=lambda: skiptofunction())
skiptobutton.grid(column=1, row=11)
assessmentnumber = ttk.Label(reviewassistantframe, textvariable=databaselength, font=(None, 8), background="#DFE8F6")
assessmentnumber.grid(column=2, row=1)
reviewtoolsbutton = ttk.Button(reviewassistantframe, text="Open Review Tools", command=lambda: createtoolwindow())
reviewtoolsbutton.grid(column=1, row=12)
hidetoolsbutton = ttk.Button(reviewassistantframe, text="Hide Review Tools", command=lambda: hidetoolwindow())
hidetoolsbutton.grid(column=0, row=12)

#notes box
notesbox = ScrolledText(reviewassistantframe, height=5, width=47)
notesbox.grid(row=7, column=0, columnspan=5, rowspan=2, sticky=NSEW)

# check boxes
verified = StringVar()
verified.set("Not Passed")
criteria = StringVar()
criteria.set("Not Passed")
maps = StringVar()
maps.set("Not Passed")
verifiedcheck = ttk.Button(reviewassistantframe, textvariable=verified, command=lambda: swapstate(verified, verifiedcheck))
criteriacheck = ttk.Button(reviewassistantframe, textvariable=criteria, command=lambda: swapstate(criteria, criteriacheck))
mapscheck = ttk.Button(reviewassistantframe, textvariable=maps, command=lambda: swapstate(maps, mapscheck))
criteriacheck.grid(column=1, row=4, sticky=(N,S))
verifiedcheck.grid(column=1, row=5, sticky=(N,S))
mapscheck.grid(column=1, row=6, sticky=(N,S))

returntomainmenu = ttk.Button(reviewassistantframe, text="Return to main menu", command=lambda: specialreturntomain())
returntomainmenu.grid(column=0, row=12, sticky=SW)

goback = ttk.Button(reviewassistantframe, text="<", command=lambda: update(-1))
goforward = ttk.Button(reviewassistantframe, text=">", command=lambda: update(1))
goback.grid(column=0, row=11, sticky=S)
goforward.grid(column=2, row=11, sticky=S)

# review assistant giving weight to the columns and rows
reviewassistantframe.columnconfigure((0, 1, 2), weight=1)
reviewassistantframe.rowconfigure((3, 4, 5, 6, 7, 8, 9, 10), weight=1)

# spatialdatatoolmenu frame
# logo and top bar
ttk.Label(spatialdatatoolmenuframe, image=topbar, borderwidth=0).grid(column=0, row=0, sticky=EW, columnspan=1)
ttk.Label(spatialdatatoolmenuframe, image=sislogo, borderwidth=0).grid(column=0, row=1, sticky=NW)

# labels
ttk.Label(spatialdatatoolmenuframe, text="Spatial Data Tools", font=(None, 14), background="#DFE8F6").grid(column=0, row=2, sticky=N)
ttk.Label(spatialdatatoolmenuframe, text="Given a chosen file directory, attempts to convert files into ESRI shapefiles", background="#DFE8F6").grid(column=0, row=3, sticky=N)

# spatialdatatoolmenu buttons
ttk.Button(spatialdatatoolmenuframe, text="Blind Convert", command=lambda: bulkconvertframe.tkraise()).grid(column=0, row=4, sticky=N, rowspan=3)
ttk.Button(spatialdatatoolmenuframe, text="Return to main menu", command=lambda: mainframe.tkraise()).grid(column=0, row=5, sticky=SW)

# give weight to rows and columns
spatialdatatoolmenuframe.columnconfigure((0, 1), weight=1)
spatialdatatoolmenuframe.rowconfigure((4), weight=1)


# final buffer tidy up
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

for child in reviewassistantframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

for child in taxadderframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

for child in taxadderassistantframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

for child in optionsframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

for child in spatialdatatoolmenuframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

for child in bulkconvertframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# panda databases have to be loaded after pandas for the above workaround to work
databasera = pandas.DataFrame(index=range(0, 4), columns=['Genus', 'Species', 'Criteria Passed?', 'Validity Passed?', 'Map Passed?', 'Notes']).astype('str')
databaseta = pandas.DataFrame(index=range(0, 4), columns=['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Taxonomic Reference', 'Working Set']).astype('str')
fastreviewdirections = pandas.DataFrame()

# mainloop and raise mainframe to top for start
mainframe.tkraise()
root.mainloop()
