# -*- coding: utf-8 -*-
"""
Created on Thu May  7 15:10:50 2020

@author: jhruo
"""

import json
import io
import re
import requests
import numpy as np
import json
import time
import matplotlib.pyplot as plt
from influxdb import InfluxDBClient
from datetime import datetime

julkaisu = "nom9"
lpstime = 720

def byteswap(x):
    l=len(x)
    d = x[l-2:l]
    d = d + x[l-4:l-2]
    d = d + x[l-6:l-4]
    d = d + x[l-8:l-6]
    return (d)


def hex_float(d):
    s = (int(d,16)) >> 31
    e = ((int(d,16)) & 0x7f800000)>>23
    m = ((int(d,16)) & 0x007fffff)
    if (s==1):
        s=-1
    else:
        s=1
    r=s*(2**(e-127))*(1.0+float(m)/float(1<<23))
    return (r)

#strhx="02,63,d8,96,01,00,56,d2,9c,bb,50,e0,10,c0,56,d2,1c,41"
#"       1  2  3  4  5  6  7  8  9  0  1  2  3  4  5  6  7  8 "

#strhx  = "0266676692424303"
#strhx = "026435FA0D000FADBCBEC3EB174114783740713DAABF295C8F3E66667640"

def hex2json (strh,cllctn):
    
    output = io.StringIO()    
    file = "generalhex2num.json"
    with open (file) as jdata:
        jsonData = json.load(jdata)
    jsonData = jsonData[cllctn]

    i=0
    j=0
    data=""
    q = "\""

    for type in jsonData['typ']:
        if type == "byte":
            n = 2
            rslt=int("0x"+strh[j:j+n],16)
            srslt=str(rslt)
            output.write(q + jsonData['out'][i] + q + ": " + srslt + ",")
        if type == "int16":
            n = 4
            data=byteswap(strh[j:j+n]+"0000")
            rslt=int("0x"+data,16) 
            srslt=str(rslt)
            output.write(q + jsonData['out'][i] + q + ": " + srslt + ",")
        if type == "int32":
            n = 8
            data=byteswap(strh[j:j+n])
            rslt=int("0x"+data,16) 
            srslt=str(rslt)
            output.write(q + jsonData['out'][i] + q + ": " + srslt + ",")
        if type == "sint32":
            n = 8
            data=byteswap(strh[j:j+n])
            rslt=int("0x"+data,16) 
            if rslt >= 0x80000000:
                rslt -= 0x100000000
            srslt=str(rslt)
            output.write(q + jsonData['out'][i] + q + ": " + srslt + ",")
        if type == "float32":
            n = 8
            data = byteswap(strh[j:j+n])
            data = "0x"+data
            rslt= hex_float(data)
            srslt=str(rslt)
            output.write(q + jsonData['out'][i] + q + ": " + srslt + ",")
        j=j+n
        i=i+1
    return(output.getvalue())

def data2json (data):

    k=0
    p2j="{"
    p2jr=""
    strhx=""
    collection = 'MIMU6f13'

    strhx =  data["m0"]["POTKU6d"]   
    stype =  data["m0"]["POTKU6d"][3:5]
    stpm  =  data["m"+str(k)]["POTKU6t"]
    
    if (stype == "64"):
        collection = 'MIMU6f13Hz'
    else:
        collection = 'HR'
            
    while(k<len(data)-2):
        strhxx=re.sub('[,",\n]','',strhx)  #remove extra 
        p2jr = hex2json(strhxx,collection)
        p2j = p2j + "\"m" + str(k) + "\":{" + "\"mtstp\":" + "\"" +str(stpm)+ "\"," + p2jr[0:len(p2jr)-1] + "},"
        strhx =  data["m"+str(k)]["POTKU6d"] 
        stpm  =  data["m"+str(k)]["POTKU6t"]
        stype =  data["m"+str(k)]["POTKU6d"] [3:5]    
        if (stype == "64"):
            collection = 'MIMU6f13Hz'
        else:
            collection = 'HR'
        k=k+1
    p2j = p2j + "\"version\": \"1.0\"}"  #make valid json
        
    return(p2j)

    
#3xample use

#file = "/Users/jhruo/OneDrive/Documents/Python development HR hengitys/data17052021sykehengitys.json"
#file = "/Users/jhruo/OneDrive/Desktop/lastensairaala/potku3IMU330062020.json"
#with open (file) as jdata:
#   jsData = json.load(jdata)


#requests.get("http://193.211.7.69:8100/message","msg=psw:saeed,cmd:mpt")
requests.get("http://192.168.0.117:8100/message","msg=psw:saeed,cmd:mpt")
time.sleep(lpstime)
#r = requests.get("http://193.211.7.69:8100/message","msg=psw:saeed,cmd:snd")
#r = requests.get("http://192.168.0.117:8100/message","msg=psw:saeed,cmd:snd")
r = requests.get("http://192.168.0.117:8100/message","msg=psw:saeed,cmd:snd")

print(r.json)

jsData = r.json()

sh=data2json(jsData)
#print(sh)
jsonData = json.loads(sh)

myHRT  = []
myBRT  = []
myHRS = []
myHR  = []
myRR  = []
myBRx = []
myBRz = []
myBRy = []
myBRxr = []
myBRzr = []
myBRyr = []
data  = []

payload = []

client = InfluxDBClient('localhost',8086)
client.switch_database('omsound')

numberofrecords = len(jsonData)
print(numberofrecords)

HRi = 0
BRi = 0
IT = 0

#IT = int(jsonData["m0"]["mtstp"])
for i in range(0,numberofrecords-1):
    if (jsonData["m"+str(i)]["ref"] == 102):
        HRT       =  int(jsonData["m"+str(i)]["mtstp"]) * 1000
        myHRT.append(int(jsonData["m"+str(i)]["mtstp"]))
        HR        = float(jsonData["m"+str(i)]["hr"])
        myHR.append(float(jsonData["m"+str(i)]["hr"]))
        RR        = int(jsonData["m"+str(i)]["RR"])
        myRR.append(int(jsonData["m"+str(i)]["RR"]))
        data = {
        "measurement": "omMVHRT",
        "tags": {
            "julkaisu": julkaisu,
            "laite": "MvHR",
            "kohde": "Jari"
            },
        "time": HRT,  # nonoseconds
        "fields": {
            "HR":  HR,
            "RR":  RR
            }
        }
        payload.append(data)
        client.write_points(payload)        
        HRi = HRi + 1
    if (jsonData["m"+str(i)]["ref"] == 100): 
        BRT      =   int(jsonData["m"+str(i)]["mtstp"]) * 1000
        myBRT.append(int(jsonData["m"+str(i)]["mtstp"]))
        BRx      =   jsonData["m"+str(i)]["x1"]
        myBRx.append(jsonData["m"+str(i)]["x1"])
        BRz      =   jsonData["m"+str(i)]["z1"] 
        myBRz.append(jsonData["m"+str(i)]["z1"])
        BRy      =   jsonData["m"+str(i)]["y1"] 
        myBRy.append(jsonData["m"+str(i)]["y1"])
        BRxr      =   jsonData["m"+str(i)]["a1"]
        myBRxr.append(jsonData["m"+str(i)]["a1"])
        BRzr      =   jsonData["m"+str(i)]["c1"] 
        myBRzr.append(jsonData["m"+str(i)]["c1"])
        BRyr      =   jsonData["m"+str(i)]["b1"] 
        myBRyr.append(jsonData["m"+str(i)]["b1"])
        data = {
        "measurement": "omMVBR",
        "tags": {
            "julkaisu": julkaisu,
            "laite":  "MvIMU",
            "kohde":  "Jari"
            },
        "time": BRT, # nanoseconds
        "fields": {
            "BRx":  BRx,
            "BRy":  BRy,
            "BRz":  BRz,
            "BRxr":  BRxr,
            "BRyr":  BRyr,
            "BRzr":  BRzr            
            }
        }
        payload.append(data)
        client.write_points(payload)        
        BRi = BRi + 1

maxRR = max(myRR)
minRR = min(myRR)
aveRR = np.mean(myRR)
stdRR = np.std(myRR)
print("minRR and maxRR and aveRR and stdRR", minRR, maxRR, aveRR, stdRR)

maxHR = max(myHR)
minHR = min(myHR)
aveHR = np.mean(myHR)
stdHR = np.std(myHR)
print("minHR and maxHR and aveHR and stdHR", minHR, maxHR, aveHR, stdHR)


#plt.subplot(222)
starttime = myHRT[0]
endtime  = myHRT[HRi-1]  
plt.title("HR data")
plt.axis([starttime, endtime, 0, 180])
plt.plot(myHRT,myHR)
plt.show()

#plt.subplot(222)
plt.title("RR data")
plt.axis([starttime, endtime, 0, 1500])
plt.plot(myHRT,myRR)
plt.show()

maxBRx = max(myBRx)
minBRx = min(myBRx)
aveBRx = np.mean(myBRx)
stdBRx = np.std(myBRx)
print("minBR and maxBR and aveBR and stdBR", minBRx, maxBRx, aveBRx, stdBRx)

starttime = myBRT[0]
endtime  = myBRT[BRi-1]
plt.title("BHx data")
plt.axis([starttime, endtime, -5, 5])
plt.plot(myBRT,myBRx)
plt.show()

maxBRz = max(myBRz)
minBRz = min(myBRz)
aveBRz = np.mean(myBRz)
stdBRz = np.std(myBRz)
print("minBR and maxBR and aveBR and stdBR", minBRz, maxBRz, aveBRz, stdBRz)

plt.title("BHz data")
plt.axis([starttime, endtime, -2, 7])
plt.plot(myBRT,myBRz)
plt.show()

maxBRy = max(myBRy)
minBRy = min(myBRy)
aveBRy = np.mean(myBRy)
stdBRy = np.std(myBRy)
print("minBR and maxBR and aveBR and stdBR", minBRy, maxBRy, aveBRy, stdBRy)

plt.title("BHy data")
plt.axis([starttime, endtime, minBRy, maxBRy])
plt.plot(myBRT,myBRy)
plt.show()



#print(hex2json(strhx,"MIMU6f13"))
        
