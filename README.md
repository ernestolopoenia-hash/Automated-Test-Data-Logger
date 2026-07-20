# Electronics Reliability Stress Test Simulator

A professional Python application that simulates automated electrical reliability qualification testing for electronic devices. The project is designed to emulate the type of software used by Reliability, Product Validation, and Design Verification (DVT) engineers to evaluate whether hardware devices meet electrical performance specifications before production.

---

## Project Overview

Reliability testing is a critical phase of product development. Before an electronic device reaches customers, engineers must verify that it can consistently operate within its design specifications under expected operating conditions.

This project simulates a hardware validation environment by generating realistic electrical measurements for multiple Devices Under Test (DUTs), evaluating those measurements against configurable engineering specifications, and automatically producing detailed engineering reports.

The simulator is intended as an educational and portfolio project demonstrating how software can automate portions of the hardware validation process commonly found in consumer electronics, industrial equipment, automotive systems, and embedded devices.

---

## Project Goals

The primary objectives of this project are to:

- Simulate automated electrical stress testing
- Evaluate multiple DUTs using engineering pass/fail criteria
- Produce realistic manufacturing test data
- Automatically identify and log failure modes
- Generate professional engineering reports
- Visualize test data using statistical plots
- Export results in industry-standard formats
- Demonstrate software design practices used in engineering automation

---

## Simulated Test Parameters

Each Device Under Test (DUT) is assigned realistic measurements including:

- Serial Number
- Test ID
- Batch Number
- Operator Name
- Test Timestamp
- Nominal Voltage
- Measured Voltage
- Current
- Power
- Temperature
- Humidity
- Leakage Current
- Voltage Ripple
- Voltage Spikes
- Calibration Offset
- Sensor Noise
- Environmental Temperature
- Test Duration

These values are generated with realistic variation to emulate actual laboratory measurements.

---

## Pass / Fail Evaluation

Each DUT is automatically evaluated against configurable engineering specifications.

Example limits include:

| Parameter | Pass Criteria |
|-----------|---------------|
| Voltage | 11.80 – 12.20 V |
| Current | ±10% of nominal |
| Temperature | < 70°C |
| Leakage Current | < 3.0 mA |
| Voltage Ripple | < 150 mV |
| Voltage Spikes | ≤ 2 |
| Humidity | 20–80% |

If any parameter exceeds its allowable limit, the DUT is classified as **FAIL**, and the simulator records the specific reason(s) for the failure.

---

## Features

- Automated pass/fail evaluation
- Realistic electrical measurement simulation
- Randomized sensor noise and calibration offsets
- Intermittent failure simulation
- Automatic retesting of failed DUTs
- Detailed failure reason logging
- Batch testing support
- Professional terminal output
- CSV export
- Excel export
- JSON summary generation
- PDF engineering report generation
- Statistical analysis
- Engineering data visualization
- Configurable engineering specifications
- Modular object-oriented architecture

---

## Engineering Reports

The simulator automatically generates:

- CSV results
- Excel spreadsheets
- JSON summaries
- Professional PDF reports

The PDF report includes:

- Executive Summary
- Test Configuration
- Engineering Specifications
- Statistical Results
- Pass/Fail Summary
- Failure Analysis
- Data Visualizations
- Engineering Conclusions
- Recommendations

---

## Data Visualization

The application generates several engineering plots including:

- Voltage Distribution
- Temperature Distribution
- Current Distribution
- Leakage Current Distribution
- Humidity Distribution
- Pass vs. Fail Pie Chart
- Voltage vs. Temperature Scatter Plot
- Current vs. Temperature Scatter Plot
- Voltage over Simulated Test Time
- Failure Mode Analysis

These visualizations provide engineers with quick insight into device performance and reliability trends.

---

## Project Structure

```text
StressTestSimulator/
│
├── main.py
├── config.py
├── dut.py
├── measurement.py
├── stress_test.py
├── statistics.py
├── plotting.py
├── report.py
├── logger.py
├── requirements.txt
├── README.md
│
├── reports/
│   ├── Stress_Test_Report.pdf
│   ├── stress_test_results.csv
│   ├── stress_test_results.xlsx
│   ├── summary.json
│   ├── stress_test.log
│   └── plots/
│
└── screenshots/
```

---

## Technologies

- Python 3
- NumPy
- Pandas
- Matplotlib
- OpenPyXL
- ReportLab
- JSON
- Logging
- Dataclasses

---

## Learning Objectives

This project demonstrates practical applications of:

- Reliability Engineering
- Design Verification Testing (DVT)
- Product Validation
- Automated Test Equipment (ATE)
- Electrical Characterization
- Data Analysis
- Statistical Reporting
- Software Engineering
- Object-Oriented Programming
- Engineering Automation

---

## Intended Audience

This project is intended for:

- Reliability Engineers
- Hardware Validation Engineers
- Electrical Engineers
- Test Engineers
- Embedded Systems Developers
- Engineering Students
- Python Developers interested in engineering automation

---

## Future Improvements

Future enhancements may include:

- Thermal cycling simulation
- Power cycling tests
- ESD simulation
- HALT/HASS profiles
- Battery life simulation
- Environmental chamber simulation
- SQLite database integration
- REST API
- Web dashboard
- Real-time data streaming
- Interactive GUI
- Machine learning for anomaly detection
- Weibull reliability modeling
- MTBF estimation
- Reliability growth analysis

---

## Why This Project?

Modern electronics companies rely heavily on software to automate hardware qualification testing. Validation engineers frequently build custom applications to control instruments, collect measurements, evaluate specifications, and generate reports.

This simulator demonstrates the core concepts behind those workflows in a self-contained Python application. While it does not interface with physical laboratory equipment, its architecture mirrors real-world validation software and serves as a foundation for future integration with programmable instruments such as power supplies, oscilloscopes, electronic loads, and digital multimeters.

---

## License

This project is intended for educational, research, and portfolio purposes. It demonstrates software design techniques commonly used in reliability engineering and automated hardware validation environments.
