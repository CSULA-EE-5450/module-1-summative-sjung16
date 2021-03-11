import paho.mqtt.client as mqtt
import time


broker = "localhost"

client = mqtt.Client("python1")     # Create new instance
print("Connecting to broker ", broker)
client.connect(broker, port=1883)  # Connect to broker

time.sleep(4)

client.disconnect()