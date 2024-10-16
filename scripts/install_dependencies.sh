#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to print messages
print_message() {
    echo "----------------------------------------------------"
    echo "$1"
    echo "----------------------------------------------------"
}

# Update and upgrade the system
print_message "Updating and upgrading the system"
sudo apt update && sudo apt upgrade -y

# Install common dependencies
print_message "Installing common dependencies"
sudo apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates lsb-release

# Install EMQX
print_message "Installing EMQX"
curl -s https://assets.emqx.com/scripts/install-emqx-deb.sh | sudo bash
sudo apt install -y emqx
sudo systemctl start emqx
sudo systemctl enable emqx

# Install InfluxDB
print_message "Installing InfluxDB"
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt update
sudo apt install -y influxdb
sudo systemctl start influxdb
sudo systemctl enable influxdb

# Install Grafana
print_message "Installing Grafana"
sudo apt-get install -y apt-transport-https software-properties-common
sudo wget -q -O /usr/share/keyrings/grafana.key https://apt.grafana.com/gpg.key
echo "deb [signed-by=/usr/share/keyrings/grafana.key] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt update
sudo apt install -y grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Install Python and pip
print_message "Installing Python and pip"
sudo apt install -y python3 python3-pip

# Install required Python packages
print_message "Installing required Python packages"
pip3 install paho-mqtt influxdb-client

# Verify installations
print_message "Verifying installations"
systemctl is-active --quiet emqx && echo "EMQX is running" || echo "EMQX is not running"
systemctl is-active --quiet influxdb && echo "InfluxDB is running" || echo "InfluxDB is not running"
systemctl is-active --quiet grafana-server && echo "Grafana is running" || echo "Grafana is not running"

print_message "Installation complete!"
echo "Please check the output above for any errors."
echo "You may need to configure each service. Refer to the setup guide for next steps."