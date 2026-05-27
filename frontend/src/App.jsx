import React, { useState } from "react";
import axios from "axios";
import { Plane, Wrench, Package, BrainCircuit, AlertTriangle, CheckCircle, ShoppingCart } from "lucide-react";

function App() {
  // Form State
  const [aircraftId, setAircraftId] = useState("BOEING-777-X1");
  const [flightHours, setFlightHours] = useState(1500);
  const [temp, setTemp] = useState(45);
  const [dust, setDust] = useState(8.5);
  const [cycles, setCycles] = useState(300);

  // System State
  const [isLoading, setIsLoading] = useState(false);
  const [stock, setStock] = useState(500); // We know it starts at 500
  const [logsCount, setLogsCount] = useState(0);
  const [latestResult, setLatestResult] = useState(null);
  const [retrainAlert, setRetrainAlert] = useState(false);

  const handleAuthorize = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setRetrainAlert(false);

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/inspect", {
        aircraft_id: aircraftId,
        flight_hours: parseFloat(flightHours),
        avg_operating_temp: parseFloat(temp),
        air_dust_index: parseFloat(dust),
        takeoff_cycles: parseInt(cycles),
      });

      const data = response.data;
      setLatestResult(data);
      setStock(data.remaining_stock);
      setLogsCount(data.total_database_logs);

      // If the log count is a multiple of 5, the backend triggered MLOps retraining!
      if (data.total_database_logs % 5 === 0) {
        setRetrainAlert(true);
      }
    } catch (error) {
      console.error("API Error", error);
      alert("AOG ERROR: Insufficient stock or server offline.");
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans p-6">
      
      {/* Top Navbar */}
      <header className="max-w-6xl mx-auto mb-8 flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <Plane className="text-blue-500 w-8 h-8" />
          <div>
            <h1 className="text-2xl font-black text-white tracking-widest uppercase">AeroPulse AI</h1>
            <p className="text-xs text-slate-500 font-mono">MRO Predictive Supply Chain Console</p>
          </div>
        </div>
        <div className="flex space-x-4">
          <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1 rounded-full border border-slate-800">
            <Package className="w-4 h-4 text-emerald-500" />
            <span className="text-xs font-mono font-bold text-white">STOCK: {stock} UNITS</span>
          </div>
          <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1 rounded-full border border-slate-800">
            <BrainCircuit className="w-4 h-4 text-purple-500" />
            <span className="text-xs font-mono font-bold text-white">DB LOGS: {logsCount}</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Column: Overseer Input Form */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center space-x-2 mb-6 border-b border-slate-800 pb-2">
            <Wrench className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-bold text-white uppercase tracking-wider">Incoming Aircraft Telemetry</h2>
          </div>

          <form onSubmit={handleAuthorize} className="space-y-5">
            <div>
              <label className="block text-xs font-mono text-slate-500 mb-1">AIRCRAFT TAIL ID</label>
              <input type="text" value={aircraftId} onChange={e => setAircraftId(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white focus:border-blue-500 outline-none font-mono" />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono text-slate-500 mb-1">FLIGHT HOURS</label>
                <input type="number" value={flightHours} onChange={e => setFlightHours(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white focus:border-blue-500 outline-none font-mono" />
              </div>
              <div>
                <label className="block text-xs font-mono text-slate-500 mb-1">TAKEOFF CYCLES</label>
                <input type="number" value={cycles} onChange={e => setCycles(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white focus:border-blue-500 outline-none font-mono" />
              </div>
              <div>
                <label className="block text-xs font-mono text-slate-500 mb-1">AVG TEMP (°C)</label>
                <input type="number" value={temp} onChange={e => setTemp(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white focus:border-blue-500 outline-none font-mono" />
              </div>
              <div>
                <label className="block text-xs font-mono text-slate-500 mb-1">AIR DUST INDEX</label>
                <input type="number" step="0.1" value={dust} onChange={e => setDust(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white focus:border-blue-500 outline-none font-mono" />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full mt-6 bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl transition-all uppercase tracking-widest flex justify-center items-center space-x-2"
            >
              {isLoading ? "Processing..." : "Authorize AI Inspection & Maintenance"}
            </button>
          </form>
        </div>

        {/* Right Column: Execution Results & System Alerts */}
        <div className="space-y-6">
          
          {/* Waiting State */}
          {!latestResult && (
            <div className="h-full border border-slate-800 border-dashed rounded-2xl flex flex-col items-center justify-center text-slate-600 space-y-4 min-h-[400px]">
              <Plane className="w-12 h-12 opacity-50" />
              <p className="font-mono text-sm uppercase tracking-widest">Awaiting Aircraft Arrival</p>
            </div>
          )}

          {/* Results State */}
          {latestResult && (
            <>
              {/* Inspection Card */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Inspection Report</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-center">
                    <p className="text-xs text-slate-500 font-mono mb-1">AI WEAR PREDICTION</p>
                    <p className="text-3xl font-black text-white">{latestResult.predicted_wear}</p>
                    <p className="text-xs text-slate-600 mt-1">Turbine Blades</p>
                  </div>
                  <div className="bg-blue-900/20 border border-blue-900/50 rounded-xl p-4 text-center">
                    <p className="text-xs text-blue-400 font-mono mb-1">ACTUAL REPLACED</p>
                    <p className="text-3xl font-black text-blue-400">{latestResult.actual_replaced}</p>
                    <p className="text-xs text-blue-900 mt-1">Mechanic Verified</p>
                  </div>
                </div>
              </div>

              {/* Automated Logistics Alerts */}
              <div className="space-y-3">
                {/* Always show success of transaction */}
                <div className="bg-emerald-900/20 border border-emerald-900/50 rounded-xl p-4 flex items-center space-x-3">
                  <CheckCircle className="w-6 h-6 text-emerald-500 shrink-0" />
                  <div>
                    <p className="text-sm font-bold text-emerald-400">Maintenance Logged to SQLite</p>
                    <p className="text-xs text-emerald-600/80">Inventory securely deducted.</p>
                  </div>
                </div>

                {/* Show if Auto-Procurement triggered */}
                {latestResult.procurement_triggered && (
                  <div className="bg-amber-900/20 border border-amber-900/50 rounded-xl p-4 flex items-center space-x-3 animate-pulse">
                    <ShoppingCart className="w-6 h-6 text-amber-500 shrink-0" />
                    <div>
                      <p className="text-sm font-bold text-amber-400">Low Stock: Auto-Procurement Triggered</p>
                      <p className="text-xs text-amber-600/80">200 units ordered from manufacturer.</p>
                    </div>
                  </div>
                )}

                {/* Show if MLOps Retraining triggered */}
                {retrainAlert && (
                  <div className="bg-purple-900/20 border border-purple-900/50 rounded-xl p-4 flex items-center space-x-3">
                    <BrainCircuit className="w-6 h-6 text-purple-500 shrink-0" />
                    <div>
                      <p className="text-sm font-bold text-purple-400">MLOps Alert: Model Retrained</p>
                      <p className="text-xs text-purple-600/80">AI model updated automatically based on new data.</p>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}

        </div>
      </main>
    </div>
  );
}

export default App;