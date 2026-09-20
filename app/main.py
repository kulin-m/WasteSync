from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal
from app.models.depot import Depot
from app.models.bin import Bin
from app.models.vehicle import Vehicle
from app.models.user import User, UserRole
from app.models.query import CitizenQuery, QueryType, QueryStatus
from app.core.security import get_password_hash

from app.api import auth, bins, vehicles, drivers, routes, queries

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. Seed initial prototype sample data if database is empty
    async with AsyncSessionLocal() as session:
        depot_res = await session.execute(select(Depot))
        if not depot_res.scalars().all():
            print("[Lifespan] Seeding database with roles, vehicles, depots, and bins...")
            
            # Depot (VIT Chennai Campus, Vandalur-Kelambakkam Road)
            depot = Depot(name="VIT Chennai Central Depot", latitude=12.8406, longitude=80.1534, address="VIT Chennai Campus, Vandalur-Kelambakkam Road, Chennai")
            session.add(depot)

            # 1. Admin Account
            admin = User(
                email="admin@wastetrack.org",
                hashed_password=get_password_hash("admin123"),
                name="System Administrator",
                role=UserRole.ADMIN
            )
            
            # 2. Driver Account
            driver = User(
                email="driver@wastetrack.org",
                hashed_password=get_password_hash("driver123"),
                name="Murugan Selvam (Driver)",
                mobile="9840123456",
                address="VIT Driver Quarters, Vandalur, Chennai",
                age=36,
                gender="Male",
                role=UserRole.DRIVER
            )

            # 3. Citizen Account
            citizen = User(
                email="citizen@wastetrack.org",
                hashed_password=get_password_hash("citizen123"),
                name="Ananya Raman (Citizen)",
                mobile="9884567890",
                address="Kelambakkam Road, Near VIT Chennai",
                age=24,
                gender="Female",
                role=UserRole.CITIZEN
            )
            session.add_all([admin, driver, citizen])
            await session.flush()

            # Vehicles
            v1 = Vehicle(vehicle_number="TN-11-GT-2026", capacity=300.0, driver_id=driver.id)
            v2 = Vehicle(vehicle_number="TN-11-GT-2027", capacity=400.0)
            session.add_all([v1, v2])

            # Sample Bins around VIT Chennai & Vandalur-Kelambakkam corridor
            b1 = Bin(latitude=12.84117, longitude=80.15230, capacity=100, height=120, current_garbage_height=95.0, address="VIT North Gate / Food Street (SH-121)")
            b2 = Bin(latitude=12.84488, longitude=80.15016, capacity=100, height=120, current_garbage_height=90.0, address="Melakottaiyur Main Junction")
            b3 = Bin(latitude=12.85158, longitude=80.14191, capacity=100, height=120, current_garbage_height=105.0, address="Kandigai Junction Bus Terminal")
            b4 = Bin(latitude=12.83670, longitude=80.15545, capacity=100, height=120, current_garbage_height=80.0, address="Mambakkam Road Junction")
            session.add_all([b1, b2, b3, b4])

            # Sample Queries
            q1 = CitizenQuery(
                citizen_name="Ananya Raman",
                address="VIT North Gate Bus Stop",
                query_text="Dustbin is overflowing with plastic waste and foul smell.",
                query_type=QueryType.CLEANLINESS_ISSUE,
                latitude=12.8438,
                longitude=80.1540,
                status=QueryStatus.PENDING
            )
            q2 = CitizenQuery(
                citizen_name="Ananya Raman",
                address="Mambakkam Lake Promenade",
                query_text="Requesting to install a new public dustbin near the walking track.",
                query_type=QueryType.DUSTBIN_REQUEST,
                latitude=12.8360,
                longitude=80.1520,
                status=QueryStatus.IN_PROGRESS
            )
            session.add_all([q1, q2])

            await session.commit()
            print("[Lifespan] Prototype database initialized with all 3 roles, bins, vehicles & queries.")

    yield
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="Modern Role-Based Garbage Truck Monitoring System with CVRP Route Optimization.",
    lifespan=lifespan
)

# Include API Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(bins.router, prefix="/api/v1")
app.include_router(vehicles.router, prefix="/api/v1")
app.include_router(drivers.router, prefix="/api/v1")
app.include_router(routes.router, prefix="/api/v1")
app.include_router(queries.router, prefix="/api/v1")

# Jinja2 HTML Templates
templates = Jinja2Templates(directory="app/templates")

# Root & Auth Gateway
@app.get("/", include_in_schema=False)
async def root_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

# Role Portals
@app.get("/admin-dashboard", include_in_schema=False)
async def admin_dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/driver-portal", include_in_schema=False)
async def driver_portal_page(request: Request):
    return templates.TemplateResponse(request=request, name="driver.html")

@app.get("/citizen-portal", include_in_schema=False)
async def citizen_portal_page(request: Request):
    return templates.TemplateResponse(request=request, name="citizen.html")

@app.get("/users-page", include_in_schema=False)
async def users_page(request: Request):
    return templates.TemplateResponse(request=request, name="users.html")

@app.get("/routes-page", include_in_schema=False)
async def routes_page(request: Request):
    return templates.TemplateResponse(request=request, name="routes.html")

@app.get("/queries-page", include_in_schema=False)
async def queries_page(request: Request):
    return templates.TemplateResponse(request=request, name="queries.html")
