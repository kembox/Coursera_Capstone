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

#Venues categories
Residence='4e67e38e036454776db1fb3a'
ParkingLot='4c38df4de52ce0d596b336e1'
BusStation='4bf58dd8d48988d1fe931735'
BusStop='52f2ab2ebcbc57f1066b8b4f'
Hotel='4bf58dd8d48988d1fa931735'
Intersection='52f2ab2ebcbc57f1066b8b4c'
MetroStation='4bf58dd8d48988d1fd931735'
LightRailStation='4bf58dd8d48988d1fc931735'
TrainStation='4bf58dd8d48988d129951735'
Office='4bf58dd8d48988d124941735'
Market='50be8ee891d4fa8dcc7199a7'
MovieTheater='4bf58dd8d48988d17f941735'
KitchenSupplyStore='58daa1558bbb0b01f18ec1b4'
Butcher='4bf58dd8d48988d11d951735'
CheeseShop='4bf58dd8d48988d11e951735'
FarmersMarket='4bf58dd8d48988d1fa941735'
FishMarket='4bf58dd8d48988d10e951735'
FoodService='56aa371be4b08b9a8d573550'
GourmetShop='4bf58dd8d48988d1f5941735'
GroceryStore='4bf58dd8d48988d118951735'


def ParkingLotNearby(venue_category,radius=500,count=3):
    L=[]
    global toronto_data
    #for row in df.head(10).itertuples():
    for row in df.itertuples():
        ll=str(row.Latitude) + ',' +  str(row.Longitude)
        venue=client.venues.search(params={'ll':ll,'categoryId':venue_category,'radius':radius})
        print(venue)
        if len(venue['venues']) > count:
            L.append(1)
        else:
            L.append(0)
    extra_df=pd.DataFrame(L,columns=['FishMarket'])
    toronto_data=toronto_data.join(extra_df)
    

ParkingLotNearby(FishMarket)
print(toronto_data.head())
