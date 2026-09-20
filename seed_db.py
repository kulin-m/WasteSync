import asyncio
from app.database import engine, Base, AsyncSessionLocal
from app.models import Depot, User, UserRole, Vehicle, Bin, CitizenQuery
from app.models.dumping_ground import DumpingGround
from app.models.query import QueryType, QueryStatus
from app.core.security import get_password_hash
from sqlalchemy import select

async def main():
    print("Re-creating and seeding database tables for VIT Chennai location...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Central Depot at VIT Chennai (Vandalur-Kelambakkam Road)
        depot = Depot(
            name="VIT Chennai Central Depot",
            latitude=12.8406,
            longitude=80.1534,
            address="VIT Chennai Campus, Vandalur-Kelambakkam Road, Chennai - 600127"
        )
        session.add(depot)

        # Dumping Ground / Landfill near Vandalur
        dumping_ground = DumpingGround(
            name="Vandalur Solid Waste Processing Facility",
            latitude=12.8698,
            longitude=80.1425,
            address="Vandalur Waste Management Zone, Chennai"
        )
        session.add(dumping_ground)

        # 1. Admin User
        admin = User(
            email="admin@wastetrack.org",
            hashed_password=get_password_hash("admin123"),
            name="System Administrator",
            role=UserRole.ADMIN
        )

        # 2. Driver User
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

        # 3. Citizen User
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

        # Bins along Vandalur-Kelambakkam Road (SH-121) & VIT Chennai Zone
        b1 = Bin(latitude=12.84117, longitude=80.15230, capacity=100, height=120, current_garbage_height=95.0, address="VIT North Gate / Food Street (SH-121)")
        b2 = Bin(latitude=12.84488, longitude=80.15016, capacity=100, height=120, current_garbage_height=90.0, address="Melakottaiyur Main Junction")
        b3 = Bin(latitude=12.85158, longitude=80.14191, capacity=100, height=120, current_garbage_height=105.0, address="Kandigai Junction Bus Terminal")
        b4 = Bin(latitude=12.83670, longitude=80.15545, capacity=100, height=120, current_garbage_height=80.0, address="Mambakkam Road Junction")
        session.add_all([b1, b2, b3, b4])

        # Sample Queries (Cleanliness, Dustbin Request, Driver Incident)
        q1 = CitizenQuery(
            citizen_name="Ananya Raman",
            address="VIT North Gate Bus Stop",
            query_text="Garbage bin is overflowing and spilling onto the pedestrian walkway near the main gate.",
            query_type=QueryType.CLEANLINESS_ISSUE,
            latitude=12.8438,
            longitude=80.1540,
            status=QueryStatus.PENDING
        )
        q2 = CitizenQuery(
            citizen_name="Ananya Raman",
            address="Mambakkam Lake Promenade",
            query_text="Requesting to install a new twin dustbin near the lake walking track.",
            query_type=QueryType.DUSTBIN_REQUEST,
            latitude=12.8360,
            longitude=80.1520,
            status=QueryStatus.IN_PROGRESS
        )
        q3 = CitizenQuery(
            citizen_name="Driver: Murugan Selvam",
            address="Kelambakkam Road Lane 2",
            query_text="[Road Blocked] Road widening construction blocking truck entry to bin #4.",
            query_type=QueryType.DRIVER_ISSUE,
            latitude=12.8250,
            longitude=80.1650,
            status=QueryStatus.RESOLVED
        )
        session.add_all([q1, q2, q3])

        await session.commit()
        print("Database seeded with VIT Chennai coordinates and sample data successfully!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
