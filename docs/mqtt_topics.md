# MQTT Topics for Healthcare Monitoring System

## Overview

This document outlines the MQTT topic structure used in our Healthcare Monitoring System. It provides details on topic hierarchies, payload formats, and usage guidelines for each type of data communicated within the system.

## Topic Structure

Our topic structure follows this general format:

```
/{organization}/{location}/{entityType}/{entityID}/{dataType}/{action}
```

- `organization`: The healthcare facility (e.g., `hospitalA`)
- `location`: Specific area within the facility (e.g., `ward5`)
- `entityType`: Type of entity (e.g., `patient`, `robot`, `sensor`)
- `entityID`: Unique identifier for the entity
- `dataType`: Nature of the data (e.g., `vitals`, `position`, `status`)
- `action`: Specific action or event (e.g., `update`, `alert`)

## Topic Categories

### 1. Patient Data

#### Vital Signs
Topic: `/{organization}/{location}/patient/{patientID}/vitals/update`

Payload (JSON):
```json
{
  "timestamp": "2023-10-16T10:00:00Z",
  "patientID": "patient001",
  "data": {
    "heartRate": 75,
    "bloodPressure": {
      "systolic": 120,
      "diastolic": 80
    },
    "temperature": 36.8,
    "respiratoryRate": 16,
    "oxygenSaturation": 98
  }
}
```

#### Patient Position
Topic: `/{organization}/{location}/patient/{patientID}/position/update`

Payload (JSON):
```json
{
  "timestamp": "2023-10-16T10:05:00Z",
  "patientID": "patient001",
  "data": {
    "coordinates": {
      "x": 10.5,
      "y": 20.2,
      "z": 0
    },
    "area": "room101"
  }
}
```

#### Patient Attributes
Topic: `/{organization}/{location}/patient/{patientID}/attributes/update`

Payload (JSON):
```json
{
  "timestamp": "2023-10-16T09:00:00Z",
  "patientID": "patient001",
  "data": {
    "height": 170,
    "weight": 70,
    "age": 45,
    "gender": "female",
    "medicalConditions": ["hypertension", "diabetes"]
  }
}
```

### 2. Robot Data

#### Robot Position
Topic: `/{organization}/{location}/robot/{robotID}/position/update`

Payload (JSON):
```json
{
  "timestamp": "2023-10-16T10:10:00Z",
  "robotID": "robot001",
  "data": {
    "coordinates": {
      "x": 15.3,
      "y": 22.1,
      "z": 0
    },
    "area": "corridor1"
  }
}
```

#### Robot Status
Topic: `/{organization}/{location}/robot/{robotID}/status/update`

Payload (JSON):
```json
{
  "timestamp": "2023-10-16T10:15:00Z",
  "robotID": "robot001",
  "data": {
    "batteryLevel": 75,
    "currentTask": "patientAssistance",
    "errorCode": null,
    "lastMaintenance": "2023-10-01T08:00:00Z"
  }
}
```

### 3. Sensor Data

#### Environmental Sensors
Topic: `/{organization}/{location}/sensor/{sensorID}/environment/update`

Payload (JSON):
```json
{
  "timestamp": "2023-10-16T10:20:00Z",
  "sensorID": "env001",
  "data": {
    "temperature": 22.5,
    "humidity": 45,
    "co2Level": 800,
    "lightLevel": 500
  }
}
```

#### Equipment Sensors
Topic: `/{organization}/{location}/sensor/{sensorID}/equipment/update`

Payload (JSON):
```json
{
  "timestamp": "2023-10-16T10:25:00Z",
  "sensorID": "eq001",
  "data": {
    "equipmentID": "ventilator001",
    "status": "operational",
    "errorCode": null,
    "lastCalibration": "2023-09-15T14:00:00Z"
  }
}
```

### 4. Alerts and Notifications

#### Patient Alert
Topic: `/{organization}/{location}/alert/patient/{patientID}`

Payload (JSON):
```json
{
  "timestamp": "2023-10-16T10:30:00Z",
  "patientID": "patient001",
  "alertType": "vitalSigns",
  "severity": "high",
  "message": "Heart rate exceeds normal range",
  "data": {
    "heartRate": 120
  }
}
```

#### Equipment Alert
Topic: `/{organization}/{location}/alert/equipment/{equipmentID}`

Payload (JSON):
```json
{
  "timestamp": "2023-10-16T10:35:00Z",
  "equipmentID": "ventilator001",
  "alertType": "malfunction",
  "severity": "critical",
  "message": "Ventilator pressure out of range",
  "data": {
    "pressure": 40
  }
}
```

### 5. System Commands

#### Robot Command
Topic: `/{organization}/{location}/command/robot/{robotID}`

Payload (JSON):
```json
{
  "timestamp": "2023-10-16T10:40:00Z",
  "robotID": "robot001",
  "command": "moveTo",
  "parameters": {
    "destination": "room105"
  }
}
```

#### System Maintenance
Topic: `/{organization}/system/maintenance`

Payload (JSON):
```json
{
  "timestamp": "2023-10-16T23:00:00Z",
  "action": "databaseBackup",
  "duration": "PT30M",
  "affectedServices": ["dataIngestion"]
}
```

## Best Practices

1. **Consistency**: Maintain consistent topic structures and payload formats across similar data types.

2. **Granularity**: Use appropriate levels of topic granularity to balance between flexibility and complexity.

3. **Timestamps**: Always include timestamps in UTC format for all messages.

4. **Validation**: Implement payload validation on both publisher and subscriber sides.

5. **Security**: Use topic-based access control to restrict data access as needed.

6. **Versioning**: Consider including a version field in payloads to support future format changes.

7. **Wildcards**: When subscribing, use wildcards carefully to avoid receiving unnecessary messages.