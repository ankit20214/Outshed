from geopy.distance import geodesic


def route_lengths():
	file = open('routes.txt','r')
	routes_data= file.readlines()
	routes_data = [routes_data[i].strip().split(',') for i in range(1,len(routes_data))]

	file.close()

	file = open('trips.txt','r')
	trips_data = file.readlines()
	trips_data = [trips_data[i].strip().split(',') for i in range(1,len(trips_data))]
	file.close()

	file = open('stop_times.txt','r')
	stop_times_data = file.readlines()
	stop_times_data = [stop_times_data[i].strip().split(',') for i in range(1,len(stop_times_data))]
	file.close()

	route_name_to_routeID_map = {routes_data[i][2]:routes_data[i][1] for i in range(len(routes_data))}

	routeID_to_tripID_map = {trips_data[i][0]:trips_data[i][2] for i in range(len(trips_data))}

	tripID_to_routeID_map = {trips_data[i][2]:trips_data[i][0] for i in range(len(trips_data))}

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

	# print(tripID_to_distance_map['498_08_00'],"Hello")
	# print(tripID_to_distance_map['317_06_00'],"Hiiii")
	return tripID_to_distance_map,routeID_to_tripID_map,route_name_to_routeID_map


def get_duties():


	file = open("/home/alchemist/Desktop/DTC/tcil_all_buses_duties_db.txt_01_08_2022_23_49")
	duties_data  = file.readlines()
	file.close()


	duties_data = [duties_data[i].strip().split(',') for i in range(1,len(duties_data))]
	plate_depot_map = {}
	bus_duty_map = {}

	for i in range(len(duties_data)):
		plate_no = duties_data[i][-5]
		if plate_no not in plate_depot_map.keys():
			plate_depot_map[plate_no] = duties_data[i][3]

		if plate_no not in bus_duty_map.keys():
			bus_duty_map[plate_no] = [duties_data[i][-5]]
		else:
			bus_duty_map[plate_no] += [duties_data[i][-5]]

	# print(bus_duty_map['DL1PC1442'])

	return bus_duty_map,plate_depot_map


def get_allocated_distances():

	bus_duty_map,plate_depot_map = get_duties()
	tripID_to_distance_map,routeID_to_tripID_map,route_name_to_routeID_map = route_lengths()

	bus_distance_allocated = {}


	for k in bus_duty_map.keys():
		duty = bus_duty_map[k]
		bus_distance_allocated[k] = 0
		for d in duty:
			if d in route_name_to_routeID_map.keys():
				route_id = route_name_to_routeID_map[d]
				trip_id = routeID_to_tripID_map[route_id]
				dist = tripID_to_distance_map[trip_id]
				bus_distance_allocated[k] += dist

	return bus_distance_allocated



bus_distance_allocated = get_allocated_distances()

# print(bus_distance_allocated['DL1PC1442'])
# print(get_allocated_distances())



# {"bus_number": "DL1PC8952", "duty": "604", "duty_id": "16", "ot": "30/11/2022, 04:50:20", "it": "", "shift": "m"}




