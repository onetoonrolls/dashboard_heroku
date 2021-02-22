# Flask Import
from time import time

from flask import Flask, jsonify, request, render_template, make_response

# FireBase Import
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# MQTT Import
import paho.mqtt.client as mqtt
import string
import json
import random as rd

# ref https://firebase.google.com/docs/database/admin/save-data
# Fetch the service account key JSON file contents
cred = credentials.Certificate('cpe-496-internet-of-things-firebase-adminsdk-96r5x-b5c2187998.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cpe-496-internet-of-things-default-rtdb.firebaseio.com/'
})


# MQTT Management

def on_connection(client, user_data, flag, rc):
    statuws_decoder = {  # swtich case in python style using dictionary
        0: "Successfully Connected",
        1: "Connection refused: Incorrect Protocol Version",
        2: "Connection refused: Invalid Client Identifier",
        3: "Connection refused: Server Unavailable",
        4: "Connection refused: Bad Username/Password",
        5: "Connection refused: Not Authorized",
    }
    # print("client {} has connected to broker with status {}".format(client_id, status_decoder.get(rc)))
    client.subscribe("smartfarm-496")


def on_message(client, user_data, msg):
    # print("received message from topic {} with data {}".format(msg.topic, msg.payload.decode('utf-8')))
    jmsg = msg.payload.decode('utf-8')
    global json_buffer
    json_buffer = json.loads(jmsg)
    ref = db.reference('/')
    ref.child(json_buffer['topic']).set((json_buffer['data']))

    global AirTemperature
    global AirHumidity
    global SoilHumidity

    AirTemperature = 12
    AirHumidity = 13
    SoilHumidity = 14


hostname = "test.mosquitto.org"
client_id = 'MyClient' + ''.join(rd.choices(string.ascii_uppercase + string.digits, k=12))

client = mqtt.Client(client_id)
client.on_connect = on_connection
client.on_message = on_message
client.connect(hostname, 1883, 60)

app = Flask(__name__)

'''
structure json
{
    "topic":""
    "data":{}
    "des":"hello"
}
'''

'''
@app.route('/data/write', methods=['POST'])
def write_data():
    json_data = request.get_json()
    #print("json_data = " + json_data)
    ref = db.reference('/')
    ref.child(json_data['topic']).set((json_data['data']))
    return json_data['data']
'''
@app.route('/switch/on')
def switch_on():
    client_id = 'MyClient' + ''.join(rd.choices(string.ascii_uppercase + string.digits, k=12))
    mqttc = mqtt.Client(client_id)
    mqttc.connect(hostname, 1883)
    mqttc.publish("cpe496_switch", "on")
    return 'switch on'

@app.route('/switch/off', methods=['GET'])
def switch_off():
    client_id = 'MyClient' + ''.join(rd.choices(string.ascii_uppercase + string.digits, k=12))
    mqttc = mqtt.Client(client_id)
    mqttc.connect(hostname, 1883)
    mqttc.publish("cpe496_switch", "off")
    return 'switch off'

@app.route('/data/read/all', methods=['GET'])
def read_all_data():
    json_data = request.get_json(silent=True)
    # print("json_data = " + json_data)
    ref = db.reference('/')
    return jsonify(ref.get())

'''
# read data by query string topic
@app.route('/data/read', methods=['GET'])
def read_data():
    query_topic = request.args.get("topic", None)
    if query_topic is not None:
        ref = db.reference('/' + query_topic)
        return jsonify(ref.get())
    else:
        return jsonify({"status": "Error", "msg": "please use query string name --topic--"})
'''
'''
@app.route('/', methods=["GET", "POST"])
def main():
    return render_template('index.html')


@app.route('/data')
def data():
    # Data Format
    # [TIME, Temperature, Humidity]

    #Serialize : JSON -> Str
    #Deserialize : Str -> JSON

    
    AirTemperature = json_buffer['data']['temperature']
    AirHumidity = json_buffer['data']['humidity']
    SoilHumidity = json_buffer['data']['moisture']
    


    data = [time() * 1000, AirTemperature, AirHumidity, SoilHumidity]

    #info = {"time" : time() * 1000, "humidityair" : AirHumidity, "temperature" : AirTemperature, "moisture" : SoilHumidity}

    response = make_response(json.dumps(data))

    response.content_type = 'application/json'

    return response
'''

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1")  # test
    client.loop_forever()