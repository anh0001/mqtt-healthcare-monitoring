#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to print messages
print_message() {
    echo "----------------------------------------------------"
    echo "$1"
    echo "----------------------------------------------------"
}

# Configure EMQX
print_message "Configuring EMQX"
sudo tee -a /etc/emqx/emqx.conf > /dev/null <<EOT
allow_anonymous = false
listener.tcp.external = 0.0.0.0:1883
EOT
sudo systemctl restart emqx

# Configure InfluxDB
print_message "Configuring InfluxDB"
sudo tee -a /etc/influxdb/influxdb.conf > /dev/null <<EOT
[http]
  enabled = true
  bind-address = ":8086"
EOT
sudo systemctl restart influxdb

# Create InfluxDB database and user
print_message "Creating InfluxDB database and user"
influx -execute "CREATE DATABASE healthcaredb"
influx -execute "CREATE USER admin WITH PASSWORD 'your_secure_password' WITH ALL PRIVILEGES"

# Configure Grafana
print_message "Configuring Grafana"
sudo tee -a /etc/grafana/grafana.ini > /dev/null <<EOT
[server]
http_addr = 0.0.0.0
http_port = 3000
EOT
sudo systemctl restart grafana-server

# Set up Python application services
print_message "Setting up Python application services"

# Publisher service
sudo tee /etc/systemd/system/mqtt-publisher.service > /dev/null <<EOT
[Unit]
Description=MQTT Publisher Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/your/publisher.py
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOT

# Subscriber service
sudo tee /etc/systemd/system/mqtt-subscriber.service > /dev/null <<EOT
[Unit]
Description=MQTT Subscriber Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/your/subscriber.py
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOT

# Reload systemd, enable and start services
sudo systemctl daemon-reload
sudo systemctl enable mqtt-publisher mqtt-subscriber
sudo systemctl start mqtt-publisher mqtt-subscriber

# Verify services
print_message "Verifying services"
services=("emqx" "influxdb" "grafana-server" "mqtt-publisher" "mqtt-subscriber")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "$service is running"
    else
        echo "$service is not running"
    fi
done

print_message "Service setup complete!"
echo "Please check the output above for any errors."
echo "Next steps:"
echo "1. Secure your services by setting up proper authentication"
echo "2. Configure Grafana datasources and dashboards"
echo "3. Test your MQTT publishers and subscribers"