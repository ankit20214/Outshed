import haversine
from haversine import Unit
from geopy.distance import geodesic
# Geopandas
file = open('route_470.txt','r')
data = file.readlines()
file.close()

data = [data[i].split(',') for i in range(len(data))]

stop_ids = [data[i][-2] for i in range(len(data))]
stop_ids = [int(stop_ids[i]) for i in range(len(stop_ids))]

print(stop_ids)

stops = open('stops.txt','r')
stops_data = stops.readlines()
stops.close()

stops_data = [stops_data[i].split(',') for i in range(1,len(stops_data))]
stops_lat_long_map = {int(stops_data[i][0]):[float(stops_data[i][-3]),float(stops_data[i][-2])] for i in range(len(stops_data))}

data_lat = []
for i in stop_ids:
    data_lat += [stops_lat_long_map[i]]


for d in data_lat:
    print(d)
print()

total_dist = 0
t2 = 0
for i in range(1, len(data_lat)):
    dist2 = haversine.haversine((data_lat[i][0],data_lat[i][1]), (data_lat[i - 1][0],data_lat[i-1][1]))
    t2 += dist2
    dist = geodesic((data_lat[i][0],data_lat[i][1]), (data_lat[i - 1][0],data_lat[i-1][1])).km
    total_dist += dist
    print(dist)
print(total_dist)
print(t2)