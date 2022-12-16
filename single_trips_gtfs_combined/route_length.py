from geopy.distance import geodesic

file = open('routes.txt','r')
routes_data= file.readlines()
routes_data = [routes_data[i].split(',') for i in range(1,len(routes_data))]

file.close()

file = open('trips.txt','r')
trips_data = file.readlines()
trips_data = [trips_data[i].split(',') for i in range(1,len(trips_data))]
file.close()

file = open('stop_times.txt','r')
stop_times_data = file.readlines()
stop_times_data = [stop_times_data[i].split(',') for i in range(1,len(stop_times_data))]
file.close()

route_name_to_routeID_map = {routes_data[i][2]:routes_data[i][1] for i in range(len(routes_data))}

routeID_to_tripID_map = {trips_data[i][0]:trips_data[i][2] for i in range(len(trips_data))}

tripID_to_stops_map = {}

cnt = 0
for k in tripID_to_stops_map.keys():
	cnt += 1
	if cnt == 10:
		break
	print(type(k))
	print(k,tripID_to_stops_map[k])

stops = open('stops.txt','r')
stops_data = stops.readlines()
stops.close()

stops_data = [stops_data[i].split(',') for i in range(1,len(stops_data))]
stops_lat_long_map = {int(stops_data[i][0]):(float(stops_data[i][-3]),float(stops_data[i][-2])) for i in range(len(stops_data))}

for i in range(len(stop_times_data)):
	if stop_times_data[i][0] not in tripID_to_stops_map.keys():
		tripID_to_stops_map[stop_times_data[i][0]] = [stop_times_data[i][3]]
	else:
		tripID_to_stops_map[stop_times_data[i][0]] += [int(stop_times_data[i][3])]

tripID_to_distance_map = {}

for k in tripID_to_stops_map.keys():
	stops_seq = tripID_to_stops_map[k]
	total_dis = 0
	for i in range(1,len(stops_seq)):
		strt = stops_lat_long_map[int(stops_seq[i-1])]
		end = stops_lat_long_map[stops_seq[i]]
		dist = geodesic(strt, end).km
		total_dis += dist
	tripID_to_distance_map[k] = total_dis

print(tripID_to_distance_map)







