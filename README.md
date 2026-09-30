# Mobility Marketplace Operations Intelligence Engine

## 1. Problem Statement

The Mobility Marketplace Operations Intelligence Engine is a Python-based analytics application for analyzing mobility operations data.

The application allows an operations user to upload:

- Drivers CSV
- Trips CSV
- Driver Activity CSV

The system validates the uploaded data, converts records into Python objects, performs operational analytics, detects anomalies, and generates dynamic business insights.

The project focuses on:

- Python OOP
- Data processing
- Data Structures and Algorithms
- Analytics
- Flask application development

---

## 2. Key Capabilities

The application provides:

### Data Ingestion and Validation

- CSV file upload
- Required-column validation
- Missing-value validation
- Invalid driver ID detection
- Invalid timestamp detection
- Negative fare detection
- Invalid trip-duration detection
- Duplicate-record detection
- Validation error display

### Driver Analytics

- Driver profile
- Total trips
- Completed trips
- Cancelled trips
- Completion rate
- Cancellation rate
- Revenue
- Average fare
- Average distance
- Average fare per kilometre
- Driver rankings
- Top-K drivers

### Trip Analytics

- Total trips
- Completed trips
- Cancelled trips
- Total revenue
- Average fare
- Average distance
- Average duration
- Trip status frequency
- Cancellation-reason frequency
- Top-K riders

### Zone Analytics

- Total requests
- Completed trips
- Cancelled trips
- Completion rate
- Cancellation rate
- Revenue
- Average fare
- Demand distribution by time period
- Top-K zones by demand
- Top-K zones by cancellation

### Advanced Analytics

- Driver utilization
- Online hours
- Busy hours
- Idle hours
- Configurable utilization thresholds
- Idle-time detection
- Peak demand analysis
- Cancellation intelligence

### Anomaly Detection

Trip-level anomalies:

- Negative fare
- Zero distance
- Invalid timestamps
- Invalid trip duration
- Unknown driver
- Unusually high fare

Driver-level anomalies:

- High cancellation rate
- Low utilization
- High trip count
- Low rating

### Operational Insights

The Insights Engine dynamically generates operational observations from the uploaded data.

Examples include:

- Zone with the highest cancellation rate
- Peak demand period
- Drivers with low utilization
- Largest cancellation category
- Number of flagged anomalies

Insights are calculated from the dataset and are not hardcoded.

---

## 3. Technology Stack

- Python 3
- Flask
- HTML
- CSS
- CSV
- `heapq`
- `unittest`

No database is required for the current implementation.

---

## 4. Project Structure

```text
mobility-operations-tool/
│
├── app.py
│
├── data/
│   ├── drivers.csv
│   ├── trips.csv
│   ├── driver_activity.csv
│   ├── generate_data.py
│   └── uploads/
│
├── models/
│   ├── driver.py
│   ├── trip.py
│   ├── zone.py
│   ├── activity.py
│   └── __init__.py
│
├── services/
│   ├── data_loader.py
│   ├── validation_service.py
│   ├── driver_analyzer.py
│   ├── trip_analyzer.py
│   ├── zone_analyzer.py
│   ├── utilization_analyzer.py
│   ├── anomaly_detector.py
│   ├── insights_engine.py
│   └── __init__.py
│
├── templates/
│   ├── index.html
│   ├── validation.html
│   ├── dashboard.html
│   ├── driver.html
│   ├── zone.html
│   └── anomalies.html
│
├── static/
│   └── style.css
│
├── tests/
│   ├── __init__.py
│   └── test_day5.py
│
├── requirements.txt
└── README.md