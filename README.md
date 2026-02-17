# Intelligent-Manufacturing-Dataset-Application

## Overview

The **Intelligent Manufacturing Dataset Application** project is an interactive analytics application built using **Streamlit**. It is designed to analyze smart manufacturing data and provide actionable insights related to machine performance, efficiency, quality control, and predictive maintenance.

The application allows users to upload a manufacturing dataset, apply dynamic filters, visualize KPIs and trends, and export the complete analysis as a **PDF report**.

---

## Key Features

* Interactive dashboard with real-time KPIs
* Machine-level performance analysis
* Efficiency and operation mode monitoring
* Predictive maintenance indicators
* Multiple visualizations (bar charts, rankings, trends)
* One-click **PDF report export**
* Sidebar filters for dynamic analysis

---

## KPIs Included

* Total Machine Count
* Average Production Speed
* Average Error Rate
* Average Temperature
* Average Vibration
* Quality Control Defect Rate
* Power Consumption
* Machines at High Maintenance Risk
* Overall Efficiency (%)

---

## Visualizations

The dashboard includes:

* Day-wise average production speed
* Top 10 machines by average vibration
* Top 10 machines by error rate
* Machines by efficiency status
* Machines by operation mode
* High-temperature machine analysis

All visualizations respond dynamically to selected filters.

---

## Dataset Requirements

The uploaded dataset should contain (at minimum) the following columns:

* `Timestamp`
* `Machine_ID`
* `Operation_Mode`
* `Efficiency_Status`
* `Production_Speed_units_per_hr`
* `Temperature_C`
* `Vibration_Hz`
* `Error_Rate_%`
* `Quality_Control_Defect_Rate_%`
* `Power_Consumption_kW`
* `Predictive_Maintenance_Score`

The dataset is uploaded **via the application** and is not stored in the repository.

---

## Technology Stack

* **Python**
* **Streamlit** (UI & Dashboard)
* **Pandas** (Data Processing)
* **Matplotlib / Plotly** (Visualizations)
* **ReportLab** (PDF Generation)

---


## Deployment

The application can be deployed for free using **Streamlit Community Cloud**:

* Push the code to a public GitHub repository
* Deploy via: https://intelligent-manufacturing-dataset-analysis.streamlit.app/
* Share the generated public URL

---

## PDF Export

The dashboard includes a **Download PDF Report** button that generates a printable report containing:

* KPI summary
* Key charts
* Filtered analysis results

This ensures both interactive exploration and static reporting.

---

## Use Cases

* Manufacturing performance monitoring
* Predictive maintenance analysis
* Operational efficiency evaluation
* Academic and research projects
* Interview and portfolio demonstration

---

