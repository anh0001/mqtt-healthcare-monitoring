import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import logging
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MQTTHelper:
    def __init__(self):
        self.broker = os.getenv('MQTT_BROKER', 'localhost')
        self.port = int(os.getenv('MQTT_PORT', 1883))
        self.username = os.getenv('MQTT_USERNAME', 'your_username')
        self.password = os.getenv('MQTT_PASSWORD', 'your_password')
        
        self.client = mqtt.Client()
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT broker")
        else:
            logging.error(f"Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        logging.info(f"Received message on topic {msg.topic}: {msg.payload}")

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            logging.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
        except Exception as e:
            logging.error(f"Failed to connect to MQTT broker: {e}")

    def publish(self, topic, message, qos=1):
        try:
            result = self.client.publish(topic, json.dumps(message), qos=qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"Published message to topic {topic}")
            else:
                logging.error(f"Failed to publish message: {mqtt.error_string(result.rc)}")
        except Exception as e:
            logging.error(f"Error publishing message: {e}")

    def subscribe(self, topic, qos=1):
        try:
            self.client.subscribe(topic, qos)
            logging.info(f"Subscribed to topic: {topic}")
        except Exception as e:
            logging.error(f"Error subscribing to topic {topic}: {e}")

    def start_loop(self):
        self.client.loop_start()

    def stop_loop(self):
        self.client.loop_stop()

    def disconnect(self):
        self.client.disconnect()
        logging.info("Disconnected from MQTT broker")

# Usage example:
# mqtt = MQTTHelper()
# mqtt.connect()
# mqtt.subscribe("hospital/+/+/+/patients/data")
# mqtt.start_loop()
# # ... do some work ...
# mqtt.publish("hospital/alerts", {"type": "high_temperature", "patient_id": "001"})
# mqtt.stop_loop()
# mqtt.disconnect()