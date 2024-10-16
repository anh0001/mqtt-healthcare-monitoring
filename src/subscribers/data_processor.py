import paho.mqtt.client as mqtt
import json
import logging
from dotenv import load_dotenv
import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MQTT Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'your_username')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'your_password')

# InfluxDB Configuration
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'your_token')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'your_org')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'healthcare_data')

# Topics
PATIENT_TOPIC = 'hospital/+/+/+/patients/data'
ROBOT_TOPIC = 'hospital/+/+/+/robots/data'

# Initialize InfluxDB client
influxdb_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker")
        client.subscribe([(PATIENT_TOPIC, 1), (ROBOT_TOPIC, 1)])
    else:
        logging.error(f"Failed to connect to MQTT broker with code: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        if 'patients' in msg.topic:
            process_patient_data(payload)
        elif 'robots' in msg.topic:
            process_robot_data(payload)
    except json.JSONDecodeError:
        logging.error(f"Failed to decode message: {msg.payload}")
    except Exception as e:
        logging.error(f"Error processing message: {e}")

def process_patient_data(data):
    patient_id = data.get('patientId')
    timestamp = data.get('timestamp')
    vitals = data.get('data', {})

    point = (
        Point("patient_vitals")
        .tag("patient_id", patient_id)
        .time(timestamp)
    )

    for key, value in vitals.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                point = point.field(f"{key}_{sub_key}", sub_value)
        else:
            point = point.field(key, value)

    write_api.write(bucket=INFLUXDB_BUCKET, record=point)
    logging.info(f"Stored patient data for {patient_id}")

def process_robot_data(data):
    robot_id = data.get('robotId')
    timestamp = data.get('timestamp')
    robot_data = data.get('data', {})

    point = (
        Point("robot_status")
        .tag("robot_id", robot_id)
        .time(timestamp)
    )

    for key, value in robot_data.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                point = point.field(f"{key}_{sub_key}", sub_value)
        else:
            point = point.field(key, value)

    write_api.write(bucket=INFLUXDB_BUCKET, record=point)
    logging.info(f"Stored robot data for {robot_id}")

def main():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        logging.info("Data processor stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        client.disconnect()
        influxdb_client.close()
        logging.info("Disconnected from MQTT broker and InfluxDB")

if __name__ == "__main__":
    main()