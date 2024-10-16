import paho.mqtt.client as mqtt
import json
import logging
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MQTT Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'your_username')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'your_password')

# Topics
PATIENT_TOPIC = 'hospital/+/+/+/patients/data'
ROBOT_TOPIC = 'hospital/+/+/+/robots/data'
ALERT_TOPIC = 'hospital/alerts'

# Alert thresholds
HEART_RATE_MIN = 60
HEART_RATE_MAX = 100
TEMPERATURE_MIN = 35.0
TEMPERATURE_MAX = 38.0
OXYGEN_SATURATION_MIN = 95
BATTERY_LEVEL_MIN = 20

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
            process_patient_data(client, payload)
        elif 'robots' in msg.topic:
            process_robot_data(client, payload)
    except json.JSONDecodeError:
        logging.error(f"Failed to decode message: {msg.payload}")
    except Exception as e:
        logging.error(f"Error processing message: {e}")

def process_patient_data(client, data):
    patient_id = data.get('patientId')
    timestamp = data.get('timestamp')
    vitals = data.get('data', {})

    heart_rate = vitals.get('heartRate')
    temperature = vitals.get('temperature')
    oxygen_saturation = vitals.get('oxygenSaturation')

    if heart_rate and (heart_rate < HEART_RATE_MIN or heart_rate > HEART_RATE_MAX):
        publish_alert(client, 'patient', patient_id, 'Abnormal Heart Rate', heart_rate, timestamp)

    if temperature and (temperature < TEMPERATURE_MIN or temperature > TEMPERATURE_MAX):
        publish_alert(client, 'patient', patient_id, 'Abnormal Temperature', temperature, timestamp)

    if oxygen_saturation and oxygen_saturation < OXYGEN_SATURATION_MIN:
        publish_alert(client, 'patient', patient_id, 'Low Oxygen Saturation', oxygen_saturation, timestamp)

def process_robot_data(client, data):
    robot_id = data.get('robotId')
    timestamp = data.get('timestamp')
    robot_data = data.get('data', {})

    battery_level = robot_data.get('batteryLevel')
    error_code = robot_data.get('errorCode')

    if battery_level and battery_level < BATTERY_LEVEL_MIN:
        publish_alert(client, 'robot', robot_id, 'Low Battery', battery_level, timestamp)

    if error_code:
        publish_alert(client, 'robot', robot_id, 'Error Detected', error_code, timestamp)

def publish_alert(client, entity_type, entity_id, alert_type, value, timestamp):
    alert = {
        'timestamp': timestamp,
        'entityType': entity_type,
        'entityId': entity_id,
        'alertType': alert_type,
        'value': value
    }
    message = json.dumps(alert)
    result = client.publish(ALERT_TOPIC, message, qos=1)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logging.info(f"Alert published: {alert}")
    else:
        logging.error(f"Failed to publish alert: {mqtt.error_string(result.rc)}")

def main():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        logging.info("Alert generator stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        client.disconnect()
        logging.info("Disconnected from MQTT broker")

if __name__ == "__main__":
    main()