import ast
import json

from httplib2 import HTTPConnectionWithTimeout
import paho.mqtt.client as mqtt

from application.models import get_measurement_type, SensorReading, Sensor, Device
from django.contrib.auth import get_user_model


class mqttuser:
    def __init__(self):
        self.client = mqtt.Client(clean_session=True)

    def add_now_topic(self,user):


        self.client.subscribe(str(user) + "/")

            # publish "Hello" to the topic "my/test/topic"
        self.client.publish(str(user) + "/", "start")

    def addtopic(self):
        User = get_user_model()
        users = User.objects.all()
        for user in users:
            self.client.subscribe(str(user) + "/")

            # publish "Hello" to the topic "my/test/topic"
            self.client.publish(str(user) + "/", "start")

    def sendorder(self):

        headers = {"charset": "utf-8", "Content-Type": "application/json"}
        conn = HTTPConnectionWithTimeout("192.168.1.8", 8000)

        sample = {""""username": self.username"""}
        sampleJson = json.dumps(sample, ensure_ascii='False')

        conn.request("POST", "/send/", sampleJson, headers)

        conn.close()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected successfully")
        else:
            print("Connect returned result code: " + str(rc))

            # The callback for when a PUBLISH message is received from the server.

    def on_message(self, client, userdata, msg):
        print("Received message: " + msg.topic + " -> " + msg.payload.decode("utf-8"))
        if str(msg.payload.decode("utf-8")) != "start":
            json_data = ast.literal_eval(msg.payload.decode("utf-8"))
            # print("Received message: " + msg.topic + " -> " + str(json_data))

            try:
                boardName = json_data['boardName']
                sensorName = json_data['sensorName']
                sensorValue = json_data['sensorValue']
                sensorValueUnit = json_data['sensorValueUnit']
                return save_data(boardName, sensorName, sensorValue, sensorValueUnit)
            except:
                return print("illi t7eb 3alih")

    def on_subscribe(self, client, userdata, flags, rc):
        print("subcribe to ")

    def run(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        # subscribe to the topic "my/test/topic"
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

        # set username and password
        self.client.username_pw_set("wissem", "@PFAwissem123")

        # connect to HiveMQ Cloud on port 8883
        self.client.connect("0ed2d1155d794dd887b6339f73c4c593.s1.eu.hivemq.cloud", 8883)

        self.addtopic()

        # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
        self.client.loop_start()


def save_data(boardName, sensorName, sensorValue, sensorValueUnit):
    try:
        board = Device.objects.get(name=boardName)
    except:
        print('The board "' + boardName + '" is not registered! Please contact admin.')
        # return HttpResponse('The board "' + boardName + '" is not registered! Please contact admin.')
    if board.enabled:
        try:
            sensor = Sensor.objects.get(name=sensorName)
        except:
            print("The sensor "' + sensorName + '" is not registered! Please contact admin.")
            # return HttpResponse('The sensor "' + sensorName + '" is not registered! Please contact admin.')
        if sensor.enabled:
            # Save SensorReading to database
            reading = SensorReading()
            reading.sensor_id = sensor.id
            reading.value = sensorValue
            sensor_measurement_type = get_measurement_type(sensor)

            # Conversion to sensor Temperature Reading unit
            if sensorValueUnit:
                if sensor_measurement_type != sensorValueUnit and 'C' not in sensorValueUnit:
                    if sensorValueUnit == 'F':
                        reading.value = int((int(sensorValue) - 32) * 5 / 9)
                    else:
                        reading.value = int((int(sensorValue) * 9 / 5) + 32)
            reading.save()
            print("Data was saved successfully!")
            # return HttpResponse("Data was saved successfully!")
        else:
            print('The sensor "' + sensorName + '" is not enabled! Please contact admin.')
            # return HttpResponse('The sensor "' + sensorName + '" is not enabled! Please contact admin.')
    else:
        print('The board "' + boardName + '" is not enabled! Please contact admin.')
        # return HttpResponse('The board "' + boardName + '" is not enabled! Please contact admin.')


mqttuser().run()
