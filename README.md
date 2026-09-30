# Mobility Marketplace Operations Intelligence Engine

A Python and Flask based mobility operations analytics application.

The application validates mobility datasets, creates Python objects, performs operational analytics, applies DSA-based analysis, detects anomalies, and generates operational insights through a web interface.

## Project Objective

Build a Python-based mobility operations intelligence tool for analyzing drivers, trips, zones, demand, cancellations, utilization, and operational anomalies.

## Tech Stack

- Python
- Flask
- HTML
- CSS
- CSV
- Python OOP
- Python data structures
- Heap-based Top-K analysis

## Project Structure

```text
mobility-operations-tool/
├── app.py
├── models/
│   ├── __init__.py
│   ├── activity.py
│   ├── driver.py
│   ├── trip.py
│   └── zone.py
├── services/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── validation_service.py
│   ├── driver_analyzer.py
│   ├── trip_analyzer.py
│   ├── zone_analyzer.py
│   ├── utilization_analyzer.py
│   ├── anomaly_detector.py
│   └── insights_engine.py
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── driver.html
│   ├── zone.html
│   └── anomalies.html
├── static/
│   └── style.css
├── data/
│   ├── generate_data.py
│   ├── drivers.csv
│   ├── trips.csv
│   ├── driver_activity.csv
│   └── uploads/
├── tests/
│   ├── __init__.py
│   ├── test_day5.py
│   └── README.md
├── requirements.txt
└── README.md