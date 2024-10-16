from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InfluxDBHelper:
    def __init__(self):
        self.url = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
        self.token = os.getenv('INFLUXDB_TOKEN', 'your_token')
        self.org = os.getenv('INFLUXDB_ORG', 'your_org')
        self.bucket = os.getenv('INFLUXDB_BUCKET', 'healthcare_data')
        
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def write_patient_data(self, patient_id, timestamp, vitals):
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

        self.write_api.write(bucket=self.bucket, record=point)
        logging.info(f"Stored patient data for {patient_id}")

    def write_robot_data(self, robot_id, timestamp, robot_data):
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

        self.write_api.write(bucket=self.bucket, record=point)
        logging.info(f"Stored robot data for {robot_id}")

    def close(self):
        self.client.close()

# Usage example:
# influxdb = InfluxDBHelper()
# influxdb.write_patient_data("patient001", "2023-05-20T12:00:00Z", {"heartRate": 75, "temperature": 36.6})
# influxdb.write_robot_data("robot001", "2023-05-20T12:00:00Z", {"batteryLevel": 80, "position": {"x": 10, "y": 20}})
# influxdb.close()