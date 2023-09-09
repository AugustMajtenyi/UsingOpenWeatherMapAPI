# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 12:03:56 2023

@author: augus
"""

#import pprint
import requests
import sys
from statistics import mean
import csv
import pandas as pd


#API Key
api_key = '265e8f3e531f7cfce5c5c6aa8c1715c4'
  
#List of locations to compare
cities = [
    'Guilin, China',
    'Dissen, Germany',
    'Guatemala City, Guatemala',
    'Kandukur, India',
    'Nanaimo, British Columbia',
    'Uijeongbu-si, South Korea',
    'Yangon, Myanmar',
    'Jalpa de Mendez, Mexico',
    'Enugu, Nigeria',
    'Peterhead, Scotland',
    'Lima, Peru',
    'Singapore, Singapore',
    'Kaohsiung, Taiwan',
    'Grimesland, North Carolina',
    'Visalia, California',
    'Colonia del Sacramento, Uruguay']

#variabls for csv writing and visuals
csv_temp = []
csv_file = "temp.csv"
max_temps = [[],[],[],[]]
avg_maxTemps = []
header = ['City','Min 1','Max 1','Min 2','Max 2','Min 3','Max 3','Min 4','Max 4','Min Avg','Max Avg']




#Looping between all the locations in the cities array...
city_num = 0
while city_num < len(cities):
    URL = 'http://api.openweathermap.org/geo/1.0/direct'

    
    city_row = [cities[city_num]]
    
    #Find the Lat and Lon...
    geo = f'{URL}?q={cities[city_num]}&limit=5&appid={api_key}'
    resp = requests.get( geo )
    if resp.status_code != 200:  # Failure?
        print( f'Error geocoding {cities[city_num]}: {resp.status_code}' )
        sys.exit( 1 )
    
    if len( resp.json() ) == 0:  # No such city?
      print( f'Error locating city {cities[city_num]}; {resp.status_code}' )
      sys.exit( 2 )
    
    json = resp.json()
    if type( json ) == list:  # List of cities?
      lat = json[ 0 ][ 'lat' ]
      lon = json[ 0 ][ 'lon' ]
    else:  # Unknown city?
      print( f'Error, invalid data returned for city {cities[city_num]}, {resp.status_code}' )
      sys.exit( 3 )
    
    #Use cities's latitude and longitude to get it's 5-day forecast in 3-hour    
    URL = 'http://api.openweathermap.org/data/2.5/forecast'
    forecast = f'{URL}?lat={lat}&lon={lon}&appid={api_key}'
    resp = requests.get( forecast )
    
    if resp.status_code != 200:  # Failure?
        print( f'Error retrieving data: {resp.status_code}' )
        sys.exit( 4 )   
    data = resp.json()        
    
    #Use 5-day forecast to create an array of min and max temps as asked
    block_Var = 0
    while data[ 'list' ][ block_Var ][ 'dt_txt' ].split(" ")[1] != '00:00:00':
        block_Var += 1
    day1start = block_Var

    day_num = 0
    while day_num < 4:
        temp_min = data[ 'list' ][ day1start + day_num*8 ][ 'main' ][ 'temp_min' ]
        temp_max = data[ 'list' ][ day1start + day_num*8 ][ 'main' ][ 'temp_max' ]
        i = 1
        while i < 8:  
            if data[ 'list' ][ day1start + i + day_num*8 ][ 'main' ][ 'temp_min' ] < temp_min:
                temp_min = data[ 'list' ][ day1start + i + day_num*8 ][ 'main' ][ 'temp_min' ]
            if data[ 'list' ][ day1start + i + day_num*8 ][ 'main' ][ 'temp_max' ] > temp_max:
                temp_max = data[ 'list' ][ day1start + i + day_num*8 ][ 'main' ][ 'temp_max' ]
            i += 1
        #Add min/max temp for each day to the CSV array
        city_row.append(temp_min)
        city_row.append(temp_max)
        #Add max temps to an array to be plotted
        max_temps[day_num].append(((temp_max-273.15)*9/5)+32)
        
        day_num += 1
    #Adds avgMin and avgMax to the CSV Array
    city_row.append(round(mean([city_row[1],city_row[3],city_row[5],city_row[7]]),2))
    city_row.append(round(mean([city_row[2],city_row[4],city_row[6],city_row[8]]),2))
    csv_temp.append(city_row)
    
    #Adds average Max temp to be plotted    
    avg_maxTemps.append(round(((mean([city_row[2],city_row[4],city_row[6],city_row[8]])-273.15)*9/5)+32,2))

    city_num += 1
    #print(city_row)   
    

# writing to csv file 
with open(csv_file, 'w') as csvfile: 
    # creating a csv writer object 
    csvwriter = csv.writer(csvfile) 
        
    # writing the fields 
    csvwriter.writerow(header) 
        
    # writing the data rows 
    csvwriter.writerows(csv_temp)
    print("csv written")

 
#Creating a line graph with pandas   
df_maxtemps = pd.DataFrame( max_temps, columns=cities, index=['Day 1', 'Day 2', 'Day 3', 'Day 4'])
ax = df_maxtemps.plot(title="Max Temps in Diff Cities")
ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))


#Creating a bar chart with pandas   
df_averageMaxTemps = pd.DataFrame({'loc':cities, 'Fahrenheit':avg_maxTemps})
df_averageMaxTemps.plot.bar(title="Comparing Avg Max Temps over the Next 4 days",x='loc', y='Fahrenheit', rot=90)
