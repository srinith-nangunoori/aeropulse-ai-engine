import pandas as pd
import numpy as np
import random
from sklearn.ensemble import RandomForestRegressor
import joblib
from sqlalchemy.orm import Session
from database import SessionLocal, Inventory, init_db, engine

print("1. Initializing Database Structure...")
init_db()

print("\n2. Seeding Warehouse Inventory...")
# Open a secure connection to the database
db = SessionLocal()

# Check if we already have the part to avoid duplicates
existing_part = db.query(Inventory).filter(Inventory.part_id == "PART-TURB-718").first()
if not existing_part:
    # Insert our starting stock into the database
    seed_item = Inventory(
        part_id="PART-TURB-718",
        part_name="Inconel-718 Turbine Blade",
        stock_level=500, # We start with 500 blades
        unit_cost=12500.00
    )
    db.add(seed_item)
    db.commit()
    print("-> Added 500 Inconel-718 Turbine Blades to inventory ledger.")
else:
    print("-> Inventory already seeded.")
db.close()


print("\n3. Generating Historical Flight Telemetry for AI Training...")
NUM_SAMPLES = 2000
data = []

for _ in range(NUM_SAMPLES):
    # Simulate Telemetry
    flight_hours = round(random.uniform(200, 2000), 1)
    temp = round(random.uniform(-40, 50), 1) # Celsius
    dust_index = round(random.uniform(0.1, 10.0), 2)
    takeoff_cycles = int(random.uniform(50, 500))
    
    # Calculate exactly how many blades were destroyed (The Math Formula)
    # More hours, extreme heat, high dust, and lots of takeoffs = more broken parts
    base_wear = (flight_hours * 0.005)
    temp_penalty = abs(temp) * 0.05
    dust_penalty = dust_index * 0.8
    cycle_penalty = takeoff_cycles * 0.02
    
    # Final calculation with some random real-world noise
    parts_replaced = int(base_wear + temp_penalty + dust_penalty + cycle_penalty + random.uniform(-2, 2))
    
    # A plane has a max of ~50 blades in a specific stage, can't be negative
    parts_replaced = max(0, min(50, parts_replaced))
    
    data.append([flight_hours, temp, dust_index, takeoff_cycles, parts_replaced])

# Convert to Pandas DataFrame
df = pd.DataFrame(data, columns=['Flight_Hours', 'Avg_Temp', 'Dust_Index', 'Takeoff_Cycles', 'Parts_Replaced'])


print("\n4. Training the V1.0 Machine Learning Brain...")
X = df.drop('Parts_Replaced', axis=1)
y = df['Parts_Replaced']

# Train a Random Forest Model
model = RandomForestRegressor(n_estimators=50, random_state=42)
model.fit(X, y)

# Save the trained brain to the hard drive
joblib.dump(model, 'aeropulse_model_v1.joblib')
joblib.dump(list(X.columns), 'model_features.joblib')

print("-> SUCCESS: Model V1.0 saved. System is ready for operation.")