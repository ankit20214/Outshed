import requests
import sys

def load_fron_it_ot():

    buses = {}
    a = requests.get('https://depot.chartr.in/get_all_depot_data/2022/08/12')
    for d in a.json():
        buses[d['bus_number']] = 0

    return buses

def get_ot_it_times():
    a = requests.get('https://depot.chartr.in/get_all_depot_data/2022/08/12')
    t_str1 = ['DL1PC8476', 'DL1PC9485', 'DL1PC9818', 'DL1PC9811', 'DL1PC8524', 'DL1PC9486', 'DL1PC9877', 'DL1PC9917', 'DL1PC9482','DL1PC7833']
    data = {}
    for d in a.json():
        if d['bus_number'] in t_str1:
            if d['bus_number'] not in data.keys():
                data[d['bus_number']] = [[d['ot'],d['it']]]
            else:
                data[d['bus_number']] += [[d['ot'],d['it']]]
    print(data)

def get_duties():


    file = open("/home/alchemist/Desktop/DTC/tcil_all_buses_duties_db.txt_12_08_2022_23_34")
    duties_data  = file.readlines()
    file.close()


    duties_data = [duties_data[i].strip().split(',') for i in range(1,len(duties_data))]
    plate_depot_map = {}
    bus_duty_map = {}

    for i in range(len(duties_data)):

        try:
            plate_no = duties_data[i][-6]
        except:
            print(duties_data[i])
            sys.exit()

        
        if plate_no not in plate_depot_map.keys():
            plate_depot_map[plate_no] = duties_data[i][3]

        if plate_no not in bus_duty_map.keys():
            bus_duty_map[plate_no] = [duties_data[i][-5]]
        else:
            bus_duty_map[plate_no] += [duties_data[i][-5]]

    print(len(bus_duty_map),len(plate_depot_map))
    return bus_duty_map,plate_depot_map


buses = load_fron_it_ot()
bus_duty_map,plate_depot_map = get_duties()


final_commmon_bus = []
for k in buses.keys():
    if k in plate_depot_map.keys():
        final_commmon_bus += [k]

# print(buses.keys())
# print(bus_duty_map.keys())

# print(final_commmon_bus)
# get_ot_it_times()


# DL1PC8476

# {'DL1PC8476': [['12/08/2022, 10:26:56', '12/08/2022, 14:16:28'],
 # ['12/08/2022, 16:48:40', '13/08/2022, 05:03:29']],

 #  'DL1PC9485': [['12/08/2022, 10:19:31', '12/08/2022, 13:08:58'], 
 #  ['12/08/2022, 16:31:55', '13/08/2022, 05:03:00']], 

 #  'DL1PC9818': [['12/08/2022, 10:31:05', '12/08/2022, 15:54:28'], 
 #  ['12/08/2022, 16:50:04', '13/08/2022, 05:02:34']], 

 #  'DL1PC9811': [['12/08/2022, 10:26:15', '12/08/2022, 16:24:46'], 
 #  ['', '']], 

 #  'DL1PC8524': [['12/08/2022, 10:26:43', '12/08/2022, 13:09:05'],
 #   ['12/08/2022, 16:30:53', '13/08/2022, 05:03:27']], 

 #   'DL1PC9486': [['12/08/2022, 11:35:42', '12/08/2022, 12:40:49'], 
 #   ['12/08/2022, 16:28:58', '13/08/2022, 05:03:01']], 

 #   'DL1PC9877': [['12/08/2022, 12:05:57', '12/08/2022, 14:18:19'], 
 #   ['12/08/2022, 16:54:19', '13/08/2022, 05:02:30']], 
   
 #   'DL1PC9917': [['12/08/2022, 10:25:49', '12/08/2022, 13:08:41'], 
 #   ['12/08/2022, 16:31:39', '13/08/2022, 05:02:29']], 

 #   'DL1PC9482': [['12/08/2022, 10:29:24', '12/08/2022, 12:39:07'], ['', '']]

# 'DL1PC7833': [['', ''], ['12/08/2022, 16:37:44', '13/08/2022, 05:04:20']]