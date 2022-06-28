# Dashboard: https://demo.thingsboard.io/dashboard/8e2235a0-7831-11ec-9ed9-f9294d38ab44?publicId=758b7b80-713a-11ec-9a90-af0223be0666
print("Xin chào ThingsBoard")
import paho.mqtt.client as mqttclient
import time
import json
import geocoder         #Geocoder libary
import serial.tools.list_ports
from ai import *
import time

timer_counter=0
timer_flag=0
mess = ""
bbc_port=""
serial_data_recv=0
mqtt_data_recv=0
ack={}
data={}
if len(bbc_port)>0:
    ser=serial.Serial(port=bbc_port,baudrate=115200)

def sendData():
    if data!={}:
        client.publish('v1/devices/me/telemetry', json.dumps(data), 1)
        print("Published: " + str(collect_data))
def sendACK():
    ack={'ACK':0}
    client.publish('v1/devices/me/attributes', json.dumps(ack), 1)
def setTimer(counter):
    global timer_counter, timer_flag
    timer_counter=counter
    timer_flag=0
def runTimer():
    global timer_counter,timer_flag
    if timer_counter>0:
        timer_counter-=1
        if timer_counter==0:
            timer_flag=1
def cancelTimer():
    global timer_counter,timer_flag
    timer_counter=0
    timer_flag=0


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    #TODO
    if (len(splitData)==3):
        id,name,value=splitData
        # if id == "1":
        #     name="temperature"
        # elif id == "2":
        #     name = "light"
        # PHAN BIET DATA BANG NAME THAY VI SU DUNG ID NODE CHO PHU HOP LAB4
        # collect_data = {name: int(value)}
        # client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
        # print("Published: " + str(collect_data))
        if name == "TEMP":
            name = "temperature"
            collect_data = {name: int(value)}
            return collect_data
            # client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
            # print("Published: " + str(collect_data))
        elif name == "LIGHT":
            name = "light"
            collect_data = {name: int(value)}
            return collect_data
            # client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
            # print("Published: " + str(collect_data))
def readSerial():
    bytesToread = ser.inWaiting()
    if (bytesToread>0):
        global mess,data,serial_data_recv
        serial_data_recv = 1
        mess = mess + ser.read(bytesToread).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            data=processData(mess[start:end + 1])
            if (end==len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]



BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "BhNX10fgoiJfjVoJhSEz"


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd=0
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['valueLed'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            if str(temp_data['valueLed']) == "True":
                cmd = 1
            else:
                cmd = 2

        if jsonobj['method'] == "setFAN":
            temp_data['valueFan'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            if str(temp_data['valueFan']) == "True":
                cmd = 3
            else:
                cmd = 4
    except:
        pass

    if len(bbc_port)>0:
        ser.write((str(cmd) + "#").encode())

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")

def getLocation():
    # retrieve my own ip address
    g = geocoder.ip('me')
    # Optain the latitude, longitude
    print(g)
    return g.latlng


cmd = ""


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

temp = 30
humi = 50
light_intesity = 100

counter_cap = 0






while True:
    collect_data = {'temperature': temp, 'humidity': humi, 'light': light_intesity}
    temp += 1
    humi += 1
    light_intesity += 1
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    client.on_subscribe
    # if (len(bbc_port) > 0):
    #      readSerial()
    counter_cap+=1
    if counter_cap>=5:
        counter_cap = 0
        capture_img()
        #Extract
        rs,accuracy=ai_detection()
        #print
        print("Ket qua:", str(rs))
        print("Do chinh xac:", str(accuracy))
        #package
        ai_data={'result':str(rs) , 'accuracy': float(accuracy)*100}
        #publish
        client.publish('v1/devices/me/telemetry', json.dumps(ai_data), 1)
    time.sleep(1)