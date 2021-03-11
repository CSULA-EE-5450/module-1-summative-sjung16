import paho.mqtt.client as mqtt


# Callback on connect
def on_connect(client, userdata, flags, rc):
    print("Connected with Code: " + str(rc))
    # Subscribe Topic
    client.subscribe("Test/#")


# Callback on message
def on_message(client, userdata, msg):
    print(str(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("test.mosquitto.org")

client.loop_forever()
