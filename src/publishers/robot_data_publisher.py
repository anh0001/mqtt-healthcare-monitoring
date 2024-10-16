import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MQTT Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'hospital/robots/data')
MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'your_username')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'your_password')

# Robot Data Configuration
ROBOT_ID = "robot001"
LOCATION = "ward5"
ORGANIZATION = "hospitalA"

def generate_robot_data():
    """Generate simulated robot data."""
    tasks = ["patient_assistance", "medication_delivery", "room_cleaning", "vital_signs_check"]
    error_codes = [None, "E001", "E002", "E003", "E004"]  # None represents no error
    return {
        "timestamp": datetime.now().isoformat(),
        "robotId": ROBOT_ID,
        "data": {
            "position": {
                "x": round(random.uniform(0, 50), 2),
                "y": round(random.uniform(0, 30), 2),
                "z": 0
            },
            "batteryLevel": random.randint(0, 100),
            "currentTask": random.choice(tasks),
            "errorCode": random.choices(error_codes, weights=[0.9, 0.025, 0.025, 0.025, 0.025])[0],
            "lastMaintenance": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        }
    }

def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server."""
    if rc == 0:
        logging.info("Connected to MQTT broker")
    else:
        logging.error(f"Failed to connect to MQTT broker with code: {rc}")

def on_publish(client, userdata, mid):
    """Callback for when a message is published."""
    logging.info(f"Message {mid} published")

def main():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        while True:
            robot_data = generate_robot_data()
            message = json.dumps(robot_data)
            topic = f"{MQTT_TOPIC}/{ORGANIZATION}/{LOCATION}/{ROBOT_ID}"
            result = client.publish(topic, message, qos=1)
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logging.error(f"Failed to publish message: {mqtt.error_string(result.rc)}")
            
            time.sleep(10)  # Publish data every 10 seconds

    except KeyboardInterrupt:
        logging.info("Publisher stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        logging.info("Disconnected from MQTT broker")

if __name__ == "__main__":
    main()