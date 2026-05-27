from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import datetime

# Import our database schema
from database import SessionLocal, Inventory, MaintenanceLog, ProcurementOrder

app = FastAPI()

# Enable React to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the current AI Brain
model = joblib.load('aeropulse_model_v1.joblib')
model_features = joblib.load('model_features.joblib')

# Dependency function to open a secure database tunnel for every request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Data Validation Models ---
class InspectionRequest(BaseModel):
    aircraft_id: str
    flight_hours: float
    avg_operating_temp: float
    air_dust_index: float
    takeoff_cycles: int

# --- THE BACKGROUND MLOPS RETRAINING SCRIPT ---
def retrain_model_background():
    print("\n[MLOps] ALERT: Threshold reached. Initiating automatic model retraining...")
    db = SessionLocal()
    
    # 1. Pull ALL historical maintenance logs from the database
    logs = db.query(MaintenanceLog).all()
    
    # 2. Convert SQL data back into a Pandas DataFrame
    data = []
    for log in logs:
        data.append([log.flight_hours, log.avg_operating_temp, log.air_dust_index, log.takeoff_cycles, log.parts_replaced])
    
    df = pd.DataFrame(data, columns=model_features + ['Parts_Replaced'])
    
    X = df.drop('Parts_Replaced', axis=1)
    y = df['Parts_Replaced']
    
    # 3. Train a brand new, smarter model
    new_model = RandomForestRegressor(n_estimators=50, random_state=42)
    new_model.fit(X, y)
    
    # 4. Save to disk and overwrite the active memory
    joblib.dump(new_model, 'aeropulse_model_v1.joblib')
    global model
    model = new_model
    
    print(f"[MLOps] SUCCESS: Model retrained on {len(logs)} live records and deployed to production.\n")
    db.close()


@app.get("/")
def home():
    return {"message": "AeroPulse AI Core is Online"}

# --- THE MAIN SUPPLY CHAIN LOOP ---
@app.post("/api/inspect")
def process_inspection(request: InspectionRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    
    # 1. AI PREDICTION: Map the API request to the EXACT column names the AI was trained on
    input_data = {
        'Flight_Hours': [request.flight_hours],
        'Avg_Temp': [request.avg_operating_temp],
        'Dust_Index': [request.air_dust_index],
        'Takeoff_Cycles': [request.takeoff_cycles]
    }
    input_df = pd.DataFrame(input_data)
    input_df = input_df[model_features] # Ensure correct column order
    
    predicted_broken_parts = int(model.predict(input_df)[0])
    # Real-world noise: Mechanics usually find +/- 1 part different from the AI
    actual_broken_parts = max(0, predicted_broken_parts + (1 if request.takeoff_cycles % 2 == 0 else -1))

    # 2. INVENTORY CHECK: Do we have enough?
    part = db.query(Inventory).filter(Inventory.part_id == "PART-TURB-718").first()
    
    if part.stock_level < actual_broken_parts:
        raise HTTPException(status_code=400, detail="AOG WARNING: Insufficient inventory to complete maintenance.")

    # 3. MAINTENANCE LOGGING: Deduct stock and log the work
    part.stock_level -= actual_broken_parts
    
    new_log = MaintenanceLog(
        aircraft_id=request.aircraft_id,
        flight_hours=request.flight_hours,
        avg_operating_temp=request.avg_operating_temp,
        air_dust_index=request.air_dust_index,
        takeoff_cycles=request.takeoff_cycles,
        parts_replaced=actual_broken_parts
    )
    db.add(new_log)
    
    # 4. AUTO-PROCUREMENT LOGIC
    procurement_triggered = False
    if part.stock_level < 100:
        new_order = ProcurementOrder(
            part_id=part.part_id,
            order_quantity=200,
            status="PENDING_DISPATCH"
        )
        db.add(new_order)
        # Fake the delivery for the simulation
        part.stock_level += 200
        procurement_triggered = True

    # Save all database changes
    db.commit()
    
    # 5. MLOPS RETRAINING CHECK
    total_logs = db.query(MaintenanceLog).count()
    if total_logs > 0 and total_logs % 5 == 0:
        background_tasks.add_task(retrain_model_background)

    return {
        "status": "Maintenance Complete",
        "predicted_wear": predicted_broken_parts,
        "actual_replaced": actual_broken_parts,
        "remaining_stock": part.stock_level,
        "procurement_triggered": procurement_triggered,
        "total_database_logs": total_logs
    }
