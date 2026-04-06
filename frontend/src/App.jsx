import React, { useState } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area, BarChart, Bar
} from 'recharts';
import { Activity, Database, Truck, Factory, Play, ShieldAlert } from 'lucide-react';

const API_URL = "http://localhost:8000";

function App() {
  const [params, setParams] = useState({
    p: 2,
    l: 2,
    j: 4,
    t: 30
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setParams(prev => ({
      ...prev,
      [name]: parseInt(value) || 0
    }));
  };

  const handleSolve = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const response = await axios.post(`${API_URL}/solve`, params);
      
      if (response.data.status === 'OPTIMAL') {
        // Transform data for charts
        // prod_t is array of {p, t, val}
        // We need data by T for Recharts: [{name: 0, p0: val, p1: val}, ...]
        const T = response.data.metadata.T;
        const P = response.data.metadata.P;
        const J = response.data.metadata.J;

        const formatForTime = (rawData) => {
          let formatted = [];
          for (let time = 0; time < T; time++) {
            let row = { name: `T${time}` };
            for (let prod = 0; prod < P; prod++) {
               const item = rawData.find(d => d.t === time && d.p === prod);
               row[`Produto ${prod}`] = item ? item.val : 0;
            }
            formatted.push(row);
          }
          return formatted;
        };

        const formatForCDs = (rawData, cdIndex) => {
          let formatted = [];
          for (let time = 0; time < T; time++) {
            let row = { name: `T${time}` };
            for (let prod = 0; prod < P; prod++) {
               const item = rawData.find(d => d.t === time && d.p === prod && d.j === cdIndex);
               row[`Produto ${prod}`] = item ? item.val : 0;
            }
            formatted.push(row);
          }
          return formatted;
        };

        setResults({
          objective: response.data.objective,
          metadata: { T, P, J },
          plots: {
            prod_t: formatForTime(response.data.plots.prod_t),
            est_f_t: formatForTime(response.data.plots.est_f_t),
            est_cd_agg_t: formatForTime(response.data.plots.est_cd_agg_t),
            fluxo_cd: Array.from({length: J}).map((_, j) => formatForCDs(response.data.plots.flux_cd_t, j))
          }
        });
      } else {
        setError(response.data.message || "Optimization failed.");
      }
    } catch (err) {
      setError(err.message || "Network error. Make sure the FastAPI backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const colors = ["#58a6ff", "#3fb950", "#d29922", "#f85149", "#dd7878"];

  return (
    <div className="app-container">
      <header className="header">
        <h1>SaOP Optimizer</h1>
        <p>Advanced Capacitated Lot Sizing Problem Resolution & Analytics</p>
      </header>

      <div className="glass-card" style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.2rem' }}>
          <Activity size={24} color="var(--accent-primary)" />
          Problem Parameters
        </h2>
        
        <div className="control-panel">
          <div className="input-group">
            <label>Products (P)</label>
            <input type="number" name="p" value={params.p} onChange={handleInputChange} min="1" max="10" />
          </div>
          <div className="input-group">
            <label>Production Lines (L)</label>
            <input type="number" name="l" value={params.l} onChange={handleInputChange} min="1" max="10" />
          </div>
          <div className="input-group">
            <label>Distribution Centers (J)</label>
            <input type="number" name="j" value={params.j} onChange={handleInputChange} min="1" max="20" />
          </div>
          <div className="input-group">
            <label>Time Periods (T)</label>
            <input type="number" name="t" value={params.t} onChange={handleInputChange} min="1" max="100" />
          </div>
        </div>

        <div className="action-bar" style={{ marginBottom: 0 }}>
          <button className="btn-primary" onClick={handleSolve} disabled={loading}>
            {loading ? <div className="spinner"></div> : <Play size={20} />}
            {loading ? 'Optimizing...' : 'Run Optimization'}
          </button>
        </div>
      </div>

      {error && (
        <div className="glass-card" style={{ border: '1px solid var(--accent-danger)', backgroundColor: 'rgba(218, 54, 51, 0.1)', color: 'var(--text-primary)', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <ShieldAlert color="var(--accent-danger)" size={28} />
          <div>
            <h3 style={{ color: 'var(--accent-danger)' }}>Optimization Failed</h3>
            <p>{error}</p>
          </div>
        </div>
      )}

      {results && !loading && (
        <div className="results-section">
          <div className="results-header">
            <div className="metric-badge">
              <span>Optimal Minimum Cost</span>
              <strong>{new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(results.objective)}</strong>
            </div>
          </div>

          <div className="charts-grid">
            {/* 1. Producao Fabrica */}
            <div className="glass-card chart-card">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Factory size={20} />
                Total Production at Factory
              </h3>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={results.plots.prod_t} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fontSize: 12}} />
                    <YAxis stroke="var(--text-secondary)" tick={{fontSize: 12}} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(13,17,23,0.9)', borderColor: 'var(--surface-border)', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                    <Legend />
                    {Array.from({length: results.metadata.P}).map((_, i) => (
                      <Line key={i} type="monotone" dataKey={`Produto ${i}`} stroke={colors[i % colors.length]} strokeWidth={3} dot={{r: 4, strokeWidth: 0}} activeDot={{r: 6}} />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 2. Estoque Fabrica */}
            <div className="glass-card chart-card">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Database size={20} />
                Factory Inventory
              </h3>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={results.plots.est_f_t} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fontSize: 12}} />
                    <YAxis stroke="var(--text-secondary)" tick={{fontSize: 12}} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(13,17,23,0.9)', borderColor: 'var(--surface-border)', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                    <Legend />
                    {Array.from({length: results.metadata.P}).map((_, i) => (
                      <Area key={i} type="monotone" dataKey={`Produto ${i}`} fill={colors[i % colors.length]} stroke={colors[i % colors.length]} fillOpacity={0.3} strokeWidth={2} />
                    ))}
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 3. Estoque CD Agregado */}
            <div className="glass-card chart-card">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Activity size={20} />
                Aggregated Distribution Center Inventory
              </h3>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={results.plots.est_cd_agg_t} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fontSize: 12}} />
                    <YAxis stroke="var(--text-secondary)" tick={{fontSize: 12}} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(13,17,23,0.9)', borderColor: 'var(--surface-border)', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                    <Legend />
                    {Array.from({length: results.metadata.P}).map((_, i) => (
                      <Bar key={i} dataKey={`Produto ${i}`} fill={colors[i % colors.length]} radius={[4, 4, 0, 0]} />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>

          <h2 style={{ marginTop: '3rem', marginBottom: '2rem', textAlign: 'center' }}>Flux from Factory to Distribution Centers</h2>
          <div className="charts-grid">
             {results.plots.fluxo_cd.map((dataForCD, cdIndex) => (
               <div key={cdIndex} className="glass-card chart-card">
                 <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                   <Truck size={20} />
                   Flux to CD {cdIndex}
                 </h3>
                 <div className="chart-container">
                   <ResponsiveContainer width="100%" height="100%">
                     <LineChart data={dataForCD} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                       <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                       <XAxis dataKey="name" stroke="var(--text-secondary)" tick={{fontSize: 12}} />
                       <YAxis stroke="var(--text-secondary)" tick={{fontSize: 12}} />
                       <Tooltip contentStyle={{ backgroundColor: 'rgba(13,17,23,0.9)', borderColor: 'var(--surface-border)', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                       <Legend />
                       {Array.from({length: results.metadata.P}).map((_, i) => (
                         <Line key={i} type="monotone" dataKey={`Produto ${i}`} stroke={colors[i % colors.length]} strokeWidth={2} dot={{r: 3, strokeWidth: 0}} />
                       ))}
                     </LineChart>
                   </ResponsiveContainer>
                 </div>
               </div>
             ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
