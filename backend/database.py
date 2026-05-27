from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

# 1. Create the SQLite Database File
SQLALCHEMY_DATABASE_URL = "sqlite:///./aeropulse.db"

# connect_args={"check_same_thread": False} is required for SQLite in FastAPI
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- TABLE 1: Warehouse Inventory ---
class Inventory(Base):
    __tablename__ = "inventory_ledger"
    
    part_id = Column(String, primary_key=True, index=True)
    part_name = Column(String)
    stock_level = Column(Integer, default=0)
    unit_cost = Column(Float)

# --- TABLE 2: Maintenance Logs (The AI Training Data) ---
class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"
    
    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    aircraft_id = Column(String, index=True)
    
    # Telemetry Features (X)
    flight_hours = Column(Float)
    avg_operating_temp = Column(Float)
    air_dust_index = Column(Float)
    takeoff_cycles = Column(Integer)
    
    # The Final Answer / Target (y)
    parts_replaced = Column(Integer)
    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# --- TABLE 3: Automatic Procurement Orders ---
class ProcurementOrder(Base):
    __tablename__ = "procurement_orders"
    
    order_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    part_id = Column(String, ForeignKey("inventory_ledger.part_id"))
    order_quantity = Column(Integer)
    status = Column(String, default="PENDING_DISPATCH") # PENDING_DISPATCH, DELIVERED
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# 2. Command to actually build the tables inside the database file
def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database and Tables created successfully!")

# If we run this file directly, it builds the database
if __name__ == "__main__":
    init_db()