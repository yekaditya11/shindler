# Schindler-Safetyconnect

## Project Overview

**Schindler-Safetyconnect** is a project designed to provide data insights and AI-driven recommendations based on Excel data. It includes interactive dashboards for visualization and features advanced AI capabilities for analyzing trends, seasonality, and user roles. This solution is built using FastAPI and Docker, ensuring efficient data processing and API interactions.

### Key Features:
- **Data Ingestion**: Upload and process Excel/CSV files.
- **AI-Driven Insights**: Generate recommendations and KPIs based on data analysis.
- **Interactive Dashboards**: Visualize data insights through user-friendly interfaces.
- **Role-Based Access**: Deliver personalized recommendations and insights for different roles.
- **Weather and External Data**: Augment your insights with external weather data.

## Setup Instructions

### Prerequisites
- Docker (for containerization)
- Python 3.12 (if running locally without Docker)
- FastAPI (included in requirements)

### Clone the Repository
If you haven’t already cloned the repository, do so with the following command:
```bash
git clone https://github.com/GYTWorkz-Private-Limited/Schindler-SafetyConnect.git
cd Schindler-Safetyconnect
```

### Docker Setup
1. **Build the Docker Image**:
   ```bash
   docker build -t schindler-safetyconnect .
   ```
2. **Run the Docker Container**:
   ```bash
   docker run -p 8000:8000 schindler-safetyconnect
   ```

### Local Setup (Without Docker)
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Application**:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

## Usage
Once the application is up and running, you can access the API documentation at `http://localhost:8000/docs`.