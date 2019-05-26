#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import pandas as pd
import foursquare

with open('canada_postal_code.xml') as f:
     soup=BeautifulSoup(f,'html.parser')

L=[]
for i in range(1,len(soup.table.find_all('tr'))):
    L.append([ x.rstrip('\n') for x in soup.table.find_all('tr')[i].strings if x.rstrip('\n') != '' ])

columns=['PostCode','Borough','Neighborhood']
df=pd.DataFrame(L,columns=columns)
#print(df.head())

#Drop rows with Borough == 'Not assigned'
df=df[df['Borough'] != 'Not assigned']

#Group multile neighbors into 1 row
df=df.groupby(['PostCode','Borough'],as_index=True)['Neighborhood'].apply(', '.join).reset_index()

#Replace 'Not assigned' Neighborhood by Borough
df.Neighborhood[df.Neighborhood == 'Not assigned'] = df.Borough

df.head()

#Load lat long
lat_long=pd.read_csv('Geospatial_data')

#Update column name
lat_long.rename(columns={'Postal Code':'PostCode'},inplace=True)
lat_long.head()

#Merge to DataFrame
df=pd.merge(df,lat_long,on='PostCode')

#Take data with borough ~ 'Toronto' on
toronto_data=df[df['Borough'].str.find("Toronto") > -1].reset_index(drop=True)
print(toronto_data.head())
######
#CLIENT_ID = 'NOCPT3ULRVCEGUZIFDUDREID0FCWL4NCTTLTUZM4BNLSMW5C' # your Foursquare ID
CLIENT_ID = 'TM3VQWC3JDBKWDVTEJRDDPM2LY2JFCIVBJ4JUOZZA0Z1K0KL'
 # your Foursquare ID
#CLIENT_SECRET = 'Q3OUHQKP3JL5UPEJCVFBC1G0M1DVGUID1RINFAFOPELUYV2F' # your Foursquare Secret
CLIENT_SECRET = 'FGBQHNJ5RSL0HCVD50BSTCU5YZZRXSS3B4NGAFL0XHM2ATK1' # your Foursquare Secret
VERSION = '20190506' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)

client = foursquare.Foursquare(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,version='20190528')

def ParkingLotNearby(df):
    L=[]
    #for row in df.head(3).itertuples():
    for row in df.itertuples():
        ll=str(row.Latitude) + ',' +  str(row.Longitude)
        park=client.venues.search(params={'ll':ll,'categoryId':'4c38df4de52ce0d596b336e1','radius':500})
        if len(park['venues']) > 3:
            L.append(1)
        else:
            L.append(0)
    return(L)

ParkingLotDf=pd.DataFrame(ParkingLotNearby(toronto_data),columns=['ParkingLotNearby'])
print(ParkingLotDf.head())
