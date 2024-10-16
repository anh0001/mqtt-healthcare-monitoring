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
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'hospital/patients/data')
MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'your_username')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'your_password')

# Patient Data Configuration
PATIENT_ID = "patient001"
LOCATION = "ward5"
ORGANIZATION = "hospitalA"

def generate_patient_data():
    """Generate simulated patient data."""
    return {
        "timestamp": datetime.now().isoformat(),
        "patientId": PATIENT_ID,
        "data": {
            "heartRate": random.randint(60, 100),
            "bloodPressure": {
                "systolic": random.randint(100, 140),
                "diastolic": random.randint(60, 90)
            },
            "temperature": round(random.uniform(36.1, 37.5), 1),
            "respiratoryRate": random.randint(12, 20),
            "oxygenSaturation": random.randint(95, 100)
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
            patient_data = generate_patient_data()
            message = json.dumps(patient_data)
            topic = f"{MQTT_TOPIC}/{ORGANIZATION}/{LOCATION}/{PATIENT_ID}"
            result = client.publish(topic, message, qos=1)
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logging.error(f"Failed to publish message: {mqtt.error_string(result.rc)}")
            
            time.sleep(5)  # Publish data every 5 seconds

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