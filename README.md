
# MQTT Healthcare Monitoring System

This project implements a healthcare monitoring system using MQTT protocol for real-time data communication, EMQX as the MQTT broker, InfluxDB for time-series data storage, and Grafana for data visualization. It is designed to be installed on a Ubuntu 22 in a NUC (Next Unit of Computing) device.

## System Architecture

1. MQTT protocol for real-time communication
2. EMQX broker for message handling
3. InfluxDB database for data storage
4. Grafana for data visualization

## Prerequisites

- NUC device with Ubuntu 22.04 or later
- Python 3.8+
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/anh0001/mqtt-healthcare-monitoring.git
   cd mqtt-healthcare-monitoring
   ```

2. Install dependencies:
   ```bash
   sudo ./scripts/install_dependencies.sh
   ```

3. Set up the Python environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Configure and start services:
   ```bash
   sudo ./scripts/setup_services.sh
   ```

5. Access the services:
   - EMQX Dashboard: http://localhost:18083
   - Influxdb2 Dashboard: http://localhost:8086
   - Grafana: http://localhost:3000

## Configuration

- EMQX configuration: `/etc/emqx/emqx.conf`
- InfluxDB configuration: `/etc/influxdb/influxdb.conf`
- Grafana configuration: `/etc/grafana/grafana.ini`

## Usage

Detailed usage instructions can be found in the `docs/` directory.

## Service Management

The system uses systemd for service management. You can control services using:
   ```bash
   sudo systemctl start/stop/restart emqx
   sudo systemctl start/stop/restart influxdb
   sudo systemctl start/stop/restart grafana-server
   ```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
