import pandas as pd
from pandas import DataFrame
import numpy as np
import random
import math
import operator
from bokeh.io import output_file, show
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, BoxSelectTool
)
from bokeh.palettes import viridis

map_frame = pd.read_csv('http://web.mta.info/developers/data/nyct/subway/StationEntrances.csv')
map_frame = map_frame.drop_duplicates(subset='Station_Name', keep='last')

print(len(map_frame))

df = []
for x in map_frame.index:
    latitude = map_frame.loc[x, 'Station_Latitude']
    longitude = map_frame.loc[x, 'Station_Longitude']

    # Search all stations
    url = 'https://api.foursquare.com/v2/venues/trending?ll=%s,%s&intent=browse&radius=1000&limit=14&client_id=CLIENT_ID&client_secret=CLIENT_SECRET&v=20170115' %(latitude,longitude)

    r = pd.read_json(url)
    venues = DataFrame(r['response']['venues'])

    try:
        venue_ids = venues['id']
        for item in venue_ids:
            venue_id = item
            url2 = 'https://api.foursquare.com/v2/venues/%s?&client_id=CLIENT_ID&client_secret=YCLIENT_SECRET&v=20161226' % venue_id
            r2 = pd.read_json(url2)
            frame = DataFrame(r2['response'])
            venue = frame['response']['venue']
            here_now = venue['hereNow']
            count = here_now['count']
            print(latitude, longitude, count)
            df.append((latitude, longitude, count))
    except Exception as e:
        venue_ids = 'NaN'
        count = 0
        print(latitude, longitude, count)
        df.append((latitude, longitude, count))

count_df = DataFrame(df)
count_df.columns = ['latitude', 'longitude', 'count'] #need to change column names; this df needs column names 0,1,2


#Categorize each venue
#bins = [-1, 0, (np.max(count_df['count'])*.25), (np.max(count_df['count'])*.5), (np.max(count_df['count'])*.75), np.max(count_df['count'])]
bins = [-1, 0, 3, 6, 9, 12, 15, 18, 21, 1000]
group_names = ['zero', 'three', 'six', 'nine', 'twelve', 'fifteen', 'eighteen', 'twentyone', 'high']
categories = pd.cut(count_df['count'], bins, labels=group_names)
count_df['categories'] = categories
count_df = count_df.drop('count', 1)
count_df.columns = [0,1,2]
print(count_df)


#Create test set
def frange(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step
df2 = []
for i in frange(-74.05, -73.75, 0.001):
    for j in frange(40.55, 40.9, 0.001):
        df2.append((j,i))
coordinates = DataFrame(df2)

# k-nearest neighbor
def loadDataset(filename, trainingSet=[]):
    df3 = filename
    for x in range(len(df3)-1):
        for y in range(2):
            df3.loc[x,y]
        trainingSet.append(df3.loc[x]) 

def euclideanDistance(instance1, instance2, length):
    distance = 0
    for x in range(length):
        distance += pow((instance1[x] - instance2[x]), 2)
    return math.sqrt(distance)

def getNeighbors(trainingSet, testInstance, k):
    distances = []
    length = len(testInstance)
    for x in range(len(trainingSet)):
        dist = euclideanDistance(testInstance, trainingSet[x], length)
        distances.append((trainingSet[x], dist))
    distances.sort(key=operator.itemgetter(1))
    neighbors = [] 
    for x in range(k):
        neighbors.append(distances[x][0])
    return neighbors

def getResponse(neighbors):
    classVotes = {}
    for x in range(len(neighbors)):
        response = neighbors[x][2]  
        if response in classVotes:
            classVotes[response] += 1
        else:
            classVotes[response] = 1
    sortedVotes = sorted(classVotes.items(), key=operator.itemgetter(1), reverse=True)
    return sortedVotes[0][0]

def main():
    trainingSet=[]
    testSet= coordinates        #range of longitude and latitudes
    loadDataset(count_df, trainingSet)
    #generate predictions
    predictions=[]
    k = 3
    for x in range(len(testSet)):
        neighbors = getNeighbors(trainingSet, testSet.iloc[x], k)
        result = getResponse(neighbors)
        predictions.append(result)
    coordinates['predictions'] = predictions
    print(predictions)
    coordinates.to_excel('/Users/twitter/Desktop/plot9.xlsx')
    coordinates.columns = ['latitude', 'longitude', 'predictions']
    return coordinates
main()




#bin into checked in ranges here
gp = coordinates.groupby('predictions')
#none = gp.get_group(name='None')
#low = gp.get_group(name='Low')
#median = gp.get_group(name='Median')
#high = gp.get_group(name='High')


#GMap options here
map_options = GMapOptions(lat=40.7352, lng=-73.9736, map_type="roadmap", zoom=13)

plot = GMapPlot(
    x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options, api_key=API_KEY
)

try:
    high = gp.get_group(name='High')
    source = ColumnDataSource(
        data=dict(
            lat=high['latitude'],
            lon=high['longitude'],
        )
    )
    circle = Circle(x="lon", y="lat", size=10, fill_color="#FDE724", fill_alpha=0.4, line_color=None)
    plot.add_glyph(source, circle)
except Exception as e:
    high = 'NaN'

try:
    twentyone = gp.get_group(name='twentyone')
    source2 = ColumnDataSource(
        data=dict(
            lat2=moderate['latitude'],
            lon2=moderate['longitude'],
        )
    )
    circle2 = Circle(x="lon2", y="lat2", size=10, fill_color="#AADB32", fill_alpha=0.4, line_color=None)
    plot.add_glyph(source2, circle2)
except Exception as e:
    moderate = 'NaN'

try:
    eighteen = gp.get_group(name='eighteen')
    source3 = ColumnDataSource(
        data=dict(
            lat3=median['latitude'],
            lon3=median['longitude'],
        )
    )
    circle3 = Circle(x="lon3", y="lat3", size=10, fill_color="#5BC862", fill_alpha=0.4, line_color=None)
    plot.add_glyph(source3, circle3)
except Exception as e:
    median = 'NaN'

try:
    fifteen = gp.get_group(name='fifteen')
    source4 = ColumnDataSource(
        data=dict(
            lat4=low['latitude'],
            lon4=low['longitude'],
        )
    )
    circle4 = Circle(x="lon4", y="lat4", size=10, fill_color="#27AD80", fill_alpha=0.4, line_color=None)
    plot.add_glyph(source4, circle4)
except Exception as e:
    low = 'NaN'

try:
    twelve = gp.get_group(name='twelve')
    source5 = ColumnDataSource(
        data=dict(
            lat5=none['latitude'],
            lon5=none['longitude'],
        )
    )
    circle5 = Circle(x="lon5", y="lat5", size=10, fill_color="#208F8C", fill_alpha=0.4, line_color=None)
    plot.add_glyph(source5, circle5)
except Exception as e:
    none = 'NaN'

try:
    nine = gp.get_group(name='nine')
    source6 = ColumnDataSource(
        data=dict(
            lat6=none['latitude'],
            lon6=none['longitude'],
        )
    )
    circle6 = Circle(x="lon6", y="lat6", size=10, fill_color="#2C718E", fill_alpha=0.4, line_color=None)
    plot.add_glyph(source6, circle6)
except Exception as e:
    none = 'NaN'

try:
    six = gp.get_group(name='six')
    source7 = ColumnDataSource(
        data=dict(
            lat7=none['latitude'],
            lon7=none['longitude'],
        )
    )
    circle7 = Circle(x="lon7", y="lat7", size=10, fill_color="#3B518A", fill_alpha=0.4, line_color=None)
    plot.add_glyph(source7, circle7)
except Exception as e:
    none = 'NaN'

try:
    three = gp.get_group(name='three')
    source8 = ColumnDataSource(
        data=dict(
            lat8=none['latitude'],
            lon8=none['longitude'],
        )
    )
    circle8 = Circle(x="lon8", y="lat8", size=10, fill_color="#472B7A", fill_alpha=0.4, line_color=None)
    plot.add_glyph(source8, circle8)
except Exception as e:
    none = 'NaN'

try:
    zero = gp.get_group(name='zero')
    source9 = ColumnDataSource(
        data=dict(
            lat9=none['latitude'],
            lon9=none['longitude'],
        )
    )
    circle9 = Circle(x="lon9", y="lat9", size=10, fill_color="#440154", fill_alpha=0.4, line_color=None)
    plot.add_glyph(source9, circle9)
except Exception as e:
    none = 'NaN'

plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool())
plot.title.text="New York City"
plot.toolbar.logo=None
output_file("gmap_plot.html")
show(plot)


