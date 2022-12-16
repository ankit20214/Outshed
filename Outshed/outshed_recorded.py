import sqlite3
import requests
import json
from datetime import datetime,timedelta
from geopy.distance import geodesic
from shapely.geometry import Point, Polygon
import pandas as pd
import time
import depots_data

# https://depot.chartr.in/get_depot_data/2022/07/25/rhd-2/morning
def load_manual_data(buses):
    morning_timings = {}
    evening_timings = {}
    a = requests.get('https://depot.chartr.in/get_all_depot_data/2022/08/03')
    for d in a.json():
        if d['bus_number'] in buses and d['shift'] == 'm':
            morning_timings[d['bus_number']] = [d['ot'], d['it']]
        if d['bus_number'] in buses and d['shift'] == 'e':
            evening_timings[d['bus_number']] = [d['ot'], d['it']]

    return morning_timings, evening_timings


def binary_search_time(data_lat_long, low, high, start_time):
    while low < high:
        mid = (low + high) // 2
        if data_lat_long[mid][-1] < start_time:
            low = mid + 1
        else:
            high = mid
    return low


def find_outshed_inshed_timings(bus_lat_long_data, start_time, depot_polygon):
    index = binary_search_time(bus_lat_long_data, 0, len(bus_lat_long_data), start_time)
    bus_lat_long_data = bus_lat_long_data[index:]

    outhsed_time = ''
    inshed_time = ''

    if len(bus_lat_long_data) == 0:
        print("No data found")
        return False
    
    outshed_index = -1  # -1 means not outshed
    inshed_ind = -1  # -1 means not inshed
    for i in range(len(bus_lat_long_data)):
        polygon = depot_polygon['tkd']
        p1 = Point(bus_lat_long_data[i][0], bus_lat_long_data[i][1])
        if not p1.within(polygon):
            if i - 20 >= 0:

                dist = geodesic((bus_lat_long_data[i][0], bus_lat_long_data[i][1]),
                                (bus_lat_long_data[i - 20][0], bus_lat_long_data[i - 20][1])).meters
                if dist >= 300:
                    outhsed_time = datetime.fromtimestamp(bus_lat_long_data[i][2]).strftime('%Y/%m/%d %H:%M:%S')
                    outshed_index = i
                    break

    if outshed_index != -1:
        for i in range(outshed_index + 1, len(bus_lat_long_data)):
            p1 = Point(bus_lat_long_data[i][0], bus_lat_long_data[i][1])
            if p1.within(polygon):
                if i - 20 >= 0:

                    dist = geodesic((bus_lat_long_data[i][0], bus_lat_long_data[i][1]),
                                    (bus_lat_long_data[i - 20][0], bus_lat_long_data[i - 20][1])).meters
                    if dist <=50:
                        inshed_time = datetime.fromtimestamp(bus_lat_long_data[i][2]).strftime('%Y/%m/%d %H:%M:%S')
                        inshed_index = i
                        break

    return outhsed_time, inshed_time, inshed_ind


depot_polygons = depots_data.load_depot_polygons()
df = pd.read_csv('../all_fleet/dtc_tcil_fleet.csv')
df_mod = df.loc[df['depot'] == 'tkd']
bus_list = df_mod['bus_reg'].tolist()
buses = bus_list
ot_it_timings_morning_shift = {}
ot_it_timings_evening_shift = {}

for bus in buses:
    ot_it_timings_morning_shift[bus] = {'ot': '', 'it': ''}
    ot_it_timings_evening_shift[bus] = {'ot': '', 'it': ''}

db_file = "/home/alchemist/Desktop/DTC/bus_movements_2022_08_dtc_raw/bus_movements_2022_08_03.db"
con = sqlite3.connect(db_file)
cur = con.cursor()

manual_m_timings, manual_e_timings = load_manual_data(buses)
start_time = time.time()
for bus in buses:
    data_lat = [a for a in
                cur.execute(f"SELECT lat,lng,vehicle_timestamp,time FROM vehicle_feed WHERE vehicle_id == '{bus}' ")]
    if len(data_lat) == 0:
        print("No data available for", bus)
        continue

    final_data = [data_lat[0]]
    for i in range(1, len(data_lat)):
        if data_lat[i] != final_data[-1]:
            final_data += [data_lat[i]]

    data_lat = final_data

    data_lat = [[float(data_lat[i][0]), float(data_lat[i][1]), int(data_lat[i][2]), data_lat[i][-1]] for i in
                range(len(data_lat))]

    ot_time, it_time, inshed_index = find_outshed_inshed_timings(data_lat, '00:00:00', depot_polygons)
    ot_it_timings_morning_shift[bus]['ot'] = ot_time
    ot_it_timings_morning_shift[bus]['it'] = it_time

    print(bus, ot_time, it_time)
    if ot_time != '' and  ot_time.split()[1] > '12:00:00':
        ot_it_timings_morning_shift[bus]['ot'] = ''
        ot_it_timings_morning_shift[bus]['it'] = ''
        ot_it_timings_evening_shift[bus]['ot'] = ot_time
        ot_it_timings_evening_shift[bus]['it'] = it_time
    elif inshed_index != -1:
        evening_shift_time = data_lat[inshed_index + 1][-1]
        ot_time, it_time, inshed_index = find_outshed_inshed_timings(data_lat, evening_shift_time, depot_polygons)
        ot_it_timings_evening_shift[bus]['ot'] = ot_time
        ot_it_timings_evening_shift[bus]['it'] = it_time

end_time = time.time()
print("Comparing the morning shift timings")
for k in ot_it_timings_morning_shift.keys():
    print(k, ":", ot_it_timings_morning_shift[k], manual_m_timings[k])
print("\n \n")
print("Comparing the evening shift timings")
for k in ot_it_timings_evening_shift.keys():
    print(k, ":", ot_it_timings_evening_shift[k], manual_e_timings[k])

file = open('Kalkaji_12_08_2022_morning_shift.txt', 'w')
file.write(json.dumps(ot_it_timings_morning_shift, indent=4))
file.close()

file = open('Kalkaji_12_08_2022_evening_shift.txt', 'w')
file.write(json.dumps(ot_it_timings_evening_shift, indent=4))
file.close()
print("Time taken:", end_time - start_time)
print()
print()
print()

df_final = pd.DataFrame(columns=['bus', 'Manual outshed', 'Manual inshed', 'Code-outshed', 'Code -inshed'])

for k in ot_it_timings_morning_shift.keys():
    df_final.loc[len(df_final.index)] = [k,manual_m_timings[k][0],manual_m_timings[k][1], ot_it_timings_morning_shift[k]['ot'], ot_it_timings_morning_shift[k]['it']]

print(df_final)
