import pandas as pd
from pandas import DataFrame
import numpy as np
import random
import math
import operator
from bokeh.models.layouts import HBox
from bokeh.models.widgets import Div
from bokeh.io import output_file, show
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, BoxSelectTool
)
from bokeh.charts import Histogram

lat = 40.725915
lon = -73.994659

def coordinate_stats(area, latitude,longitude):
    # Search from selected coordinates
    url = 'https://api.foursquare.com/v2/venues/search?ll=%s,%s&intent=browse&radius=80&limit=5000&client_id=CLIENT_ID&client_secret=CLIENT_SECRET&v=20170115' %(latitude,longitude)

    r = pd.read_json(url)
    venues = DataFrame(r['response']['venues'])

    df = []
    venue_ids = venues['id']
    for item in venue_ids:
        venue_id = item
        url2 = 'https://api.foursquare.com/v2/venues/%s?&client_id=CLIENT_ID&client_secret=CLIENT_SECRET&v=20161226' % venue_id
        r2 = pd.read_json(url2)
        frame = DataFrame(r2['response'])
        venue = frame['response']['venue']
        venue_name = venue['name']
        check_ins = venue['stats']['checkinsCount']
        user_count = venue['stats']['usersCount']
        here_now = venue['hereNow']
        count = here_now['count']
        #print("Name: ", venue_name, "Check-ins: ", check_ins, "User count: ", user_count, "Here now: ", count)
        df.append((venue_name, check_ins, user_count, count))

    frame = DataFrame(df)
    frame.columns= ['venue name', 'check-ins', 'user count', 'count']
    frame['user check-in frequency'] = frame['check-ins']/frame['user count']
    frame['name'] = area
    return frame


ace = coordinate_stats('Ace Hotel, W 29th & Broadway', 40.745888, -73.988280)
bowery = coordinate_stats('Bowery Hotel, E 2nd & Bowery', 40.726367, -73.991730)
frames = [ace, bowery]
result = pd.concat(frames)
print(result)


plot = Histogram(result, values='user check-in frequency', color='name', title='Regional Popularity', legend='top_right')

description = Div(text="""<p>Foursquare provides details on individual venues but does not currently provide statistics of users’ check-ins for a region as a whole.</p> 

<p>User check-in frequency (UCF) is used as a metric of overall venue popularity. This is calculated as the cumulative number of check-ins divided by number of unique users of a venue. A larger UCF value represents more check-ins from a user on average. UCF can be interpreted as users’ loyalty to a venue.</p> 

<p>For example, if a business owner is deciding between opening a restaurant near the Ace Hotel or the Bowery Hotel in Manhattan, they would want to know which location generates more return customers. Based on analysis of venues within 80 meters of each location, the Ace Hotel has more return users in its surrounding area than the Bowery Hotel and is therefore the more desirable location.</p> 

<p>This analysis will run off of user-selected coordinates when project is complete.</p> 

<p>Data scraped from <a href="https://foursquare.com">Foursquare’s API</a></p>""") 


page = HBox(plot, description)

output_file("Distribution.html")

show(page)
