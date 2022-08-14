import requests
from datetime import datetime, timedelta
import haversine as hs
from haversine import Unit
from dateutil.parser import parse
import time
import schedule
import json

bus_records = {}
shed_status = {}


def get_bus_trips_data():
    data = requests.get("http://143.110.182.192:8090/depot_tool_duty_master.txt")
    data = data.text.split("\n")
    data = [data[i].split(',') for i in range(1, len(data))]

    return data


def get_bus_gps_data():
    gps_data = requests.get("http://143.110.182.192:8090/tcil_all_buses_db.txt")
    gps_data = gps_data.text.split("\n")
    gps_data = [gps_data[i].split(',') for i in range(len(gps_data))]

    return gps_data


def load_depot_data():
    file = open('depot_lat_long.txt', 'r')
    depot_data = file.readlines()
    depot_data = [depot_data[i].split(',') for i in range(len(depot_data))]
    file.close()

    depot_lat_long = {}
    for i in range(len(depot_data)):
        depot_lat_long[depot_data[i][1]] = [float(depot_data[i][2].strip()), float(depot_data[i][3].strip())]

    return depot_lat_long


def filter_on_depot_distance(current_lat, current_long, depot_lat, depot_long):
    location1 = (current_lat, current_long)
    location2 = (depot_lat, depot_long)

    dist = hs.haversine(location1, location2, unit=Unit.METERS)

    if dist <= 300:
        return True
    else:
        return False


def filter_on_distance_travelled(current_lat, current_long, prev_lat, prev_long):
    location1 = (current_lat, current_long)
    location2 = (prev_lat, prev_long)

    dist = hs.haversine(location1, location2, unit=Unit.METERS)

    if dist <= 100:
        return True
    else:
        return False


def process_start_stop_times():
    bus_duties_data = requests.get("http://143.110.182.192:8090/depot_tool_duty_master.txt")
    bus_duties_data = bus_duties_data.text.split("\n")
    bus_duties_data = [bus_duties_data[i].split(',') for i in range(len(bus_duties_data))]

    bus_timing = {}
    for i in range(1, len(bus_duties_data)):

        if len(bus_duties_data[i]) < 18:
            continue
        current_bus = bus_duties_data[i]
        plate_no = current_bus[11]
        trip_st_time = current_bus[-2]
        trip_en_time = current_bus[-4]
        trip_st_time = datetime.strptime(trip_st_time, '%H:%M:%S').time()
        trip_en_time = datetime.strptime(trip_en_time, '%H:%M:%S').time()
        trip_st_time = datetime.combine(datetime.today().date(), trip_st_time)
        trip_en_time = datetime.combine(datetime.today().date(), trip_en_time)

        if plate_no not in bus_timing.keys():
            bus_timing[plate_no] = [trip_st_time, trip_en_time]
        else:
            bus_timing[plate_no][1] = trip_en_time

    return bus_timing


def record_gps_data(bus_data):
    global bus_records

    if bus_data[2] not in bus_records.keys():
        bus_records[bus_data[2]] = []
    bus_records[bus_data[2]] = [bus_data[0], bus_data[1]]


def detect_out_shed():

    pass


def filter_buses(bus_gps_data, depot_lat_long, bus_timings):
    global shed_status
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    current_date_time = datetime.now()

    for i in range(len(bus_gps_data) - 1):

        datetime_str = bus_gps_data[i][5]
        datetime_obj = parse(datetime_str)

        if len(bus_gps_data[i]) != 14:
            continue

        if datetime_obj.date() != current_date:
            shed_status[bus_gps_data[i][2]] = {'it': "", "ot": ""}
            continue

        plate_no = bus_gps_data[i][2]
        shed_location = bus_gps_data[i][11]
        shed_lat_long = depot_lat_long[shed_location]

        if plate_no not in shed_status.keys():
            shed_status[plate_no] = {'it': "", "ot": ""}

        distance_factor = filter_on_depot_distance(float(bus_gps_data[i][0]), float(bus_gps_data[i][1]),
                                                   float(shed_lat_long[0]), float(shed_lat_long[1]))

        current_lat = bus_gps_data[i][0]
        current_long = bus_gps_data[i][1]

        recorded = False
        distance_travelled_factor = False

        if plate_no not in bus_records.keys():
            record_gps_data(bus_gps_data[i])
        else:
            recorded = True
            prev_rec_lat = bus_records[plate_no][0]
            prev_rec_long = bus_records[plate_no][1]

            distance_travelled_factor = filter_on_distance_travelled(float(current_lat), float(current_long),
                                                                     float(prev_rec_lat), float(prev_rec_long))
            record_gps_data(bus_gps_data[i])

        if plate_no not in bus_timings.keys():
            if not distance_factor and not distance_travelled_factor and shed_status[plate_no]['ot'] == '':
                shed_status[plate_no]['ot'] = current_time.strftime('%H:%M:%S')
            elif distance_travelled_factor and distance_factor and shed_status[plate_no]['ot'] != '' and shed_status[plate_no]['it'] == '':
                shed_status[plate_no]['it'] = current_time.strftime('%H:%M:%S')
            continue

        trip_start_time = bus_timings[plate_no][0]
        trip_end_time = bus_timings[plate_no][1]

        if current_date_time >= trip_start_time or (trip_start_time - current_date_time) <= timedelta(seconds=300):
            trip_started = True
        else:
            trip_started = False

        if abs(trip_end_time - current_date_time) <= timedelta(seconds=600) or \
                (current_date_time - trip_end_time > timedelta(seconds=0)):
            time_factor = True
        else:
            time_factor = False

        if recorded:
            if time_factor and distance_factor and distance_travelled_factor and shed_status[plate_no]['ot'] != '' and \
                    shed_status[plate_no]['it'] == '':
                shed_status[plate_no]['it'] = current_time.strftime('%H:%M:%S')
            elif trip_started and not distance_factor and not distance_travelled_factor and \
                    shed_status[plate_no]['ot'] == '':
                shed_status[plate_no]['ot'] = current_time.strftime('%H:%M:%S')

        else:
            if distance_factor and time_factor and shed_status[plate_no]['ot'] != '' and \
                    shed_status[plate_no]['it'] == "":
                shed_status[plate_no]['it'] = current_time.strftime('%H:%M:%S')
            elif not distance_factor and trip_started and shed_status[plate_no]['ot'] == "":
                shed_status[plate_no]['ot'] = current_time.strftime('%H:%M:%S')


def main():
    depots_lat_long = load_depot_data()

    while True:
        st = time.time()

        buss_gps_data = get_bus_gps_data()
        bus_timing = process_start_stop_times()
        filter_buses(buss_gps_data, depots_lat_long, bus_timing)

        en = time.time()
        with open('convert.txt', 'w') as convert_file:
            convert_file.write(json.dumps(shed_status))
        print(en - st)
        time.sleep(180 - (en - st) % 60)


if __name__ == '__main__':
    main()
