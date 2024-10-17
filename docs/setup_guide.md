# MQTT Healthcare Monitoring System Setup Guide

## Overview

This guide provides step-by-step instructions for setting up the MQTT Healthcare Monitoring System on a NUC device running Ubuntu 22.04. The system consists of EMQX (MQTT broker), InfluxDB (time-series database), Grafana (visualization platform), and custom Python applications.

## Prerequisites

- NUC device with Ubuntu 22.04 LTS installed
- Sudo access on the NUC
- Internet connection

## Step 1: System Update

First, ensure your system is up to date:

```bash
sudo apt update
sudo apt upgrade -y
```

## Step 2: Install EMQX

1. Add EMQX repository:

```bash
curl -s https://assets.emqx.com/scripts/install-emqx-deb.sh | sudo bash
```

2. Install EMQX:

```bash
sudo apt install emqx
```

3. Start EMQX and enable it to run on boot:

```bash
sudo systemctl start emqx
sudo systemctl enable emqx
```

4. Verify EMQX is running:

```bash
sudo systemctl status emqx
```

## Step 3: Install InfluxDB

1. Add InfluxData repository:

```bash
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
```

2. Update package list and install InfluxDB:

```bash
sudo apt update
sudo apt install influxdb
```

3. Start InfluxDB and enable it to run on boot:

```bash
sudo systemctl start influxdb
sudo systemctl enable influxdb
```

4. Verify InfluxDB is running:

```bash
sudo systemctl status influxdb
```

## Step 4: Install Grafana

1. Add Grafana repository:

```bash
sudo apt-get install -y apt-transport-https software-properties-common
sudo wget -q -O /usr/share/keyrings/grafana.key https://apt.grafana.com/gpg.key
```

2. Add the repository:

```bash
echo "deb [signed-by=/usr/share/keyrings/grafana.key] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
```

3. Update package list and install Grafana:

```bash
sudo apt update
sudo apt install grafana
```

4. Start Grafana and enable it to run on boot:

```bash
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

5. Verify Grafana is running:

```bash
sudo systemctl status grafana-server
```

## Step 5: Install Python and Required Libraries

1. Install Python 3 and pip:

```bash
sudo apt install python3 python3-pip
```

2. Install required Python libraries:

```bash
pip3 install paho-mqtt influxdb-client
```

## Step 6: Configure EMQX

1. Open the EMQX configuration file:

```bash
sudo nano /etc/emqx/emqx.conf
```

2. Add or modify the following settings:

```
allow_anonymous = false
listener.tcp.external = 0.0.0.0:1883
```

3. Save the file and exit.

4. Restart EMQX:

```bash
sudo systemctl restart emqx
```

## Step 7: Create EMQX Connector to InfluxDB and Set Up Rule

1. Access the EMQX Dashboard:
   Open a web browser and navigate to `http://<NUC-IP-ADDRESS>:18083`
   Default login: admin / public

2. Create InfluxDB Connector:
   - Go to "Data Integration" > "Connectors"
   - Click "Create" and select "HTTP Server"
   - Configure the connector:
     - Name: `influxdb_connector`
     - URL: `http://localhost:8086/write?db=healthcaredb`
     - Method: POST
     - Headers:
       - Key: `Authorization`
       - Value: `Basic <base64-encoded-credentials>`
         (Replace <base64-encoded-credentials> with the actual base64 encoded string of "admin:your_secure_password")

   To generate the base64-encoded credentials:
   ```bash
   echo -n "admin:your_secure_password" | base64
   ```
   Use the output of this command as the value for the Authorization header.

   - Click "Test" to verify the connection, then "Create"

3. Create EMQX Rule:
   - Go to "Rules"
   - Click "Create"
   - In the SQL editor, enter a rule to process incoming messages:
     ```sql
     SELECT
       payload.patientId as patient_id,
       payload.data.heartRate as heart_rate,
       payload.data.bloodPressure.systolic as systolic,
       payload.data.bloodPressure.diastolic as diastolic,
       payload.data.temperature as temperature,
       payload.data.respiratoryRate as respiratory_rate,
       payload.data.oxygenSaturation as oxygen_saturation,
       payload.timestamp as timestamp,
       topic as full_topic
     FROM
       "hospital/patients/data/#"
     ```
   - Under "Actions", click "Add Action"
   - Select "Data to Web Server"
   - Configure the action:
     - Connector: Select the HTTP Server connector you created
     - Payload template:
       ```
       patient_metrics,patient_id=${patient_id},topic=${full_topic} heart_rate=${heart_rate},systolic=${systolic},diastolic=${diastolic},temperature=${temperature},respiratory_rate=${respiratory_rate},oxygen_saturation=${oxygen_saturation} ${timestamp}
       ```
   - Click "Confirm" to add the action
   - Click "Create" to finalize the rule

4. Test the Rule:
   - Use your Python script to publish messages to the MQTT broker
   - Check the EMQX Dashboard for rule metrics to ensure it's processing messages
   - Verify in InfluxDB that the data is being stored correctly

   You can query InfluxDB to check if the data is being stored properly:
   ```sql
   SELECT * FROM patient_metrics ORDER BY time DESC LIMIT 10
   ```

## Step 8: Configure InfluxDB

1. Open the InfluxDB configuration file:

```bash
sudo nano /etc/influxdb/influxdb.conf
```

2. Ensure the following settings are correct:

```
[http]
  enabled = true
  bind-address = ":8086"
```

3. Save the file and exit.

4. Restart InfluxDB:

```bash
sudo systemctl restart influxdb
```

5. Create InfluxDB database and user:

```bash
influx -execute "CREATE DATABASE healthcaredb"
influx -execute "CREATE USER admin WITH PASSWORD 'your_secure_password' WITH ALL PRIVILEGES"
```

## Step 9: Configure Grafana

1. Open the Grafana configuration file:

```bash
sudo nano /etc/grafana/grafana.ini
```

2. Modify the following settings if needed:

```
[server]
http_addr = 0.0.0.0
http_port = 3000
```

3. Save the file and exit.

4. Restart Grafana:

```bash
sudo systemctl restart grafana-server
```

## Step 10: Set Up Python Applications

1. Clone your project repository:

```bash
git clone https://github.com/yourusername/mqtt-healthcare-monitoring.git
cd mqtt-healthcare-monitoring
```

2. Install project-specific dependencies:

```bash
pip3 install -r requirements.txt
```

3. Set up systemd services for your Python applications (publishers and subscribers):

```bash
sudo nano /etc/systemd/system/mqtt-publisher.service
```

Add the following content:

```
[Unit]
Description=MQTT Publisher Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/your/publisher.py
Restart=always
User=your_username

[Install]
WantedBy=multi-user.target
```

Repeat this process for your subscriber application.

4. Start and enable the services:

```bash
sudo systemctl start mqtt-publisher
sudo systemctl enable mqtt-publisher
sudo systemctl start mqtt-subscriber
sudo systemctl enable mqtt-subscriber
```

## Step 11: Verify the Setup

1. Check if all services are running:

```bash
sudo systemctl status emqx influxdb grafana-server mqtt-publisher mqtt-subscriber
```

2. Access the Grafana web interface:
   Open a web browser and navigate to `http://<NUC-IP-ADDRESS>:3000`
   Default login: admin / admin

3. Add InfluxDB as a data source in Grafana:
   - Go to Configuration > Data Sources
   - Add a new InfluxDB data source
   - Set the URL to `http://localhost:8086`
   - Set the database name you created in InfluxDB

4. Create dashboards in Grafana to visualize your healthcare monitoring data.

## Conclusion

You have now set up the MQTT Healthcare Monitoring System on your NUC device running Ubuntu 22.04. The system includes EMQX as the MQTT broker with a connector to InfluxDB, InfluxDB for data storage, Grafana for visualization, and custom Python applications for data publishing and processing.

Remember to secure your system by setting up firewalls, implementing proper authentication for all services, and regularly updating your software. For production environments, consider setting up SSL/TLS for encrypted communications.

For troubleshooting and further configuration, refer to the official documentation of each component:

- EMQX: https://www.emqx.io/docs/en/v4.3/
- InfluxDB: https://docs.influxdata.com/influxdb/v2.0/
- Grafana: https://grafana.com/docs/grafana/latest/