import datetime, time
from geopy.distance import geodesic
import requests
from shapely.geometry import Point, Polygon
import pandas as pd
import json
import depots_data

bus_ot_it_timings_morning_shift = {}
bus_ot_it_timings_evening_shift = {}
recorded_bus_gps_data = {}


def load_polygons():
    depot_polygons = depots_data.load_depot_polygons()
    return depot_polygons


def get_bus_depot_map():
    global bus_ot_it_timings_morning_shift
    global bus_ot_it_timings_evening_shift
    df = pd.read_csv('all_buses_delhi.csv')
    buses, depot_id = list(df['reg_num']), list(df['depot'])
    bus_depot_map = {buses[i]: depot_id[i] for i in range(len(buses))}
    bus_ot_it_timings_morning_shift = {buses[i]: {"bus_number": buses[i], "ot":"", "it":"", "shift":"m"} for i in range(len(buses))}
    bus_ot_it_timings_evening_shift = {buses[i]: {"bus_number": buses[i], "ot":"", "it":"", "shift": "e"} for i in range(len(buses))}
    return bus_depot_map


def get_bus_gps_data():
    gps_data = requests.get("http://143.110.182.192:8090/tcil_all_buses_db.txt")
    dimts_data = requests.get("http://143.110.182.192:8090/tcil_all_dimts_buses_db.txt")
    gps_data = gps_data.text.split("\n")
    dimts_data = dimts_data.text.split("\n")
    gps_data = [gps_data[i].split(',') for i in range(len(gps_data))]
    dimts_data = [dimts_data[i].split(',') for i in range(len(dimts_data))]
    gps_data += dimts_data

    return gps_data


def get_bus_duties():
    data = requests.get("http://143.110.182.192:8090/depot_tool_duty_master.txt")
    data = data.text.split("\n")
    data = [data[i].split(',') for i in range(1, len(data))]

    return data


def record_gps_data(recorded_bus_gps: dict):
    gps_data = get_bus_gps_data()
    for bus_data in gps_data:
        if len(bus_data) == 14:
            if bus_data[2] not in recorded_bus_gps.keys():
                recorded_bus_gps[bus_data[2]] = [[float(bus_data[0]), float(bus_data[0])]]
            else:
                recorded_bus_gps[bus_data[2]] += [[float(bus_data[0]), float(bus_data[0])]]
                if len(recorded_bus_gps) > 10:
                    del recorded_bus_gps[bus_data[2]][0]


def check_bus_within_depot(position: list, polygon: Polygon):
    p1 = Point(position[0], position[1])
    if p1.within(polygon):
        return True
    else:
        return False


def convert_to_json(data_morning, data_evening):
    final_data = []
    for k in data_morning.keys():
        final_data.append(data_morning[k])
    for k in data_evening.keys():
        final_data.append(data_evening[k])
    dump_data = json.dumps(final_data, indent=4)
    return dump_data


def check_shed_status(bus_depot_map: dict, gps_data, recorded_bus_gps_data, depot_polygons, file):
    global bus_ot_it_timings_morning_shift
    global bus_ot_it_timings_evening_shift
    for bus_data in gps_data:
        if len(bus_data) != 14:
            continue
        bus_number = bus_data[2]
        if bus_number not in bus_depot_map.keys():
            continue
        if bus_depot_map[bus_number] not in depot_polygons.keys():
            continue
        depot_poly = depot_polygons[bus_depot_map[bus_number]]

        if bus_ot_it_timings_morning_shift[bus_number]["ot"] != "" and bus_ot_it_timings_morning_shift[bus_number]["it"] != "" and bus_ot_it_timings_evening_shift[bus_number]["ot"] != "" and bus_ot_it_timings_evening_shift[bus_number]["it"] != "":
            continue

        if bus_ot_it_timings_morning_shift[bus_number]['ot'] == '':
            if not check_bus_within_depot([float(bus_data[0]), float(bus_data[1])], depot_poly):
                prev_location = recorded_bus_gps_data[bus_number][0]
                current_location = [float(bus_data[0]), float(bus_data[1])]
                distance = geodesic(prev_location, current_location).km
                if distance > 0.3:
                    bus_ot_it_timings_morning_shift[bus_number]['ot'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        elif bus_ot_it_timings_morning_shift[bus_number]['ot'] != '' and bus_ot_it_timings_morning_shift[bus_number]['it'] == '':
            if check_bus_within_depot([float(bus_data[0]), float(bus_data[1])], depot_poly):
                prev_location = recorded_bus_gps_data[bus_number][0]
                current_location = [float(bus_data[0]), float(bus_data[1])]
                distance = geodesic(prev_location, current_location).km
                if distance < 0.05:
                    bus_ot_it_timings_morning_shift[bus_number]['it'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        elif bus_ot_it_timings_evening_shift[bus_number]['ot'] == '':
            if not check_bus_within_depot([float(bus_data[0]), float(bus_data[1])], depot_poly):
                prev_location = recorded_bus_gps_data[bus_number][0]
                current_location = [float(bus_data[0]), float(bus_data[1])]
                distance = geodesic(prev_location, current_location).km
                if distance > 0.3:
                    bus_ot_it_timings_evening_shift[bus_number]['ot'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        else:
            if check_bus_within_depot([float(bus_data[0]), float(bus_data[1])], depot_poly):
                prev_location = recorded_bus_gps_data[bus_number][0]
                current_location = [float(bus_data[0]), float(bus_data[1])]
                distance = geodesic(prev_location, current_location).km
                if distance < 0.05:
                    bus_ot_it_timings_evening_shift[bus_number]['it'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        if bus_ot_it_timings_morning_shift[bus_number]['ot'] == '' and bus_ot_it_timings_morning_shift[bus_number]['ot'] > '12:00:00':
            bus_ot_it_timings_evening_shift[bus_number]['ot'] = bus_ot_it_timings_morning_shift[bus_number]['ot']
            bus_ot_it_timings_morning_shift[bus_number]['ot'] = ''
            bus_ot_it_timings_evening_shift[bus_number]['it'] = bus_ot_it_timings_morning_shift[bus_number]['it']
            bus_ot_it_timings_morning_shift[bus_number]['it'] = ''

    json_data = convert_to_json(bus_ot_it_timings_morning_shift, bus_ot_it_timings_evening_shift)
    file.write(json_data)


def main():
    global recorded_bus_gps_data
    iteration = 1
    bus_depot_map = get_bus_depot_map()
    depot_polygons = load_polygons()
    f_name = None
    while True:
        iteration += 1
        gps_data = get_bus_gps_data()
        record_gps_data(recorded_bus_gps_data)
        if f_name is None:
            f_name = datetime.datetime.now().strftime("%d_%m_%Y") + ".json"
        if datetime.datetime.now().strftime("%H:%M:%S") == "03:00:00":
            f_name = datetime.datetime.now().strftime("%d_%m_%Y") + ".json"
        file = open(f_name, "w+")
        check_shed_status(bus_depot_map, gps_data, recorded_bus_gps_data, depot_polygons, file)
        time.sleep(10)


if __name__ == '__main__':
    main()