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
        if type == "Int24":
            n = 6
            data=byteswap(strh[j:j+n]+"00")
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

    p2j   = "{"
    p2jr  = ""
    strhx =""
    collection = 'SEEG'
    i = 0

    strhx  =  data["m0"]["mw"] + data["m1"]["mw"]  
    st     =  data["m0"]["st"]
    strhxx =  re.sub('[,",\n]','',strhx)  #remove extra 
    p2jr   =  hex2json(strhxx,collection)
    p2j    =  p2j + "\"m" + str(i) + "\":{" + "\"st\":" + "\"" +str(st)+ "\"," + p2jr[0:len(p2jr)-1] + "},"
  
    k = 2
            
    while(k<len(data)-2):
        strhxx=re.sub('[,",\n]','',strhx)  #remove extra 
        strhx =  data["m"+str(k)]["mw"] + data["m"+str(k+1)]["mw"] 
        stpm  =  data["m"+str(k)]["st"]
        st  =  data["m"+str(k)]["st"]
        strhxx=re.sub('[,",\n]','',strhx)  #remove extra 
        p2jr = hex2json(strhxx,collection)
        print(p2jr)
        p2j = p2j + "\"m" + str(i) + "\":{" + "\"st\":" + "\"" +str(st)+ "\"," + p2jr[0:len(p2jr)-1] + "},"
        k = k + 2
        i = i + 1
    p2j = p2j + "\"version\": \"1.0\"}"  #make valid json
        
    return(p2j)

    
#3xample use

#file = "/Users/jhruo/OneDrive/Documents/Python development HR hengitys/Mindwave200521.json"
#file = "/Users/jhruo/OneDrive/Desktop/lastensairaala/potku3IMU330062020.json"
#with open (file) as jdata:
#   jsData = json.load(jdata)

#requests.get("http://212.213.64.162:8091/message","msg=psw:saeed,cmd:mpt")
#time.sleep(120)
#r = requests.get("http://212.213.64.162:8091/message","msg=psw:saeed,cmd:snd")
#jsData = r.json()

#requests.get("http://193.211.7.69:8091/message","msg=psw:saeed,cmd:mpt")
#time.sleep(30)
#r = requests.get("http://193.211.7.69:8091/message","msg=psw:saeed,cmd:snd")
#jsData = r.json()

#requests.get("http://192.168.0.117:8091/message","msg=psw:saeed,cmd:mpt")
requests.get("http://192.168.0.117:8091/message","msg=psw:saeed,cmd:mpt")

time.sleep(lpstime)
r = requests.get("http://192.168.0.117:8091/message","msg=psw:saeed,cmd:snd")
jsData = r.json()



sh=data2json(jsData)
#print(sh)
jsonData = json.loads(sh)

myTheta = []
myDelta = []
myTSTMP = []
myLAlpha = []
myHAlpha = []
myLBeta = []
myHBeta = []
myAtt = []
myMedit = []
myLGamma = []
myMGamma = []

payload = []

numberofrecords = len(jsonData)

client = InfluxDBClient('localhost',8086)
client.switch_database('omsound')

#IT = int(jsonData["m0"]["st"])
for i in range(0,numberofrecords-2):
        TSTMP    =     int(jsonData["m"+str(i)]["st"])*1000
        myTSTMP.append(int(jsonData["m"+str(i)]["st"]))
        delta    =     (float(jsonData["m"+str(i)]["Delta"])*(1.8/4096))/2000
        myDelta.append((float(jsonData["m"+str(i)]["Delta"])*(1.8/4096))/2000)
        theta    =     (float(jsonData["m"+str(i)]["Theta"])*(1.8/4096))/2000
        myTheta.append((float(jsonData["m"+str(i)]["Theta"])*(1.8/4096))/2000)
        lalpha   =      (float(jsonData["m"+str(i)]["LAlpha"])*(1.8/4096))/2000
        myLAlpha.append((float(jsonData["m"+str(i)]["LAlpha"])*(1.8/4096))/2000)
        halpha   =      (float(jsonData["m"+str(i)]["LAlpha"])*(1.8/4096))/2000
        myHAlpha.append((float(jsonData["m"+str(i)]["LAlpha"])*(1.8/4096))/2000)
        lbeta    =     (float(jsonData["m"+str(i)]["LBeta"])*(1.8/4096))/2000
        myLBeta.append((float(jsonData["m"+str(i)]["LBeta"])*(1.8/4096))/2000)
        hbeta    =     (float(jsonData["m"+str(i)]["LBeta"])*(1.8/4096))/2000
        myHBeta.append((float(jsonData["m"+str(i)]["LBeta"])*(1.8/4096))/2000)
        lgamma   =      (float(jsonData["m"+str(i)]["LGamma"])*(1.8/4096))/2000
        myLGamma.append((float(jsonData["m"+str(i)]["LGamma"])*(1.8/4096))/2000)
        mgamma   =       (float(jsonData["m"+str(i)]["MGamma"])*(1.8/4096))/2000  
        myMGamma.append((float(jsonData["m"+str(i)]["MGamma"])*(1.8/4096))/2000)
        att      =    (float(jsonData["m"+str(i)]["Att"])) 
        myAtt.append((float(jsonData["m"+str(i)]["Att"])))
        medit    =     (float(jsonData["m"+str(i)]["Medit"]))
        myMedit.append((float(jsonData["m"+str(i)]["Medit"])))
        data = {
        "measurement": "omEEG",
        "tags": {
            "julkaisu": julkaisu,
            "laite":  "EEG",
            "kohde": "Jari"
            },
        "time": TSTMP, # nanoseconds
        "fields": {
            "delta":  delta,
            "theta":  theta,
            "lalpha": lalpha,
            "halpha": halpha,
            "lbeta":  lbeta,
            "hbeta":  hbeta,
            "lgamma": lgamma,
            "mgamma": mgamma,
            "att":    att,
            "medit":  medit
#            "rtime":  datetime.now()
            }
        }
        payload.append(data)
        client.write_points(payload)        
        
maxDelta = np.max(myDelta)
minDelta = np.min(myDelta)
aveDelta = np.mean(myDelta)
stdDelta = np.std(myDelta)
print("minDelta and maxDelta and aveDelta and stdDelta", minDelta, maxDelta, aveDelta, stdDelta)

maxTheta = np.max(myTheta)
minTheta = np.min(myTheta)
aveTheta = np.mean(myTheta)
stdTheta = np.std(myTheta)
print("minTheta and maxTheta and aveTheta and stdTheta", minTheta, maxTheta, aveTheta, stdTheta)

maxLAlpha = np.max(myLAlpha)
minLAlpha = np.min(myLAlpha)
aveLAlpha = np.mean(myLAlpha)
stdLAlpha = np.std(myLAlpha)
print("minLAlpha and maxLAlpha and aveLAlpha and stdLAlpha", minLAlpha, maxLAlpha, aveLAlpha, stdLAlpha)

maxLGamma = np.max(myLGamma)
minLGamma = np.min(myLGamma)
aveLGamma = np.mean(myLGamma)
stdLGamma = np.std(myLGamma)
print("minLGamma and maxLGamma and aveLGamma and stdLGamma", minLGamma, maxLGamma, aveLGamma, stdLGamma)

maxAtt = np.max(myAtt)
minAtt = np.min(myAtt)
aveAtt = np.mean(myAtt)
stdAtt = np.std(myAtt)
print("minAtt and maxAtt and aveAtt and stdAtt", minAtt, maxAtt, aveAtt, stdAtt)

maxMedit = np.max(myMedit)
minMedit = np.min(myMedit)
aveMedit = np.mean(myMedit)
stdMedit = np.std(myMedit)
print("minMedit and maxMedit and aveMedit and stdMedit", minMedit, maxMedit, aveMedit, stdMedit)


#plt.subplot(222)
starttime = myTSTMP[0]
endtime  = myTSTMP[numberofrecords-3]
plt.title("Delta data")
plt.axis([starttime, endtime, 0, 10])
plt.plot(myTSTMP,myDelta)
plt.show()

starttime = myTSTMP[0]
endtime  = myTSTMP[numberofrecords-3]
plt.title("Theta data")
plt.axis([starttime, endtime, 0, 10])
plt.plot(myTSTMP,myTheta)
plt.show()

starttime = myTSTMP[0]
endtime  = myTSTMP[numberofrecords-3]
plt.title("LAlpha")
plt.axis([starttime, endtime, 0, 10])
plt.plot(myTSTMP,myLAlpha)
plt.show()

starttime = myTSTMP[0]
endtime  = myTSTMP[numberofrecords-3]
plt.title("myLGamma")
plt.axis([starttime, endtime, 0, 10])
plt.plot(myTSTMP,myLGamma)
plt.show()

starttime = myTSTMP[0]
endtime  = myTSTMP[numberofrecords-3]
plt.title("Att")
plt.axis([starttime, endtime, 0, 100])
plt.plot(myTSTMP,myAtt)
plt.show()

starttime = myTSTMP[0]
endtime  = myTSTMP[numberofrecords-3]
plt.title("Medit")
plt.axis([starttime, endtime, 0, 200])
plt.plot(myTSTMP,myMedit)
plt.show()