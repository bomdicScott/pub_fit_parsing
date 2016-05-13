from staticmap.staticmap import *

def clean_data(lat,long):
    i=0
    while(len(lat) > i):
        if(lat[i] == -1 or long[i] == -1):
            del lat[i]
            del long[i]
        else:
            i+=1
    return lat,long

def compute_color_code(stamina):
    stamina = int(stamina+0.5)
    if (stamina > 100 or stamina < 0):
        print("Your stamina must in range [ 0 , 100 ]")
        return None
    if (stamina > 50):
        return ((100-stamina)*5,0,255)
    else:
        return (255,0,int((stamina*5.1)+0.5))

def draw_GPS_route(lat,lng,width=2):
    m = StaticMap(500, 500)
    point = []
    for i in range(len(lat)):
        point.append((lng[i],lat[i]))
    point = point[::2]
    for count in range(len(point)-1):
        color=compute_color_code(count*100/float(len(point)))
        line = Line([point[count],point[count+1]], color, width)
        m.add_line(line)
    image = m.render()
    return image