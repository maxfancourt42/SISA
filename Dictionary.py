import pickle
import pandas


df = pandas.DataFrame(data=None, columns=['WorkingSetName', 'MapLocation', "Date", "LeftAt"],index=[0])

df.iat[0,0] = "TempWorkingSetName"
df.iat[0,1] = "TempLocation"
df.iat[0,2] = "2018-11-01"
df.iat[0,3] = "1"

df.to_pickle("C:\\Users\\fancourtm\\Desktop\\WSMAPLinkTable.pkl")

#df = pandas.read_pickle("C:\\Users\\fancourtm\\PycharmProjects\\SISA\\WorkingSetStore\\WSMAPLinkTable.pkl")



print("Hello")