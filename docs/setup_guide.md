# MQTT Healthcare Monitoring System Setup Guide (Updated)

## Overview

This guide provides step-by-step instructions for setting up the MQTT Healthcare Monitoring System on a NUC device running Ubuntu 22.04. The system consists of EMQX (MQTT broker), Telegraf (data collection and processing), InfluxDB (time-series database), Grafana (visualization platform), and custom Python applications.

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

## Step 3: Install InfluxDB2

1. Add InfluxData2 repository:

```bash
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
```

2. Update package list and install InfluxDB2:

```bash
sudo apt update
sudo apt install influxdb2
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

## Step 4: Install Telegraf

1. Add InfluxData GPG key:

```bash
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
```

2. Add InfluxData repository:

```bash
echo "deb https://repos.influxdata.com/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/influxdata.list
```

3. Update package list and install Telegraf:

```bash
sudo apt update
sudo apt install telegraf
```

## Step 5: Install Grafana

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

## Step 6: Install Python and Required Libraries

1. Install Python 3 and pip:

```bash
sudo apt install python3 python3-pip
```

2. Install required Python libraries:

```bash
pip3 install paho-mqtt influxdb-client
```

## Step 7: Configure Telegraf

1. Create a new configuration file for MQTT input:

```bash
sudo nano /etc/telegraf/telegraf.d/mqtt.conf
```

2. Add the following content:

```toml
[[inputs.mqtt_consumer]]
  servers = ["tcp://localhost:1883"]     # Change to your MQTT broker address
  topics = ["rt1/sensors"]               # Topics to subscribe to
  qos = 0                                # Quality of Service level
  client_id = "telegraf"                 # Unique client ID
  #username = "your_mqtt_username"        # MQTT username (if required)
  #password = "your_mqtt_password"        # MQTT password (if required)
  data_format = "json"                   # Data format of the incoming messages
```

3. Create a new configuration file for InfluxDB output:

```bash
sudo nano /etc/telegraf/telegraf.d/influxdb.conf
```

4. Add the following content:

```toml
[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]       # InfluxDB URL
  token = "9InQA0SCnf6GJrbHhZsAo7pSmfyUH9D1HwREpbHSCzB5dTm2cy9BJ2aE0R1TlGDOKSKnT2WIEyjoavi35VYENA=="  # InfluxDB API token
  organization = "tmu"                   # InfluxDB organization name
  bucket = "healthcare_monitoring"       # InfluxDB bucket name
```

5. Restart Telegraf to apply changes:

```bash
sudo systemctl restart telegraf
```

## Step 8: Configure Grafana

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

## Step 9: Set Up Python Applications

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

## Step 10: Verify the Setup

1. Check if all services are running:

```bash
sudo systemctl status emqx influxdb telegraf grafana-server mqtt-publisher mqtt-subscriber
```

2. Check Telegraf logs for errors:

```bash
sudo journalctl -u telegraf -f
```

3. Access the Grafana web interface:
   Open a web browser and navigate to `http://<NUC-IP-ADDRESS>:3000`
   Default login: admin / admin

4. Add InfluxDB as a data source in Grafana:
   - Go to Configuration > Data Sources
   - Add a new InfluxDB data source
   - Set the URL to `http://localhost:8086`
   - Set the organization and bucket name you created in InfluxDB
   - Use the API token you generated for authentication

5. Create dashboards in Grafana to visualize your healthcare monitoring data.

## Conclusion

You have now set up the MQTT Healthcare Monitoring System on your NUC device running Ubuntu 22.04. The system includes EMQX as the MQTT broker, Telegraf for data collection and processing, InfluxDB for data storage, Grafana for visualization, and custom Python applications for data publishing and processing.

Remember to secure your system by setting up firewalls, implementing proper authentication for all services, and regularly updating your software. For production environments, consider setting up SSL/TLS for encrypted communications.

## Troubleshooting

- If Telegraf fails to start, run `telegraf --config /etc/telegraf/telegraf.conf --test` to test the configuration.
- If no data appears in InfluxDB, ensure that the MQTT broker is publishing messages to the topics you've subscribed to.
- For authentication errors, double-check your MQTT username/password and InfluxDB token.
- If data isn't parsed correctly, adjust the `data_format` settings in the Telegraf MQTT input configuration.

For further configuration and troubleshooting, refer to the official documentation of each component:

- EMQX: https://www.emqx.io/docs/en/v4.3/
- InfluxDB: https://docs.influxdata.com/influxdb/v2.0/
- Telegraf: https://docs.influxdata.com/telegraf/v1.21/
- Grafana: https://grafana.com/docs/grafana/latest/