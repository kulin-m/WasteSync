# WasteSync | Smart Waste Monitoring & CVRP Route Optimization Platform

**WasteSync** is an AI-assisted, real-time municipal waste management and garbage collection route optimization platform built with a high-performance modern tech stack: **FastAPI**, **PostgreSQL / SQLite (SQLAlchemy 2.0)**, **Google OR-Tools CVRP solver**, **OSRM (Open Source Routing Machine)**, and **Leaflet.js + OpenStreetMap**.

---

## 🌟 Key Features

- **🚀 FastAPI Asynchronous Backend**: High-throughput REST API with async endpoints and auto-generated Swagger UI (`/docs`).
- **🗺️ 100% Free & Zero-Key Map Services**: Interactive mapping powered by **Leaflet.js** and **OpenStreetMap** with zero API keys or billing accounts needed.
- **🛣️ Real Turn-by-Turn Road Routing**: Solves Capacitated Vehicle Routing Problems (CVRP) with **Google OR-Tools** and maps smooth, road-following navigation polylines using **OSRM**.
- **📍 Real-Time Search & Geocoding**: Proxy-backed Nominatim search to pinpoint addresses, landmarks, and coordinates without CORS or rate limiting errors.
- **👥 Multi-Role Portals & Role-Based Access Control (RBAC)**:
  - **👑 Admin Portal**: Live operations monitoring, bin capacity telemetry, user management, and truck fleet management.
  - **🚛 Driver Portal**: Interactive turn-by-turn route directions, one-tap "Mark Bin Emptied", and real-time roadblock/incident reporting.
  - **🏡 Citizen Portal**: Interactive map to pinpoint cleanliness issues with photo attachments and request new public dustbins.
- **🔐 Secure Authentication**: OAuth2 Password Bearer flow with JWT access tokens and salted password hashing (PBKDF2/Bcrypt).

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/kulin-m/WasteSync.git
cd WasteSync
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
```bash
python seed_db.py
```

### 4. Start the Application Server
```bash
uvicorn app.main:app --reload
```

---

## 🔑 Default Login Credentials

| Role | Email | Password | Portal URL |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@wastetrack.org` | `admin123` | [http://127.0.0.1:8000/admin-dashboard](http://127.0.0.1:8000/admin-dashboard) |
| **Driver** | `driver@wastetrack.org` | `driver123` | [http://127.0.0.1:8000/driver-portal](http://127.0.0.1:8000/driver-portal) |
| **Citizen** | `citizen@wastetrack.org` | `citizen123` | [http://127.0.0.1:8000/citizen-portal](http://127.0.0.1:8000/citizen-portal) |

---

## 🗺️ Key Application Pages

- **Authentication Gateway**: `http://127.0.0.1:8000/login`
- **Admin Dashboard**: `http://127.0.0.1:8000/admin-dashboard`
- **Real-Road Route Optimizer**: `http://127.0.0.1:8000/routes-page`
- **Driver Navigation Hub**: `http://127.0.0.1:8000/driver-portal`
- **Citizen Portal**: `http://127.0.0.1:8000/citizen-portal`
- **Interactive Swagger API Docs**: `http://127.0.0.1:8000/docs`

---

## 🏗️ Project Architecture

```
WasteSync/
├── app/
│   ├── api/             # REST Routers (auth, bins, vehicles, drivers, routes, queries)
│   ├── core/            # JWT authentication & security helpers
│   ├── models/          # SQLAlchemy 2.0 ORM Models (User, Bin, Vehicle, Depot, Route, Query)
│   ├── schemas/         # Pydantic v2 validation models
│   ├── services/        # CVRP Optimization (Google OR-Tools) & Distance Matrix (OSRM)
│   ├── templates/       # Jinja2 Dynamic UI (Tailwind CSS + Leaflet.js)
│   ├── config.py        # Pydantic Settings & environment loader
│   ├── database.py      # Async SQLAlchemy engine & session maker
│   └── main.py          # FastAPI application factory & lifespan router
├── seed_db.py           # Database migration & demo data initializer
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── .gitignore           # Git ignore rules
```

---

## 📜 License
This project is open-source and free to use under the MIT License.

