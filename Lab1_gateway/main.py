# Dashboard: https://demo.thingsboard.io/dashboard/8e2235a0-7831-11ec-9ed9-f9294d38ab44?publicId=758b7b80-713a-11ec-9a90-af0223be0666
print("Xin chào ThingsBoard")
import paho.mqtt.client as mqttclient
import time
import json
import geocoder         #Geocoder libary
import serial.tools.list_ports

mess = ""
bbc_port="COM5"
if len(bbc_port)>0:
    ser=serial.Serial(port=bbc_port,baudrate=115200)
def converse(name):
    swich={
        'HUMI':"humidity",
        'TEMP':"temperature",
        'LIGHT':"light"
    }
    return swich.get(name)

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    #TODO
    id,name,value=splitData
    name=converse(name)
    collect_data={name:int(value)}
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
def readSerial():
    bytesToread = ser.inWaiting()
    if (bytesToread>0):
        global mess
        mess = mess + ser.read(bytesToread).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
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
    cmd=""
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/LED', json.dumps(temp_data), 1)
            cmd += "!4:LED:" + str(temp_data['value'])
        if jsonobj['method'] == "setPump":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/PUMP', json.dumps(temp_data), 1)
            cmd += "!5:PUMP:" + str(temp_data['value'])
    except:
        pass

    if len(bbc_port)>0:
        ser.write((str(cmd) + "#").encode())
        print("msg control has been sent:" + cmd)

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
    return g.latlng

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

counter = 0
while True:
    #Dynamic update the coordinate
    # latitude, longitude = getLocation()
    # collect_data = {'temperature': temp, 'humidity': humi, 'light': light_intesity,
    #                 'longitude': longitude,  'latitude': latitude}
    # temp += 1
    # humi += 1
    # light_intesity += 1
    # client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    # time.sleep(10)
    if (len(bbc_port) > 0):
        readSerial()
    time.sleep(1)