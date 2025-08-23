# Pollution Routing Flask API

A Flask web service powering the Pollution Avoidance Navigation Tool.  
It exposes live pollution data, site metadata, and pollution-aware routing endpoints backed by OpenRouteService.
Developed by Ross Cochrane as part of a submission for MSc Software Development
dissertation.
Part of Pollution Avoidance Navigation Tool (PANT):
Flask Pollution Data Generation Web Service
Spring API 
Flask API (This)
Flutter Front End


---

## Features

- Serve latest pollution readings per site (GeoJSON)  
- Retrieve all monitoring site locations (GeoJSON)  
- Generate and return the cleanest route enriched with pollution scores  
- Modular Flask Blueprints for heatmap, sites, and routing  

---

## Prerequisites

- Python 3.10+  
- PostgreSQL ≥ 13 with PostGIS enabled  
- An OpenRouteService API key (sign up at https://openrouteservice.org/)  

---

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/GarminFenix/PANTflaskapi.git
   cd PANTflaskapi
   ```

2. **Create and activate a virtual environment**  
   ```bash
   python -m venv venv
   
   venv\Scripts\activate         # Windows PowerShell
   ```

3. **Install Python dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

This project reads sensitive settings from environment variables. They can also be set in the shell or via a `.env` file.

### A. Shell (runtime)

```bash
export DATABASE_URL="postgresql://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>"
export ORS_API_KEY="your-openrouteservice-api-key"
flask run
```

_On Windows PowerShell:_

```powershell
$env:DATABASE_URL = "postgresql://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>"
$env:ORS_API_KEY   = "your-openrouteservice-api-key"
flask run
```

### B. `.env` file with `python-dotenv`

1. Install `python-dotenv`  
   ```bash
   pip install python-dotenv
   ```
2. Create a `.env` file at project root:
  ```bash
  New-Item -Path . -Name ".env" -ItemType "file"
  ```
  ```bash
  code .env
  ```

   ```ini
   DATABASE_URL=postgresql://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>
   ORS_API_KEY=your-openrouteservice-api-key
   ```

## Running the Service

Once configured, simply run:

```bash
flask run
```

By default, the API listens on `http://127.0.0.1:5000`.  
Use `FLASK_ENV=development` to enable auto-reload.

---

## API Endpoints

- **GET /heatmap/latest_readings**  
  Returns an array of latest pollution readings per site.

- **GET /sites**  
  Returns all monitoring sites as a GeoJSON FeatureCollection.

- **POST /routing/route**  
  Request body:
  ```json
  {
    "start": [lon, lat],
    "end":   [lon, lat],
    "mode":  "foot-walking" | "cycling-regular",
    "pollutant": "co" | "no" | "no2" | "noise" | "aqi"
  }
  ```
  Returns the cleanest route GeoJSON with `pollution_scores` and `average_pollution_score`.

---

## Testing

- **pytest**  
  ```bash
  pytest
  ```

- **unittest**  
  ```bash
  python -m unittest discover
  ```

Ensure DATABASE_URL points to the same PostgreSQL/PostGIS database used by the Spring service, so Flask can access the pollution data it needs for routing and heatmap endpoints.


---

## Project Structure

```
.
├── app.py                  # Flask app initialization & blueprint registration
├── extensions.py           # SQLAlchemy setup
├── layers/                 # Blueprints
│   ├── heat_map.py
│   ├── site_location.py
│   └── routing.py
├── models/                 # SQLAlchemy models
│   ├── site.py
│   └── pollution_reading.py
├── utils/                  # AQI & route enrichment logic
│   ├── pollution/aqi.py
│   └── routes/enrichment.py
├── tests/                  # Unit & integration tests
│   ├── test_heatmap.py
│   ├── test_sites.py
│   ├── test_routing.py
│   └── test_utils_aqi.py
└── requirements.txt        # Python dependencies
```

---


