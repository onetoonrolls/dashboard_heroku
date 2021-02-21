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
cred = credentials.Certificate('project-cpe-496-59cdc-firebase-adminsdk-h16ku-6546e83e14.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cpe-496-internet-of-things-default-rtdb.firebaseio.com/'
})


# MQTT Management

def on_connection(client, user_data, flag, rc):
    status_decoder = {  # swtich case in python style using dictionary
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
    json_buffer = json.loads(jmsg)
    ref = db.reference('/')
    ref.child(json_buffer['topic']).set((json_buffer['data']))


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


@app.route('/data/read/all', methods=['GET'])
def read_all_data():
    json_data = request.get_json(silent=True)
    # print("json_data = " + json_data)
    ref = db.reference('/')
    return jsonify(ref.get())


# read data by query string topic
@app.route('/data/read', methods=['GET'])
def read_data():
    query_topic = request.args.get("topic", None)
    if query_topic is not None:
        ref = db.reference('/' + query_topic)
        return jsonify(ref.get())
    else:
        return jsonify({"status": "Error", "msg": "please use query string name --topic--"})


@app.route('/', methods=["GET", "POST"])
def main():
    return render_template('index.html')


@app.route('/data', methods=["GET", "POST"])
def data():
    # Data Format
    # [TIME, Temperature, Humidity]

    AirTemperature = rd.random() * 100
    AirHumidity = rd.random() * 55
    SoilHumidity = rd.random() * 55

    data = [time() * 1000, AirTemperature, AirHumidity, SoilHumidity]

    response = make_response(json.dumps(data))

    response.content_type = 'application/json'

    return response


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1")  # test
    client.loop_forever()
    # app.run(threaded=True, port=5000)

# # As an admin, the app has access to read and write all data, regradless of Security Rules
# ref = db.reference('/')
# ref.set({
#     'theater1': {
#         'movie':'Big Bang Theory - click up',
#         'duration':'1:30hrs',
#         'status':'now showing'
#     }
# })
# print(ref.get())
# https://paas-iot.herokuapp.com/
# curl --header "Content-Type: application/json" --request POST --data '{"topic":"temp","data":{"1611073073":"1234", "1611073073":"2048", "1611083073":"2000", "1611093073":"1", "1611103073":"0"}}' http://localhost:5000/data/write
