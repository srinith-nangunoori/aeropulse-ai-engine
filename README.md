# AeroPulse AI | Predictive Aerospace Supply Chain & MLOps Engine

AeroPulse AI is a closed-loop, autonomous ERP (Enterprise Resource Planning) ecosystem designed for Aerospace MRO (Maintenance, Repair, and Overhaul) facilities. It predicts jet engine part degradation based on flight telemetry, autonomously manages warehouse inventory, triggers automated procurement orders, and continuously retrains its own Machine Learning models in the background based on live SQL transaction data.

Built on a decoupled microservice architecture featuring a **Python (FastAPI + SQLAlchemy) MLOps Backend** and a **React (Vite + Tailwind CSS) Human-in-the-Loop Console**.

---

##  System Architecture & Automated Loops

AeroPulse AI moves beyond static predictions by implementing a **Four-Tier State Machine**:

1. **The Predictive Brain (Scikit-Learn):** A Random Forest Regressor evaluates incoming flight telemetry (`Flight_Hours`, `Temp`, `Dust_Index`, `Takeoff_Cycles`) to predict Turbine Blade wear-and-tear before an aircraft lands.
2. **The State Machine (SQLite + SQLAlchemy):** A normalized relational database maintains strict ACID compliance across three ledgers: `inventory_ledger`, `maintenance_logs`, and `procurement_orders`.
3. **Automated Procurement Logic:** If a predicted maintenance transaction drops the warehouse stock below the critical threshold (100 units), the FastAPI server autonomously issues a database-level Purchase Order to the manufacturer to prevent AOG (Aircraft on Ground) scenarios.
4. **Continuous MLOps Retraining:** The system features an automated feedback loop utilizing FastAPI `BackgroundTasks`. After every 5 live maintenance transactions, the server pulls the latest data from the SQLite `maintenance_logs`, retrains the Random Forest model in the background, and seamlessly overwrites the active `.joblib` weights in production with zero downtime.

---

##  Technical Stack

*   **Machine Learning & MLOps:** Python, Scikit-Learn (Random Forest), Pandas, Joblib
*   **Backend Server & ORM:** FastAPI, Uvicorn, SQLAlchemy, Pydantic
*   **Database:** SQLite (Database-agnostic ORM design, ready for PostgreSQL migration)
*   **Frontend Dashboard:** React.js, Vite, Tailwind CSS, Lucide-React, Axios
*   **Version Control:** Git, GitHub (Feature-Branching)

---

##  Installation & Local Execution

### Prerequisites
*   Python 3.10+
*   Node.js v18+

### 1. Backend & Database Initialization

```bash
cd backend

# Initialize isolated Python environment
python3 -m venv venv
source venv/bin/activate

# Install exact dependency pipeline
pip install fastapi uvicorn sqlalchemy pandas scikit-learn joblib

# Forge the SQLite Database, Seed Inventory, and Train V1.0 Model
python setup_system.py

# Launch the FastAPI MLOps Server
python -m uvicorn main:app --reload
```
*   **API Live Server:** `http://127.0.0.1:8000`

---

### 2. React Overseer Console Setup

Open a **new** terminal tab:

```bash
cd frontend

# Install UI and networking libraries
npm install

# Start the Vite React local development server
npm run dev
```
*   **Web Application URL:** `http://localhost:5173`
```
