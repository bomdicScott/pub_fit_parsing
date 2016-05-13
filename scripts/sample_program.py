#!/usr/bin/env python

import csv,glob,sys,os,json,time as times
from fitparse import Activity
from plot_picture import *
from GPS_route_plot import *

com_path = 'C:/Users/sean/Desktop/bOMDIC/Fit_data/'
PROJECT_PATH = os.path.realpath(os.path.join(sys.path[0], '..'))
sys.path.append(PROJECT_PATH)

compare_optional = False #if false then all the fit data will be parsing

def print_record(rec, ):
    global time,distance,heartrate,velocity_smooth ,lat,lng,altitude,watts,cadence,temp,grade_smooth
    global header,header_dict,header_csv,csv_dict,missing_count

    total_sec = -1
    for field in rec.fields:
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
            #check None value
            for data in csv_dict:
                if(csv_dict[data] < csv_dict["time"]):
                    list = eval(data)
                    list += [-1]
                    csv_dict[data] += 1
                    missing_count[data]+=1
            #===========================
            time += [total_sec]
            csv_dict["time"] += 1
            if(field.data!=None and field.data!=0):
                distance += [field.data]
                csv_dict["distance"] += 1
        if field.name == 'heart_rate':
            if(field.data!=None and field.data!=0):
                heartrate += [field.data]
                csv_dict["heartrate"] += 1
        if field.name == 'speed':
            if(field.data!=None and field.data!=0):
                velocity_smooth  += [field.data]
                csv_dict["velocity_smooth"] += 1
        if field.name == 'position_lat':
            if(field.data!=None and field.data!=0):
                lat += [field.data*(180/float(pow(2,31)))]
                csv_dict["lat"] += 1
        if field.name == 'position_long':
            if(field.data!=None and field.data!=0):
                lng += [field.data*(180/float(pow(2,31)))]
                csv_dict["lng"] += 1
        if field.name == 'altitude':
            if(field.data!=None and field.data!=0):
                altitude += [field.data]
                csv_dict["altitude"] += 1
        if field.name == 'power':
            if(field.data!=None and field.data!=0):
                watts += [field.data]
                csv_dict["watts"] += 1
        if field.name == 'cadence':
            if(field.data!=None and field.data!=0):
                cadence += [field.data]
                csv_dict["cadence"] += 1
        if field.name == 'temperature':
            if(field.data!=None and field.data!=0):
                temp += [field.data]
                csv_dict["temp"] += 1


if __name__=="__main__":
    for fname in glob.glob(com_path+'*.fit'):

        time,distance,heartrate,velocity_smooth ,lat,lng,altitude,watts,cadence,temp,grade_smooth = [],[],[],[],[],[],[],[],[],[],[]
        header,header_dict,header_csv = True,{},[] #for create header.json
        csv_dict = {"time":0,"distance":0,"heartrate":0,"velocity_smooth":0,"lat":0,"lng":0,"altitude":0,"watts":0,"cadence":0,"temp":0,"grade_smooth":0}
        missing_count = {"time":0,"distance":0,"heartrate":0,"velocity_smooth":0,"lat":0,"lng":0,"altitude":0,"watts":0,"cadence":0,"temp":0,"grade_smooth":0}

        fit_id_list = []
        try:
            direct = open(com_path+"direct_table.csv","rb")
            for fit_id in csv.reader(direct):
                fit_id_list += [fit_id[0]]
            direct.close()
        except:
            pass

        ID = fname[38:-4]#depend on your com_path
        if ID not in fit_id_list:
            print fname+" Start parsing!!"
            time_start = times.time()

            a = Activity(fname)
            a.parse(hook_func=print_record)

            #check None value
            for data in csv_dict:
                if(csv_dict[data] < csv_dict["time"]):
                    list = eval(data)
                    list += [-1]
                    csv_dict[data] += 1
                    missing_count[data]+=1

            if time != []:
                min_time = min(time)
                for i in range(len(time)):
                    time[i] = time[i] - min_time

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

                with open(file_path+"/missing_rate.txt",'wb') as missing:
                    data_len = csv_dict["time"]
                    for data_name in missing_count:
                        rate = missing_count[data_name]*100 / float(data_len)
                        missing.write(data_name+" : "+str('%.4f' % rate)+"\n")
                with open(file_path+'/'+ID+'.csv', 'wb') as f:
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

                lat,lng = clean_data(lat,lng)
                if (lat != []):
                    draw_GPS_route(lat,lng,3).save(file_path+"/GPS_route.png")
                else:
                    print ID+" has no route picture,sorry~~~"

                with open(com_path+'direct_table.csv','ab') as direct:
                    table = [ID,file_path]
                    csv.writer(direct).writerow(table)
                    direct.close()

                print "complete parsing Use: "+str('%.2f' % float(times.time()-time_start))+" second."
