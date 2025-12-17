/**
 * Premium Production Insights Component
 * UI-UX-PROMAX: Stunning, modern, and highly interactive production analytics dashboard
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
    TrendingUp, Factory, Package, AlertCircle, Calendar, Filter,
    BarChart3, PieChart, Activity, Clock, CheckCircle, XCircle, Loader2
} from 'lucide-react';
import {
    BarChart, Bar, LineChart, Line, PieChart as RePieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    Area, AreaChart
} from 'recharts';

// Interfaces
interface MTOData {
    status: string;
    summary: {
        total_orders: number;
        avg_prep_days: number;
        avg_production_days: number;
        avg_delivery_days: number;
        avg_total_cycle_days: number;
        avg_yield_rate: number;
    };
    timeline_breakdown: Array<{
        phase: string;
        avg_days: number;
        description: string;
    }>;
    orders: any[];
}

interface MTSData {
    status: string;
    summary: {
        total_orders: number;
        avg_planning_days: number;
        avg_production_days: number;
        avg_total_lead_time: number;
        avg_yield_rate: number;
    };
    mrp_performance: Array<{
        mrp_controller: string;
        total_orders: number;
        avg_lead_time: number;
        avg_yield: number;
    }>;
    orders: any[];
}

interface VarianceData {
    status: string;
    summary: {
        total_orders: number;
        perfect_match: number;
        over_production: number;
        under_production: number;
        perfect_match_rate: number;
        avg_variance_pct: number;
    };
    variance_distribution: Array<{
        category: string;
        count: number;
    }>;
    orders: any[];
}

const COLORS = {
    primary: '#6366f1',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',
    purple: '#8b5cf6',
    teal: '#14b8a6'
};

const ProductionInsights: React.FC = () => {
    // State
    const [startDate, setStartDate] = useState(() => {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
    });
    const [endDate, setEndDate] = useState(() => {
        const now = new Date();
        const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        return `${lastDay.getFullYear()}-${String(lastDay.getMonth() + 1).padStart(2, '0')}-${String(lastDay.getDate()).padStart(2, '0')}`;
    });
    const [mrpFilter, setMrpFilter] = useState('All');
    const [activeView, setActiveView] = useState<'mto' | 'mts' | 'variance'>('mto');

    const [mtoData, setMtoData] = useState<MTOData | null>(null);
    const [mtsData, setMtsData] = useState<MTSData | null>(null);
    const [varianceData, setVarianceData] = useState<VarianceData | null>(null);
    const [loading, setLoading] = useState(false);

    // Fetch data
    const fetchData = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({
                start_date: startDate,
                end_date: endDate,
                mrp_filter: mrpFilter
            });

            const [mtoRes, mtsRes, varianceRes] = await Promise.all([
                fetch(`http://localhost:8000/api/production/mto-timeline?${params}`),
                fetch(`http://localhost:8000/api/production/mts-analysis?${params}`),
                fetch(`http://localhost:8000/api/production/variance?${params}`)
            ]);

            const [mto, mts, variance] = await Promise.all([
                mtoRes.json(),
                mtsRes.json(),
                varianceRes.json()
            ]);

            setMtoData(mto);
            setMtsData(mts);
            setVarianceData(variance);
        } catch (error) {
            console.error('Error fetching production data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [startDate, endDate, mrpFilter]);

    // Loading state
    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <Loader2 className="w-12 h-12 animate-spin text-indigo-600 mx-auto mb-4" />
                    <p className="text-gray-600 font-medium">Loading production insights...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Premium Header with Gradient */}
            <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl shadow-2xl p-8 text-white">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-3xl font-bold mb-2 flex items-center gap-3">
                            <Factory className="w-8 h-8" />
                            Production Intelligence Hub
                        </h2>
                        <p className="text-indigo-100 text-lg">Real-time insights into MTO, MTS, and quality metrics</p>
                    </div>
                    <div className="bg-white/20 backdrop-blur-lg rounded-xl p-4">
                        <p className="text-sm text-indigo-100">Total Orders</p>
                        <p className="text-4xl font-bold">{(mtoData?.summary.total_orders || 0) + (mtsData?.summary.total_orders || 0)}</p>
                    </div>
                </div>
            </div>

            {/* Filters - Premium Design */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <div className="flex items-center gap-6 flex-wrap">
                    <div className="flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-gray-500" />
                        <span className="text-sm font-semibold text-gray-700">Period:</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div>
                            <label className="text-xs text-gray-500 block mb-1">From</label>
                            <input
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                className="px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:outline-none transition-colors"
                            />
                        </div>
                        <div>
                            <label className="text-xs text-gray-500 block mb-1">To</label>
                            <input
                                type="date"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                                className="px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:outline-none transition-colors"
                            />
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <Filter className="w-5 h-5 text-gray-500" />
                        <select
                            value={mrpFilter}
                            onChange={(e) => setMrpFilter(e.target.value)}
                            className="px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:outline-none bg-white transition-colors font-medium"
                        >
                            <option value="All">All Production Groups</option>
                            <option value="P01">P01 - Finished Goods</option>
                            <option value="P02">P02 - Semi-Filling</option>
                            <option value="P03">P03 - Semi-Base</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* View Selector - Pill Style */}
            <div className="flex gap-3">
                <button
                    onClick={() => setActiveView('mto')}
                    className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all duration-300 ${activeView === 'mto'
                            ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg scale-105'
                            : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
                        }`}
                >
                    <div className="flex items-center justify-center gap-2">
                        <Package className="w-5 h-5" />
                        <span>MTO Timeline</span>
                    </div>
                </button>
                <button
                    onClick={() => setActiveView('mts')}
                    className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all duration-300 ${activeView === 'mts'
                            ? 'bg-gradient-to-r from-green-600 to-teal-600 text-white shadow-lg scale-105'
                            : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
                        }`}
                >
                    <div className="flex items-center justify-center gap-2">
                        <TrendingUp className="w-5 h-5" />
                        <span>MTS Efficiency</span>
                    </div>
                </button>
                <button
                    onClick={() => setActiveView('variance')}
                    className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all duration-300 ${activeView === 'variance'
                            ? 'bg-gradient-to-r from-amber-600 to-orange-600 text-white shadow-lg scale-105'
                            : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
                        }`}
                >
                    <div className="flex items-center justify-center gap-2">
                        <Activity className="w-5 h-5" />
                        <span>Quantity Variance</span>
                    </div>
                </button>
            </div>

            {/* MTO View */}
            {activeView === 'mto' && mtoData && (
                <div className="space-y-6 animate-fadeIn">
                    {/* KPI Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
                            <Clock className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Prep Time</p>
                            <p className="text-3xl font-bold">{mtoData.summary.avg_prep_days.toFixed(1)}</p>
                            <p className="text-xs opacity-75 mt-1">days (SO → Release)</p>
                        </div>
                        <div className="bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
                            <Factory className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Production</p>
                            <p className="text-3xl font-bold">{mtoData.summary.avg_production_days.toFixed(1)}</p>
                            <p className="text-xs opacity-75 mt-1">days (Release → Finish)</p>
                        </div>
                        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
                            <Package className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Delivery</p>
                            <p className="text-3xl font-bold">{mtoData.summary.avg_delivery_days.toFixed(1)}</p>
                            <p className="text-xs opacity-75 mt-1">days (Finish → Billing)</p>
                        </div>
                        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
                            <Activity className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Total Cycle</p>
                            <p className="text-3xl font-bold">{mtoData.summary.avg_total_cycle_days.toFixed(1)}</p>
                            <p className="text-xs opacity-75 mt-1">days (end-to-end)</p>
                        </div>
                        <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
                            <CheckCircle className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Yield Rate</p>
                            <p className="text-3xl font-bold">{mtoData.summary.avg_yield_rate.toFixed(1)}%</p>
                            <p className="text-xs opacity-75 mt-1">quality metric</p>
                        </div>
                    </div>

                    {/* Timeline Breakdown Chart */}
                    <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
                        <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                            <BarChart3 className="w-6 h-6 text-indigo-600" />
                            MTO Timeline Breakdown
                        </h3>
                        <ResponsiveContainer width="100%" height={350}>
                            <BarChart data={mtoData.timeline_breakdown}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis dataKey="phase" stroke="#6b7280" />
                                <YAxis stroke="#6b7280" label={{ value: 'Days', angle: -90, position: 'insideLeft' }} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#fff',
                                        border: '2px solid #e5e7eb',
                                        borderRadius: '12px',
                                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                                    }}
                                />
                                <Bar dataKey="avg_days" radius={[8, 8, 0, 0]}>
                                    {mtoData.timeline_breakdown.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={[COLORS.info, COLORS.warning, COLORS.success][index]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Recent Orders Table */}
                    <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
                        <h3 className="text-2xl font-bold text-gray-900 mb-6">Recent MTO Orders</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                                    <tr>
                                        <th className="px-4 py-3 text-left font-semibold text-gray-700">Order ID</th>
                                        <th className="px-4 py-3 text-left font-semibold text-gray-700">Material</th>
                                        <th className="px-4 py-3 text-right font-semibold text-gray-700">Prep</th>
                                        <th className="px-4 py-3 text-right font-semibold text-gray-700">Production</th>
                                        <th className="px-4 py-3 text-right font-semibold text-gray-700">Delivery</th>
                                        <th className="px-4 py-3 text-right font-semibold text-gray-700">Total</th>
                                        <th className="px-4 py-3 text-right font-semibold text-gray-700">Yield</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {mtoData.orders.slice(0, 10).map((order) => (
                                        <tr key={order.order_id} className="hover:bg-gray-50 transition-colors">
                                            <td className="px-4 py-3 font-medium text-gray-900">{order.order_id}</td>
                                            <td className="px-4 py-3 text-gray-700 max-w-xs truncate">{order.material}</td>
                                            <td className="px-4 py-3 text-right text-blue-600 font-semibold">{order.prep_days}d</td>
                                            <td className="px-4 py-3 text-right text-amber-600 font-semibold">{order.production_days}d</td>
                                            <td className="px-4 py-3 text-right text-green-600 font-semibold">{order.delivery_days}d</td>
                                            <td className="px-4 py-3 text-right text-purple-600 font-bold">{order.total_cycle_days}d</td>
                                            <td className={`px-4 py-3 text-right font-bold ${order.yield_rate >= 98 ? 'text-green-600' : order.yield_rate >= 95 ? 'text-amber-600' : 'text-red-600'
                                                }`}>
                                                {order.yield_rate.toFixed(1)}%
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {/* MTS View */}
            {activeView === 'mts' && mtsData && (
                <div className="space-y-6 animate-fadeIn">
                    {/* KPI Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="bg-gradient-to-br from-teal-500 to-teal-600 rounded-xl p-6 text-white shadow-lg">
                            <Clock className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Planning Time</p>
                            <p className="text-3xl font-bold">{mtsData.summary.avg_planning_days.toFixed(1)}</p>
                            <p className="text-xs opacity-75 mt-1">days (Basic → Release)</p>
                        </div>
                        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
                            <Factory className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Production Time</p>
                            <p className="text-3xl font-bold">{mtsData.summary.avg_production_days.toFixed(1)}</p>
                            <p className="text-xs opacity-75 mt-1">days (Release → Finish)</p>
                        </div>
                        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
                            <Activity className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Total Lead Time</p>
                            <p className="text-3xl font-bold">{mtsData.summary.avg_total_lead_time.toFixed(1)}</p>
                            <p className="text-xs opacity-75 mt-1">days (end-to-end)</p>
                        </div>
                        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
                            <CheckCircle className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Yield Rate</p>
                            <p className="text-3xl font-bold">{mtsData.summary.avg_yield_rate.toFixed(1)}%</p>
                            <p className="text-xs opacity-75 mt-1">quality metric</p>
                        </div>
                    </div>

                    {/* MRP Performance Chart */}
                    <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
                        <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                            <BarChart3 className="w-6 h-6 text-green-600" />
                            MRP Controller Performance
                        </h3>
                        <ResponsiveContainer width="100%" height={350}>
                            <BarChart data={mtsData.mrp_performance}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis dataKey="mrp_controller" stroke="#6b7280" />
                                <YAxis stroke="#6b7280" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#fff',
                                        border: '2px solid #e5e7eb',
                                        borderRadius: '12px'
                                    }}
                                />
                                <Legend />
                                <Bar dataKey="avg_lead_time" fill={COLORS.info} name="Avg Lead Time (days)" radius={[8, 8, 0, 0]} />
                                <Bar dataKey="avg_yield" fill={COLORS.success} name="Avg Yield (%)" radius={[8, 8, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            {/* Variance View */}
            {activeView === 'variance' && varianceData && (
                <div className="space-y-6 animate-fadeIn">
                    {/* Summary Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
                            <CheckCircle className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Perfect Match</p>
                            <p className="text-3xl font-bold">{varianceData.summary.perfect_match}</p>
                            <p className="text-xs opacity-75 mt-1">{varianceData.summary.perfect_match_rate.toFixed(1)}% of total</p>
                        </div>
                        <div className="bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl p-6 text-white shadow-lg">
                            <TrendingUp className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Over Production</p>
                            <p className="text-3xl font-bold">{varianceData.summary.over_production}</p>
                            <p className="text-xs opacity-75 mt-1">exceeded target</p>
                        </div>
                        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white shadow-lg">
                            <AlertCircle className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Under Production</p>
                            <p className="text-3xl font-bold">{varianceData.summary.under_production}</p>
                            <p className="text-xs opacity-75 mt-1">below target</p>
                        </div>
                        <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl p-6 text-white shadow-lg">
                            <Activity className="w-8 h-8 mb-3 opacity-80" />
                            <p className="text-sm opacity-90 mb-1">Avg Variance</p>
                            <p className="text-3xl font-bold">{varianceData.summary.avg_variance_pct.toFixed(1)}%</p>
                            <p className="text-xs opacity-75 mt-1">absolute deviation</p>
                        </div>
                    </div>

                    {/* Variance Distribution */}
                    <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
                        <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                            <PieChart className="w-6 h-6 text-amber-600" />
                            Variance Distribution
                        </h3>
                        <ResponsiveContainer width="100%" height={350}>
                            <RePieChart>
                                <Pie
                                    data={varianceData.variance_distribution}
                                    dataKey="count"
                                    nameKey="category"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={120}
                                    label
                                >
                                    {varianceData.variance_distribution.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={[COLORS.success, COLORS.warning, COLORS.danger][index]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </RePieChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Variance Details Table */}
                    <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
                        <h3 className="text-2xl font-bold text-gray-900 mb-6">Top Variance Orders</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                                    <tr>
                                        <th className="px-4 py-3 text-left font-semibold text-gray-700">Order ID</th>
                                        <th className="px-4 py-3 text-left font-semibold text-gray-700">Type</th>
                                        <th className="px-4 py-3 text-left font-semibold text-gray-700">Material</th>
                                        <th className="px-4 py-3 text-right font-semibold text-gray-700">Order Qty</th>
                                        <th className="px-4 py-3 text-right font-semibold text-gray-700">Delivered</th>
                                        <th className="px-4 py-3 text-right font-semibold text-gray-700">Variance</th>
                                        <th className="px-4 py-3 text-center font-semibold text-gray-700">Status</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {varianceData.orders.slice(0, 15).map((order) => (
                                        <tr key={order.order_id} className="hover:bg-gray-50 transition-colors">
                                            <td className="px-4 py-3 font-medium text-gray-900">{order.order_id}</td>
                                            <td className="px-4 py-3">
                                                <span className={`px-2 py-1 text-xs font-semibold rounded ${order.order_type === '201O' ? 'bg-purple-100 text-purple-800' : 'bg-teal-100 text-teal-800'
                                                    }`}>
                                                    {order.order_type}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-gray-700 max-w-xs truncate">{order.material}</td>
                                            <td className="px-4 py-3 text-right text-gray-900">{order.order_qty.toLocaleString()}</td>
                                            <td className="px-4 py-3 text-right text-gray-900">{order.delivered_qty.toLocaleString()}</td>
                                            <td className={`px-4 py-3 text-right font-bold ${order.variance_pct > 0 ? 'text-amber-600' : order.variance_pct < 0 ? 'text-red-600' : 'text-green-600'
                                                }`}>
                                                {order.variance_pct > 0 ? '+' : ''}{order.variance_pct.toFixed(2)}%
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                {order.status === 'Perfect' ? (
                                                    <CheckCircle className="w-5 h-5 text-green-600 mx-auto" />
                                                ) : order.status === 'Over' ? (
                                                    <TrendingUp className="w-5 h-5 text-amber-600 mx-auto" />
                                                ) : (
                                                    <XCircle className="w-5 h-5 text-red-600 mx-auto" />
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ProductionInsights;
