import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Users, DollarSign, TrendingUp, AlertTriangle, Search, Activity, ShieldAlert } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const API_BASE = "http://127.0.0.1:8000";

interface Summary {
  total_customers: number;
  total_revenue: number;
  average_order_value: number;
  churn_rate: number;
}

interface Customer {
  Customer_ID: string;
  recency_days: number;
  frequency: number;
  monetary: number;
  avg_basket_size: number;
  avg_item_price: number;
  churn: number;
}

export default function App() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'customers' | 'predict'>('overview');

  // Prediction Form State
  const [predInput, setPredInput] = useState({
    recency_days: 30,
    frequency: 3,
    monetary: 250.0,
    avg_basket_size: 5.0,
    avg_item_price: 15.0
  });
  const [predictionResult, setPredictionResult] = useState<any>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const summaryRes = await axios.get(`${API_BASE}/api/summary`);
      setSummary(summaryRes.data);

      const custRes = await axios.get(`${API_BASE}/api/customers?limit=100`);
      setCustomers(custRes.data.customers);
    } catch (err) {
      console.error("Error connecting to FastAPI backend:", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_BASE}/api/predict`, predInput);
      setPredictionResult(res.data);
    } catch (err) {
      console.error("Prediction failed:", err);
    }
  };

  const filteredCustomers = customers.filter(c => 
    c.Customer_ID.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-xs">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <Activity className="h-8 w-8 text-blue-600" />
            <h1 className="text-xl font-bold tracking-tight">Customer Behavior & Churn Analytics</h1>
          </div>
          <nav className="flex space-x-2">
            <button 
              onClick={() => setActiveTab('overview')} 
              className={`px-4 py-2 rounded-lg font-medium text-sm transition ${activeTab === 'overview' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              Overview
            </button>
            <button 
              onClick={() => setActiveTab('customers')} 
              className={`px-4 py-2 rounded-lg font-medium text-sm transition ${activeTab === 'customers' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              Customer Table
            </button>
            <button 
              onClick={() => setActiveTab('predict')} 
              className={`px-4 py-2 rounded-lg font-medium text-sm transition ${activeTab === 'predict' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              Churn Predictor
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {loading ? (
          <div className="text-center py-20 text-gray-500 font-medium">Connecting to backend and loading metrics...</div>
        ) : (
          <>
            {/* OVERVIEW TAB */}
            {activeTab === 'overview' && summary && (
              <div className="space-y-8">
                {/* KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Total Customers</p>
                      <h3 className="text-2xl font-bold mt-1">{summary.total_customers.toLocaleString()}</h3>
                    </div>
                    <Users className="h-10 w-10 text-blue-500 bg-blue-50 p-2 rounded-lg" />
                  </div>
                  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Total Revenue</p>
                      <h3 className="text-2xl font-bold mt-1">${summary.total_revenue.toLocaleString()}</h3>
                    </div>
                    <DollarSign className="h-10 w-10 text-emerald-500 bg-emerald-50 p-2 rounded-lg" />
                  </div>
                  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Average Order Value</p>
                      <h3 className="text-2xl font-bold mt-1">${summary.average_order_value.toFixed(2)}</h3>
                    </div>
                    <TrendingUp className="h-10 w-10 text-indigo-500 bg-indigo-50 p-2 rounded-lg" />
                  </div>
                  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Churn Rate</p>
                      <h3 className="text-2xl font-bold mt-1">{(summary.churn_rate * 100).toFixed(1)}%</h3>
                    </div>
                    <AlertTriangle className="h-10 w-10 text-rose-500 bg-rose-50 p-2 rounded-lg" />
                  </div>
                </div>

                {/* Quick Chart */}
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-xs">
                  <h3 className="text-lg font-semibold mb-4">Customer Monetary Distribution Sample</h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={customers.slice(0, 15)}>
                        <XAxis dataKey="Customer_ID" tick={{ fontSize: 10 }} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="monetary" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}

            {/* CUSTOMER TABLE TAB */}
            {activeTab === 'customers' && (
              <div className="bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden">
                <div className="p-5 border-b border-gray-200 flex justify-between items-center">
                  <h3 className="text-lg font-semibold">Customer Directory & Behavior</h3>
                  <div className="relative w-72">
                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                    <input 
                      type="text" 
                      placeholder="Search Customer ID..." 
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        <th className="py-3 px-6">Customer ID</th>
                        <th className="py-3 px-6">Recency (Days)</th>
                        <th className="py-3 px-6">Frequency</th>
                        <th className="py-3 px-6">Total Spend ($)</th>
                        <th className="py-3 px-6">Avg Basket</th>
                        <th className="py-3 px-6">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 text-sm">
                      {filteredCustomers.map((c, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="py-4 px-6 font-medium text-blue-600">{c.Customer_ID}</td>
                          <td className="py-4 px-6">{c.recency_days} days</td>
                          <td className="py-4 px-6">{c.frequency}</td>
                          <td className="py-4 px-6 font-semibold">${c.monetary.toFixed(2)}</td>
                          <td className="py-4 px-6">${c.avg_basket_size.toFixed(2)}</td>
                          <td className="py-4 px-6">
                            <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${c.churn === 1 ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>
                              {c.churn === 1 ? 'Churned' : 'Active'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* PREDICT TAB */}
            {activeTab === 'predict' && (
              <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl border border-gray-200 shadow-xs">
                <h3 className="text-lg font-semibold mb-6 flex items-center">
                  <ShieldAlert className="mr-2 h-5 w-5 text-blue-600" />
                  Real-Time Churn Risk Predictor
                </h3>
                <form onSubmit={handlePredict} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Recency (Days)</label>
                      <input 
                        type="number" 
                        value={predInput.recency_days}
                        onChange={e => setPredInput({...predInput, recency_days: Number(e.target.value)})}
                        className="w-full p-2.5 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Frequency (Orders)</label>
                      <input 
                        type="number" 
                        value={predInput.frequency}
                        onChange={e => setPredInput({...predInput, frequency: Number(e.target.value)})}
                        className="w-full p-2.5 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Monetary ($)</label>
                      <input 
                        type="number" 
                        value={predInput.monetary}
                        onChange={e => setPredInput({...predInput, monetary: Number(e.target.value)})}
                        className="w-full p-2.5 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Avg Basket Size</label>
                      <input 
                        type="number" 
                        value={predInput.avg_basket_size}
                        onChange={e => setPredInput({...predInput, avg_basket_size: Number(e.target.value)})}
                        className="w-full p-2.5 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Avg Item Price ($)</label>
                      <input 
                        type="number" 
                        value={predInput.avg_item_price}
                        onChange={e => setPredInput({...predInput, avg_item_price: Number(e.target.value)})}
                        className="w-full p-2.5 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                  </div>
                  <button type="submit" className="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition">
                    Predict Churn Risk
                  </button>
                </form>

                {predictionResult && (
                  <div className="mt-6 p-5 bg-gray-50 border border-gray-200 rounded-lg flex justify-between items-center">
                    <div>
                      <p className="text-sm text-gray-500">Risk Assessment</p>
                      <p className="text-xl font-bold mt-0.5">{predictionResult.risk_level} Risk</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">Churn Probability</p>
                      <p className="text-xl font-bold mt-0.5 text-blue-600">{(predictionResult.churn_probability * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}