import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, ZAxis
} from 'recharts'
import { Timer, TrendingDown, MapPin, Package, Target } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

function App() {
  const [summary, setSummary] = useState(null)
  const [breakdown, setBreakdown] = useState(null)
  const [error, setError] = useState(null)
  const [breakdownDim, setBreakdownDim] = useState('Weatherconditions')
  const [samples, setSamples] = useState([])
  const [liveResult, setLiveResult] = useState(null)
  
  const [formData, setFormData] = useState({
    Distance_km: 5.5,
    Road_traffic_density: 'High',
    Weatherconditions: 'Fog',
    Type_of_vehicle: 'motorcycle',
    multiple_deliveries: 0,
    Delivery_person_Age: 30,
    Delivery_person_Ratings: 4.5
  })

  const fetchInitialData = async (retries = 3) => {
    try {
      setError(null)
      const config = { timeout: 90000 }
      const [summaryRes, samplesRes] = await Promise.all([
        axios.get(`${API_URL}/summary`, config),
        axios.get(`${API_URL}/sample-predictions?n=30`, config)
      ])
      setSummary(summaryRes.data)
      setSamples(samplesRes.data)
    } catch (err) {
      if (retries > 0) {
        setTimeout(() => fetchInitialData(retries - 1), 5000)
      } else {
        setError(err.message || 'Failed to connect to server')
      }
    }
  }

  useEffect(() => {
    fetchInitialData()

    // Keep-alive ping every 10 minutes
    const interval = setInterval(() => {
      axios.get(`${API_URL}/summary`, { timeout: 10000 }).catch(() => {})
    }, 10 * 60 * 1000)
    
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    axios.get(`${API_URL}/breakdown?by=${breakdownDim}`).then(res => {
      // Format data for Recharts
      const formatted = res.data.map(d => ({
        name: d.segment,
        baseline_mae: d.baseline.MAE,
        ml_mae: d.ml_model.MAE
      }))
      setBreakdown(formatted)
    }).catch(console.error)
  }, [breakdownDim])

  const handlePredict = async (e) => {
    e.preventDefault()
    try {
      const res = await axios.post(`${API_URL}/predict`, formData)
      setLiveResult(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: ['Distance_km', 'multiple_deliveries', 'Delivery_person_Age', 'Delivery_person_Ratings'].includes(name) 
        ? Number(value) : value
    }))
  }

  if (error) return (
    <div className="flex flex-col items-center justify-center h-screen space-y-4">
      <div className="text-xl text-amberBase">Connection Error: {error}</div>
      <button onClick={() => fetchInitialData(3)} className="btn-primary mt-4 flex justify-center items-center gap-2">
        Retry
      </button>
    </div>
  )

  if (!summary) return (
    <div className="flex flex-col items-center justify-center h-screen space-y-6">
      <div className="w-12 h-12 border-4 border-tealBase border-t-transparent rounded-full animate-spin"></div>
      <div className="text-lg text-tealBase animate-pulse">Waking up the server (free hosting, can take up to 60 seconds)...</div>
    </div>
  )

  const maxVal = samples.length > 0 ? Math.ceil(Math.max(...samples.map(s => Math.max(s.actual_time, s.baseline_eta, s.ml_eta)))) : 60;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-surfaceHighlight bg-surface/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Target className="text-tealBase w-8 h-8" />
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
              ETA Accuracy Tracker
            </h1>
          </div>
          <div className="text-sm text-gray-400 max-w-lg text-right">
            Benchmarking delivery platforms (like Zomato/Swiggy) using ML. We compare a simulated naive 
            <span className="text-amberBase ml-1">Promised ETA</span> vs our <span className="text-tealBase ml-1">ML Predicted ETA</span> against actual delivery times to measure reliability.
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        
        {/* Top KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity text-amberBase"><TrendingDown size={48} /></div>
            <h3 className="text-gray-400 text-sm font-medium">Baseline MAE</h3>
            <div className="text-3xl font-bold mt-2 text-white">{summary.Baseline.MAE} <span className="text-lg font-normal text-gray-500">min</span></div>
            <div className="text-xs text-gray-500 mt-2">Naive distance formula</div>
          </div>
          <div className="card relative overflow-hidden group border-tealBase/30">
            <div className="absolute inset-0 bg-gradient-to-br from-tealBase/10 to-transparent"></div>
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity text-tealBase"><Timer size={48} /></div>
            <h3 className="text-tealBase text-sm font-medium relative z-10">ML Model MAE</h3>
            <div className="text-4xl font-bold mt-1 text-white relative z-10">{summary.ML_Model.MAE} <span className="text-lg font-normal text-gray-500">min</span></div>
            <div className="text-xs text-success mt-2 font-medium relative z-10">↓ {summary.Improvement.MAE_improvement_pct}% Improvement</div>
          </div>
          <div className="card relative overflow-hidden">
            <h3 className="text-gray-400 text-sm font-medium">RMSE Comparison</h3>
            <div className="mt-2 flex items-end gap-2">
              <span className="text-2xl font-bold text-gray-300 line-through decoration-amberBase/50">{summary.Baseline.RMSE}</span>
              <span className="text-3xl font-bold text-white">{summary.ML_Model.RMSE}</span>
            </div>
            <div className="text-xs text-gray-500 mt-2">Root Mean Squared Error</div>
          </div>
          <div className="card relative overflow-hidden">
            <h3 className="text-gray-400 text-sm font-medium">Deliveries within ±5 mins</h3>
            <div className="mt-2 flex justify-between items-center">
              <div>
                <div className="text-sm text-gray-500">Baseline</div>
                <div className="text-xl font-bold text-gray-300">{summary.Baseline.Within_5_min_pct}%</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-tealBase font-medium">ML Model</div>
                <div className="text-2xl font-bold text-white">{summary.ML_Model.Within_5_min_pct}%</div>
              </div>
            </div>
            <div className="w-full bg-surfaceHighlight h-2 rounded-full mt-3 overflow-hidden flex">
               <div className="bg-amberBase h-full" style={{width: `${summary.Baseline.Within_5_min_pct}%`}}></div>
               <div className="bg-tealBase h-full" style={{width: `${summary.ML_Model.Within_5_min_pct - summary.Baseline.Within_5_min_pct}%`}}></div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Charts Section */}
          <div className="lg:col-span-2 space-y-8">
            {/* Breakdown Chart */}
            <div className="card">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-white">Error Breakdown (MAE)</h2>
                <select 
                  className="bg-surfaceHighlight border border-gray-700 text-white rounded-md px-3 py-1.5 text-sm outline-none"
                  value={breakdownDim}
                  onChange={e => setBreakdownDim(e.target.value)}
                >
                  <option value="Weatherconditions">By Weather</option>
                  <option value="Road_traffic_density">By Traffic</option>
                  <option value="City">By City</option>
                  <option value="Type_of_vehicle">By Vehicle</option>
                </select>
              </div>
              <div className="h-80 w-full">
                {breakdown ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={breakdown} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2A2A40" vertical={false} />
                      <XAxis dataKey="name" stroke="#6B7280" tick={{fill: '#9CA3AF', fontSize: 12}} />
                      <YAxis stroke="#6B7280" tick={{fill: '#9CA3AF', fontSize: 12}} />
                      <RechartsTooltip 
                        contentStyle={{ backgroundColor: '#1a1d24', borderColor: '#2a2e39', borderRadius: '8px' }}
                        itemStyle={{ color: '#E5E7EB' }}
                      />
                      <Legend wrapperStyle={{ paddingTop: '20px' }}/>
                      <Bar name="Baseline MAE" dataKey="baseline_mae" fill="#F59E0B" radius={[4, 4, 0, 0]} maxBarSize={50} />
                      <Bar name="ML Model MAE" dataKey="ml_mae" fill="#14B8A6" radius={[4, 4, 0, 0]} maxBarSize={50} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : <div className="animate-pulse bg-surfaceHighlight w-full h-full rounded-lg"></div>}
              </div>
            </div>

            {/* Scatter Plot */}
            <div className="card">
              <h2 className="text-xl font-bold text-white mb-2">Prediction vs Actual</h2>
              <p className="text-sm text-gray-400 mb-6">Closer to the diagonal line is better. Notice how the ML model tightly hugs the line compared to the naive baseline scatter.</p>
              
              <div className="grid grid-cols-2 gap-4 h-80">
                <div className="h-full border-r border-surfaceHighlight pr-2">
                  <p className="text-center text-xs text-amberBase mb-2">Baseline ETA</p>
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: -20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2e39" />
                      <XAxis type="number" dataKey="actual_time" name="Actual (min)" stroke="#6B7280" domain={[0, 'dataMax + 10']} />
                      <YAxis type="number" dataKey="baseline_eta" name="Predicted (min)" stroke="#6B7280" domain={[0, 'dataMax + 10']} />
                      <RechartsTooltip cursor={{strokeDasharray: '3 3'}} contentStyle={{ backgroundColor: '#1a1d24', borderColor: '#2a2e39', borderRadius: '8px' }} />
                      <Scatter name="Baseline" data={samples} fill="#F59E0B" opacity={0.6} />
                      {/* Perfect prediction line */}
                      <Scatter data={[{actual_time:0, baseline_eta:0}, {actual_time:maxVal, baseline_eta:maxVal}]} line={{stroke: '#F59E0B', strokeWidth: 1}} shape={() => null} />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
                <div className="h-full pl-2">
                  <p className="text-center text-xs text-tealBase mb-2">ML ETA</p>
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: -20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2e39" />
                      <XAxis type="number" dataKey="actual_time" name="Actual (min)" stroke="#6B7280" domain={[0, 'dataMax + 10']} />
                      <YAxis type="number" dataKey="ml_eta" name="Predicted (min)" stroke="#6B7280" domain={[0, 'dataMax + 10']} />
                      <RechartsTooltip cursor={{strokeDasharray: '3 3'}} contentStyle={{ backgroundColor: '#1a1d24', borderColor: '#2a2e39', borderRadius: '8px' }} />
                      <Scatter name="ML" data={samples} fill="#14B8A6" opacity={0.6} />
                      <Scatter data={[{actual_time:0, ml_eta:0}, {actual_time:maxVal, ml_eta:maxVal}]} line={{stroke: '#14B8A6', strokeWidth: 1}} shape={() => null} />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-8">
            {/* Try it yourself panel */}
            <div className="card border-tealBase/30 relative">
              <div className="absolute -top-3 -right-3 w-20 h-20 bg-tealBase/20 blur-2xl rounded-full"></div>
              <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2"><MapPin size={20} className="text-tealBase"/> Live Prediction</h2>
              
              <form onSubmit={handlePredict} className="space-y-4 relative z-10">
                <div>
                  <label className="label">Distance (km)</label>
                  <input type="number" step="0.1" name="Distance_km" value={formData.Distance_km} onChange={handleInputChange} className="input-field" required />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="label">Traffic</label>
                    <select name="Road_traffic_density" value={formData.Road_traffic_density} onChange={handleInputChange} className="input-field">
                      <option value="Low">Low</option>
                      <option value="Medium">Medium</option>
                      <option value="High">High</option>
                      <option value="Jam">Jam</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Weather</label>
                    <select name="Weatherconditions" value={formData.Weatherconditions} onChange={handleInputChange} className="input-field">
                      <option value="Sunny">Sunny</option>
                      <option value="Cloudy">Cloudy</option>
                      <option value="Fog">Fog</option>
                      <option value="Stormy">Stormy</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="label">Vehicle</label>
                    <select name="Type_of_vehicle" value={formData.Type_of_vehicle} onChange={handleInputChange} className="input-field">
                      <option value="motorcycle">Motorcycle</option>
                      <option value="scooter">Scooter</option>
                      <option value="electric_scooter">Electric Scooter</option>
                      <option value="bicycle">Bicycle</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Batched Orders</label>
                    <input type="number" name="multiple_deliveries" value={formData.multiple_deliveries} onChange={handleInputChange} className="input-field" />
                  </div>
                </div>

                <button type="submit" className="btn-primary mt-4 flex justify-center items-center gap-2">
                  <Package size={18} /> Calculate ETA
                </button>
              </form>

              {liveResult && (
                <div className="mt-6 p-4 bg-black/40 rounded-lg border border-gray-800 animate-fade-in">
                  <div className="text-center mb-2 text-sm text-gray-400">Result</div>
                  <div className="flex justify-between items-center">
                    <div className="text-center">
                      <div className="text-xs text-amberBase uppercase tracking-wider">Baseline</div>
                      <div className="text-2xl font-bold text-gray-300">{liveResult.baseline_eta} <span className="text-xs font-normal text-gray-500">m</span></div>
                    </div>
                    <div className="w-px h-8 bg-gray-700"></div>
                    <div className="text-center">
                      <div className="text-xs text-tealBase uppercase tracking-wider font-bold">ML Prediction</div>
                      <div className="text-3xl font-bold text-white">{liveResult.ml_eta} <span className="text-xs font-normal text-gray-400">m</span></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Sample Table */}
            <div className="card">
              <h2 className="text-sm font-bold text-gray-300 mb-4 uppercase tracking-wider">Recent Deliveries</h2>
              <div className="overflow-y-auto max-h-64 pr-2">
                <table className="w-full text-left text-sm">
                  <thead className="text-xs text-gray-500 sticky top-0 bg-surface">
                    <tr>
                      <th className="pb-2 font-medium">Actual</th>
                      <th className="pb-2 font-medium text-center text-amberBase">Baseline</th>
                      <th className="pb-2 font-medium text-right text-tealBase">ML ETA</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-surfaceHighlight">
                    {samples.slice(0, 10).map((s, i) => (
                      <tr key={i} className="hover:bg-surfaceHighlight/50 transition-colors">
                        <td className="py-2">{s.actual_time}m</td>
                        <td className="py-2 text-center text-gray-400">{s.baseline_eta}m</td>
                        <td className="py-2 text-right font-medium text-tealBase">{s.ml_eta}m</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        </div>
      </main>
    </div>
  )
}

export default App
