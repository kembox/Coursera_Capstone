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

#Visibility
easy_view={'Intersection':'52f2ab2ebcbc57f1066b8b4c'}

#support parking lot
parking={'ParkingLot':'4c38df4de52ce0d596b336e1','Hotel':'4bf58dd8d48988d1fa931735'}

#accessibility
transport={
        'BusStation':'4bf58dd8d48988d1fe931735',
        'BusStop':'52f2ab2ebcbc57f1066b8b4f', 
        'MetroStation':'4bf58dd8d48988d1fd931735',
        'LightRailStation':'4bf58dd8d48988d1fc931735',
        'TrainStation':'4bf58dd8d48988d129951735'
        }

#Customer source
customer_source={
        'Office':'4bf58dd8d48988d124941735',
        'Residence':'4e67e38e036454776db1fb3a',
        'ShoppingPlaza':'5744ccdfe4b0c0459246b4dc',
        'PedestrianPlaza':'52e81612bcbc57f1066b7a25',
        'CollegeUniversity':'4d4b7105d754a06372d81259'
        }

#Material supply
supply={
        'Market':'50be8ee891d4fa8dcc7199a7',
        'SuperMarket':'52f2ab2ebcbc57f1066b8b46',
        'Butcher':'4bf58dd8d48988d11d951735',
        'FarmersMarket':'4bf58dd8d48988d1fa941735',
        'FishMarket':'4bf58dd8d48988d10e951735'
        }


def VenuesNearby(df,venue_categories,radius=500):
    nearby_df=pd.DataFrame([])
    for k in venue_categories.keys():
        L=[]
        venue_category=venue_categories[k]    
        for row in df.itertuples():
        #for row in df.head().itertuples():
            ll=str(row.Latitude) + ',' +  str(row.Longitude)
            venue=client.venues.search(params={'ll':ll,'categoryId':venue_category,'radius':radius})
            if len(venue['venues']) > 0:
                L.append(len(venue['venues']))
        if nearby_df.empty: 
            nearby_df=pd.DataFrame(L,columns=[k + 'NearBy'])
        else:
            nearby_df=nearby_df.join(pd.DataFrame(L,columns=[k + 'NearBy']))
    
    return nearby_df
    

supply_nearby=VenuesNearby(toronto_data,supply,radius=3000)
easy_view_nearby=VenuesNearby(toronto_data,easy_view,radius=500)
park_nearby=VenuesNearby(toronto_data,park,radius=500)
transport_nearby=VenuesNearby(toronto_data,transport,radius=1000)
customer_source_nearby=VenuesNearby(toronto_data,customer_source,radius=1000)

#Merge all the nearby venues data into main dataframe
places=[supply_nearby,easy_view_nearby,park_nearby,transport_nearby,customer_source_nearby]
#places=[supply_nearby]
for i in range(len(places)):
    toronto_data=toronto_data.join(places[i])
