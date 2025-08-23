
# Pollution Routing Flask API

A Flask web service that provides  
- live pollution data simulation and subscription  
- pollution-aware routing via OpenRouteService  
- site metadata and heatmap endpoints  

This README guides setup, configuration, and usage.

---

## Prerequisites

- Python 3.10+  
- PostgreSQL with PostGIS extension  
- An OpenRouteService API key  


---

## Environment Configuration

This project uses environment variables for sensitive configuration. You can set them **at runtime** in your shell before launching the Flask app.

### PowerShell (Windows)

```powershell
$env:DATABASE_URL = "postgresql://postgres:Unsalted2025@localhost:5432/pollution_routing"
$env:ORS_API_KEY = "your-ors-api-key-here"
flask run
```

> These variables are loaded dynamically when the app starts. No `.env` file is required unless you prefer that method for local development.

### Optional: Using a `.env` File

If you'd rather not set variables manually each time, you can use a `.env` file and load it with `python-dotenv`:

1. Install:
   ```bash
   pip install python-dotenv
   ```

2. Create `.env`:
   ```
   DATABASE_URL=postgresql://postgres:Unsalted2025@localhost:5432/pollution_routing
   ORS_API_KEY=your-ors-api-key-here
   ```

3. Load it in your app:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

---

## Installation

```bash
git clone <repo-url>
cd flask-api
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

---

## Configuration

1. Set environment variables at runtime (see above).  
2. Ensure your Postgres database is running and PostGIS is enabled:
   ```sql
   CREATE EXTENSION postgis;
   ```

---

## Running the Service

```bash
flask run
```

By default it listens on `http://127.0.0.1:5000`.  
Use `FLASK_ENV=development` for auto-reload.

---

## API Endpoints

- **GET /heatmap/latest_readings**  
  Returns most recent pollution readings per site.

- **GET /sites**  
  Returns all site locations as GeoJSON FeatureCollection.

- **POST /routing/route**  
  Body: `{ start, end, mode, pollutant }`  
  Returns cleanest route GeoJSON enriched with pollution scores.

- **/pollutiondata**  
  - **POST /subscribe** – register callback URL  
  - **GET/POST /simtime** – view or set simulation clock  
  - **GET /?timestamp&site** – retrieve pollution data for one site  
  - **GET /sitemetadata** – all static site coords

---

## Running Tests

Unit and integration tests use `pytest` and `unittest`.

```bash
pytest                # runs all pytest tests
python -m unittest    # runs built-in suites
```

Ensure `DATABASE_URL` points to a test database when running DB-backed tests.

---

## Project Structure

```
├─ app.py                  # Flask app initialization
├─ extensions.py           # SQLAlchemy setup
├─ layers/                 # Blueprints (heatmap, sites, routing)
├─ models/                 # SQLAlchemy models
├─ utils/                  # AQI and enrichment logic
├─ data/                   # Generated JSON for pollution simulation
├─ tests/                  # Unit & integration tests
└─ requirements.txt        # Python dependencies
```

---


