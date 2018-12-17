import csv
import pandas
import re
import datetime
import pickle
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from geopandas import GeoDataFrame
from shapely.geometry import Point
import shapely
import fiona
shapely.speedups.enable()
import geopandas
import os
fiona.drvsupport.supported_drivers['libkml'] = 'rw'
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'


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
    # user points are stored separatly to the GBIF points
    sourcelist = contents.split(sep="points")
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

    # with the data in a dataframe format, now do the first stage rough tidying up of data
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
def inportandcovert(csvfile, gdf, speciesname):
    # create dictionary to store all conversions
    try:
        conversiontable = []
        for counter, combobox in enumerate(CSVdetails.children.values()):
            if 'combobox' in str(combobox):
                conversiontable.append(combobox.get())

        # test to see if any are Not Present
        if conversiontable[0] == "Not Present":
            messagebox.showerror(title="Devil Llama with Horns", message="No Dec_Lat column defined, define to continue")
        if conversiontable[1] == "Not Present":
            messagebox.showerror(title="Devil Llama with Long Horns", message="No Dec_Long column defined, define to continue")
        if conversiontable[2] == "Not Present":
            messagebox.showerror(title="Devil Llama in disguise", message="No CRS definined, creating and defaulting to WGS84")
            csvfile["SpatialRef"] = "WGS84"
            conversiontable[2] = "SpatialRef"

        # if already correct then don't rename column
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

        geometry = [Point(xy) for xy in zip(csvfile.Dec_Long, csvfile.Dec_Lat)]
        crs = {'init': 'epsg:4326'}
        gdf = GeoDataFrame(csvfile, crs=crs, geometry=geometry)

        # if crs is not WGS 84 then convert the points
        if crs != "{'init': 'epsg:4326'}":
            print("Data supplied is not in WGS84 reprojecting...")
            gdf = gdf.to_crs({'init': 'epsg:4326'})

        # save to file
        gdf.to_file("C:\\Users\\fancourtm\\Desktop\\Converted\\", driver='ESRI Shapefile', layer=speciesname)

        # destroy topwindow
        CSVdetails.destroy()
    except:
        print("Error in convering CSV to ESRI feature class")
        messagebox.showerror(title="Two toned llama", message="Error in CSV to feature class conversion")
        return 1

# reads in csv file and coverts into a ESRI shapefile
def convertCSV(csvfile, gdf, speciesname):
    global CSVdetails

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
    if "Dec_lat" in attributenames:
        Latitude.set("Dec_lat")
    elif "Latitude" in attributenames:
        Latitude.set("Latitude")

    # long search
    if "Dec_long" in attributenames:
        Longitude.set("Dec_long")
    elif "Longitude" in attributenames:
        Longitude.set("Longitude")

    # crs search
    if "Spatialref" in attributenames:
        CRS.set("Spatialref")
    elif "CRS" in attributenames:
        CRS.set("CRS")

    # Import button (this will trigger the columns to be renamed and will transform the pandas into a geopandas dataframe
    ttk.Button(CSVdetails, text="Import", command=lambda: inportandcovert(pandascsvdf, gdf, speciesname)).grid(column=1, row=7, sticky=NSEW)

    # give weight to everything to fill it out
    CSVdetails.columnconfigure((0, 1, 2), weight=1)
    CSVdetails.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

    CSVdetails.wait_window()

def convertKML(kml):
    #print("KML Detected")
    # read the kml into geopandas
    try:
        temp = geopandas.read_file(kml)
        if temp.empty:
            print("Unable to convert {} file is empty".format(kml))
            return 1
    except:
        print("Unable to convert {}".format(kml))
        return 1

    # drop everything except the geometry field as the rest isn't usable currently
    for x in temp:
        if x == "geometry":
            # get type
            if "Polygon" or "LineString" in temp[x].geom_type:
                temp2 = GeoDataFrame(
                    columns=['ID_NO', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION',
                             'DATA_SENS'], geometry=temp[x])
            else:
                geometry = [Point(xy) for xy in temp[x]]
                crs = {'init': 'epsg:4326'}
                temp2 = GeoDataFrame(
                    columns=['ID_NO', 'BINOMIAL', 'PRESENCE', 'ORIGIN', 'SEASONAL', 'COMPILER', 'YEAR', 'CITATION',
                             'DATA_SENS'], crs=crs, geometry=geometry)
        else:
            temp.drop(x, axis=1, inplace=True)

    temp2['ID_NO'] = 0
    temp2['BINOMIAL'] = speciesname
    temp2['PRESENCE'] = 1
    temp2['ORIGIN'] = 1
    temp2['SEASONAL'] = 1
    temp2['YEAR'] = 0
    temp2['DATA_SENS'] = 0

    try:
        temp2.to_file(exportfile, driver="ESRI Shapefile", layer=speciesname)
        return 0
    except:
        print("Unable to save")
        return 1


root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry('%dx%d+%d+%d' % (510, 510, screen_width - 535, 5))
root.update()

file = 'C:\\Users\\fancourtm\\Desktop\\MapData'
exportfile = 'C:\\Users\\fancourtm\\Desktop\\Converted'

for x in os.listdir(file):
    # get species name
    speciesname= x.split(".")[0]
    if ".csv" in x:
        gdf = GeoDataFrame()
        convertCSV("C:\\Users\\fancourtm\\Desktop\\CSVs\\%s" % x, gdf, speciesname)

    elif ".kml" in x:
        convertKML("%s\\%s" % (file, x))

    else:
        print("Llama Noise")

print("Conversion Completed")

root.mainloop()


