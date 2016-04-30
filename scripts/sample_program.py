#!/usr/bin/env python

from datetime import datetime
import csv,glob,sys,os,json
from fitparse import Activity
from decimal import *
from plot_picture import *

com_path = 'C:/Users/sean/Desktop/bOMDIC/Fit_data/'
PROJECT_PATH = os.path.realpath(os.path.join(sys.path[0], '..'))
sys.path.append(PROJECT_PATH)

csv_dict = {"time":0,"distance":0,"heartrate":0,"velocity_smooth":0,"lat":0,"long":0,"altitude":0,"watts":0,"cadence":0,"temp":0,"grade_smooth":0}

quiet = 'quiet' in sys.argv or '-q' in sys.argv
filenames = None

if len(sys.argv) >= 2:
    filenames = [f for f in sys.argv[1:] if os.path.exists(f)]

def write_zero(csv_dict):
    for data in csv_dict:
        if len(eval(data)) == 0:
            for count in range(len(time)):
                listname = eval(data)
                listname += [-1]

def print_record(rec, ):
    global record_number, time,distance,heartrate,velocity_smooth ,lat,long,altitude,watts,cadence,temp,grade_smooth
    csv_dict = {"time":0,"distance":0,"heartrate":0,"velocity_smooth":0,"lat":0,"long":0,"altitude":0,"watts":0,"cadence":0,"temp":0,"grade_smooth":0}
    global header,header_dict,header_csv

    record_number += 1
    # time_stamp = 0
    total_sec = 0
    # print ("-- %d. #%d: %s (%d entries) " % (record_number, rec.num, rec.type.name, len(rec.fields))).ljust(60, '-')
    for field in rec.fields:
        to_print = "%s [%s]: %s" % (field.name, field.type.name, field.data)

        if field.data is not None and field.units:
            to_print += " [%s]" % field.units
        to_print += " [%d]" % total_sec

        if(header == True):
            if(field.name == "timestamp"):
                header_csv += eval('['+str(header_dict)+']')
                header_dict = {"time":str(field.data)}
            else:
                header_dict[field.name] = str(field.data)

        if field.name == 'timestamp':
            total_sec = field.data.hour*3600 + field.data.minute*60 + field.data.second
        if field.name == 'distance':
            header = False
            for data in csv_dict:
                if(csv_dict[data] < csv_dict["time"]):
                    list = eval(data)
                    list += [-1]
                    csv_dict[data] += 1
            time += [total_sec]
            csv_dict["time"] += 1
            distance += [field.data]
            csv_dict["distance"] += 1
        if field.name == 'heart_rate':
            heartrate += [field.data]
            csv_dict["heartrate"] += 1
        if field.name == 'speed':
            velocity_smooth  += [field.data]
            csv_dict["velocity_smooth"] += 1
        if field.name == 'position_lat':
            if(field.data!=None):
                lat += [field.data*(180/float(pow(2,31)))]
                csv_dict["lat"] += 1
        if field.name == 'position_long':
            if(field.data!=None):
                long += [field.data*(180/float(pow(2,31)))]
                csv_dict["long"] += 1
        if field.name == 'altitude':
            altitude += [field.data]
            csv_dict["altitude"] += 1
        if field.name == 'power':
            if(field.data!=None):
                watts += [field.data]
                csv_dict["watts"] += 1
        if field.name == 'cadence':
            cadence += [field.data]
            csv_dict["cadence"] += 1
        if field.name == 'temperature':
            temp += [field.data]
            csv_dict["temp"] += 1

    for data in csv_dict:
        if(csv_dict[data] < csv_dict["time"]):
            list = eval(data)
            list += [-1]
            csv_dict[data] += 1

if not filenames:
    count = 0
    for fname in glob.glob(com_path+'*.fit'):
        time,distance,heartrate,velocity_smooth ,lat,long,altitude,watts,cadence,temp,grade_smooth = [],[],[],[],[],[],[],[],[],[],[]
        header,header_dict,header_csv = True,{},[] #for create header.json

        count += 1

        print fname

        print_hook_func = None
        if not quiet:
            print_hook_func = print_record

        record_number = 0
        a = Activity(fname)
        a.parse(hook_func=print_hook_func)

        if time != []:
            min_time = min(time)
            for i in range(len(time)):
                time[i] = time[i] - min_time

            write_zero(csv_dict)

            ID = fname[51:-4]
            if len(distance) != 0:
                distance_max = max(distance) / 1000
            else:
                distance_max = 0
            if len(velocity_smooth) != 0:
                speed_everage = sum(velocity_smooth) / float(len(velocity_smooth))
            else:
                speed_everage = 0
            if max(heartrate) > 0:
                total,length = 0,0
                for rate in heartrate:
                    if(rate > 0):
                        total += rate
                        length += 1
                heartrate_average = total / float(length)
                file_path = com_path+'Fit_'+str(ID)+'_'+str('%.2f' % distance_max)+'km_'+str('%.2f' % speed_everage)+'kmph_'+str('%.2f' % heartrate_average)+'bpm'
            else:
                file_path = com_path+'Fit_'+str(ID)+'_'+str('%.2f' % distance_max)+'km_'+str('%.2f' % speed_everage)+'kmph'


            if not os.path.exists(file_path):
                os.makedirs(file_path)

            with open(file_path+'/'+ID+'.csv', 'wb') as f:  # Just use 'w' mode in 3.x
                w = csv.DictWriter(f, csv_dict.keys())
                w.writeheader()
                for i in range(len(time)):
                    w.writerow(dict((name, eval(name)[i]) for name in csv_dict.keys()))
                f.close()

            with open(file_path+"/"+ID+".json","w") as header_json:
                json.dump(header_csv,header_json,ensure_ascii=False)
                header_json.close()

            for data in csv_dict:
                csv_dict[data] = eval(data)
            data_plot(csv_dict,file_path)

            with open(com_path+'direct_table.csv','ab') as direct:
                w = csv.writer(direct)
                table = [ID,file_path]
                w.writerow(table)
                direct.close()

            # a = datetime.strptime('30/03/09 16:31:32', '%d/%m/%y %H:%M:%S')

            # print('total_sec = {}'.format(a.hour*3600 + a.minute*60 + a.second))
