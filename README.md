# 🏠 California Homelessness Data Platform

A complete end-to-end **Data Engineering and Analytics** project that automates the collection, transformation, storage, analysis, and visualization of California homelessness data. The platform features a robust ETL pipeline, SQLite database, SQL analytics, interactive Streamlit dashboard, geospatial mapping, pipeline monitoring, and Docker deployment.

---

## 🚀 Live Dashboard

### 👉 https://california-homelessness-data-platform-sxpoygmhanxarnpuch5p5c.streamlit.app/

---

# 📸 Dashboard Preview

## Executive Dashboard

![Dashboard Overview](docs/images/dashboard_overview.png)

---

## California County Map

![California Map](docs/images/california_map.png)

---

# 📖 Project Overview

This project demonstrates the complete lifecycle of a modern **Data Engineering** solution using publicly available California homelessness datasets.

The platform automatically:

- Extracts raw homelessness datasets
- Cleans and validates incoming data
- Transforms and standardizes records
- Loads processed data into SQLite
- Performs SQL-based analytical reporting
- Generates visualizations and charts
- Displays interactive dashboards using Streamlit
- Tracks ETL pipeline execution
- Produces automated data quality reports
- Supports Docker containerization
- Includes GitHub Actions for Continuous Integration (CI)

---

# 🏗 Project Architecture

```text
                    Raw CSV Files
                          │
                          ▼
                  Extract & Validate
                          │
                          ▼
                  Data Transformation
                          │
                          ▼
                  Processed CSV Files
                          │
                          ▼
                     SQLite Database
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
    SQL Analytics                  Streamlit Dashboard
          │                               │
          ▼                               ▼
   Charts & Reports             Interactive Visualizations
```

---

# ✨ Key Features

## 🔹 ETL Pipeline

- Automated Data Extraction
- Data Cleaning & Standardization
- Data Validation
- Logging & Error Handling
- Configuration Management

---

## 🔹 Database

- SQLite Database
- SQL Queries
- Aggregations
- Analytical Reporting

---

## 🔹 Interactive Dashboard

- Executive KPI Cards
- Homeless Population Trends
- County Comparison Dashboard
- California Choropleth Map
- Age Distribution Analysis
- Race Distribution Analysis
- Data Explorer
- Automated Insights

---

## 🔹 Monitoring & Reporting

- Pipeline Run History
- Data Quality Report
- CSV Downloads
- Interactive Dashboard Filters

---

# 🛠 Technology Stack

| Category | Technologies |
|----------|--------------|
| Programming | Python 3 |
| Data Processing | Pandas, NumPy |
| Database | SQLite |
| Dashboard | Streamlit, Plotly |
| Geospatial | GeoPandas, Shapely, PyProj |
| Visualization | Matplotlib |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Version Control | Git & GitHub |

---

# 📂 Project Structure

```text
california-homelessness-data-platform/

├── dashboard/
│   ├── app.py
│   └── map_utils.py
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── analyze.py
│   ├── visualize.py
│   ├── monitoring.py
│   ├── data_quality.py
│   ├── logger.py
│   ├── config_loader.py
│   └── main.py
│
├── data/
│   ├── homelessness.db
│   ├── raw/
│   ├── processed/
│   └── geo/
│
├── reports/
│
├── sql/
│
├── docs/
│   └── images/
│
├── config/
│
├── .github/
│   └── workflows/
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/MedhaBData/california-homelessness-data-platform.git
```

Navigate to the project directory

```bash
cd california-homelessness-data-platform
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Install the required packages

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the ETL Pipeline

```bash
python src/main.py
```

---

# ▶️ Launch the Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

---

# 🐳 Docker Deployment

Build the Docker image

```bash
docker build -t homelessness-dashboard .
```

Run the Docker container

```bash
docker run -p 8501:8501 homelessness-dashboard
```

Open your browser and navigate to:

```
http://localhost:8501
```

---

# 📊 Dashboard Highlights

- ✅ Executive KPI Dashboard
- ✅ California County-Level Analysis
- ✅ Interactive California Choropleth Map
- ✅ Homeless Population Trend Analysis
- ✅ Age Distribution Dashboard
- ✅ Race Distribution Dashboard
- ✅ Data Explorer
- ✅ Automated Insights
- ✅ Pipeline Monitoring
- ✅ Data Quality Reports
- ✅ CSV Export

---

# 📈 Future Enhancements

- PostgreSQL Integration
- Apache Airflow Pipeline Orchestration
- AWS Cloud Deployment
- Automated Scheduled ETL Jobs
- Machine Learning Forecasting
- Real-Time Data Integration
- User Authentication
- Predictive Analytics Dashboard

---

# 👩‍💻 Author

## **Medha Besta**

**Master of Science in Data Science**

**Data Engineer | Data Analyst | Python | SQL | ETL | Streamlit | Power BI | Data Visualization**

📧 **Email:** bestamedha6@gmail.com

🐙 **GitHub:** https://github.com/MedhaBData

---

# 🤝 Connect With Me

I'm passionate about building scalable data engineering solutions, interactive analytics dashboards, and end-to-end data pipelines.

If you'd like to collaborate, discuss data engineering, or explore opportunities, feel free to connect!

⭐ **If you found this project helpful, consider giving it a star on GitHub!**