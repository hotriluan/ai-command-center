/**
 * Production Insights Dashboard
 * 
 * Comprehensive production analytics dashboard featuring:
 * - Real-time KPI tracking (Lead Time, Yield Rate, Total Orders)
 * - Interactive charts for lead time breakdown and yield trends
 * - Table of problematic orders requiring attention
 * - Date range filtering
 * 
 * @module ProductionDashboard
 */

'use client';

import React, { useEffect, useState } from 'react';
import {
    fetchProductionAnalytics,
    fetchMrpPerformance,
    type ProductionAnalytics,
    type MrpPerformanceData,
    type ProductionOrder,
} from '../../services/productionService';
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    Cell,
} from 'recharts';
import { Calendar, TrendingUp, PackageCheck, AlertTriangle, Loader2 } from 'lucide-react';

// --- Interfaces ---

interface KPICardProps {
    title: string;
    value: string | number;
    subtitle?: string;
    trend?: number;
    color: 'blue' | 'green' | 'red' | 'yellow';
    icon: React.ReactNode;
}

/**
 * KPI Card Component
 */
const KPICard: React.FC<KPICardProps> = ({ title, value, subtitle, trend, color, icon }) => {
    const colorClasses = {
        blue: 'bg-blue-50 text-blue-600 border-blue-200',
        green: 'bg-green-50 text-green-600 border-green-200',
        red: 'bg-red-50 text-red-600 border-red-200',
        yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
                    <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
                    {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
                </div>
                <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
                    {icon}
                </div>
            </div>
        </div>
    );
};

/**
 * Loading Spinner Component
 */
const LoadingSpinner: React.FC = () => (
    <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Loading production data...</span>
    </div>
);

/**
 * Empty State Component
 */
const EmptyState: React.FC<{ message: string }> = ({ message }) => (
    <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <AlertTriangle className="w-12 h-12 mb-4 text-gray-400" />
        <p className="text-lg font-medium">{message}</p>
        <p className="text-sm mt-2">Try selecting a different date range</p>
    </div>
);

/**
 * Main Production Dashboard Component
 */
const ProductionDashboard: React.FC = () => {
    const [analytics, setAnalytics] = useState<ProductionAnalytics | null>(null);
    const [mrpPerformance, setMrpPerformance] = useState<MrpPerformanceData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    // Date Range State (default to current month)
    const [startDate, setStartDate] = useState<string>(() => {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
    });
    const [endDate, setEndDate] = useState<string>(() => {
        const now = new Date();
        const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        return `${lastDay.getFullYear()}-${String(lastDay.getMonth() + 1).padStart(2, '0')}-${String(lastDay.getDate()).padStart(2, '0')}`;
    });

    /**
     * Fetch production data from API
     */
    const fetchData = async () => {
        try {
            setLoading(true);
            setError(null);

            const [analyticsData, mrpData] = await Promise.all([
                fetchProductionAnalytics(startDate, endDate),
                fetchMrpPerformance(),
            ]);

            setAnalytics(analyticsData);
            setMrpPerformance(mrpData);
        } catch (err) {
            console.error('Error fetching production data:', err);
            setError(err instanceof Error ? err.message : 'Failed to load production data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [startDate, endDate]);

    /**
     * Get problematic orders (lowest yield or highest lead time)
     */
    const getProblematicOrders = (): ProductionOrder[] => {
        if (!analytics?.order_details || analytics.order_details.length === 0) {
            return [];
        }

        // Sort by yield rate (ascending) and lead time (descending)
        const sorted = [...analytics.order_details].sort((a, b) => {
            // Prioritize low yield
            if (a.yield_rate !== b.yield_rate) {
                return a.yield_rate - b.yield_rate;
            }
            // Then by high lead time
            return b.lead_time_production - a.lead_time_production;
        });

        return sorted.slice(0, 10);
    };

    /**
     * Format yield rate color
     */
    const getYieldColor = (yieldRate: number): string => {
        if (yieldRate >= 98) return 'text-green-600';
        if (yieldRate >= 95) return 'text-yellow-600';
        return 'text-red-600';
    };

    /**
     * Format yield status badge
     */
    const getYieldBadge = (status: string): React.ReactNode => {
        const badges = {
            Good: <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Good</span>,
            Warning: <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">Warning</span>,
            Critical: <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">Critical</span>,
        };
        return badges[status as keyof typeof badges] || badges.Good;
    };

    // Render loading state
    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 p-8">
                <div className="max-w-7xl mx-auto">
                    <h1 className="text-3xl font-bold text-gray-900 mb-8">Production Insights</h1>
                    <LoadingSpinner />
                </div>
            </div>
        );
    }

    // Render error state
    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 p-8">
                <div className="max-w-7xl mx-auto">
                    <h1 className="text-3xl font-bold text-gray-900 mb-8">Production Insights</h1>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                        <p className="text-red-800 font-medium">Error: {error}</p>
                        <button
                            onClick={fetchData}
                            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                        >
                            Retry
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    const problematicOrders = getProblematicOrders();
    const hasData = analytics && analytics.summary.total_orders > 0;

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header with Date Range Picker */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">Production Insights</h1>
                    
                    {/* Date Range Picker */}
                    <div className="flex items-center gap-4 bg-white p-4 rounded-lg shadow-md">
                        <Calendar className="w-5 h-5 text-gray-600" />
                        <div className="flex items-center gap-2">
                            <label className="text-sm font-medium text-gray-700">From:</label>
                            <input
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <label className="text-sm font-medium text-gray-700">To:</label>
                            <input
                                type="date"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <button
                            onClick={fetchData}
                            className="ml-auto px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
                        >
                            Apply Filter
                        </button>
                    </div>
                </div>

                {!hasData ? (
                    <EmptyState message="No data found for this period" />
                ) : (
                    <>
                        {/* Section A: KPI Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                            <KPICard
                                title="Average Lead Time"
                                value={`${analytics.summary.avg_lead_time.toFixed(1)} Days`}
                                subtitle="Production cycle time"
                                color="blue"
                                icon={<TrendingUp className="w-6 h-6" />}
                            />
                            <KPICard
                                title="Yield Rate"
                                value={`${analytics.summary.avg_yield_rate.toFixed(2)}%`}
                                subtitle={analytics.summary.avg_yield_rate >= 98 ? 'Excellent' : analytics.summary.avg_yield_rate >= 95 ? 'Good' : 'Needs Attention'}
                                color={analytics.summary.avg_yield_rate >= 98 ? 'green' : analytics.summary.avg_yield_rate >= 95 ? 'yellow' : 'red'}
                                icon={<PackageCheck className="w-6 h-6" />}
                            />
                            <KPICard
                                title="Total Orders"
                                value={analytics.summary.total_orders.toLocaleString()}
                                subtitle="In selected period"
                                color="blue"
                                icon={<Calendar className="w-6 h-6" />}
                            />
                        </div>

                        {/* Section B: Charts */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                            {/* Lead Time Trend Chart */}
                            <div className="bg-white rounded-lg shadow-md p-6">
                                <h3 className="text-xl font-bold text-gray-900 mb-4">Lead Time Trend</h3>
                                {analytics.monthly_trends.length > 0 ? (
                                    <ResponsiveContainer width="100%" height={300}>
                                        <BarChart data={analytics.monthly_trends}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                            <XAxis
                                                dataKey="month_name"
                                                stroke="#6b7280"
                                                style={{ fontSize: '12px' }}
                                            />
                                            <YAxis
                                                stroke="#6b7280"
                                                style={{ fontSize: '12px' }}
                                                label={{ value: 'Days', angle: -90, position: 'insideLeft' }}
                                            />
                                            <Tooltip
                                                contentStyle={{
                                                    backgroundColor: '#fff',
                                                    border: '1px solid #e5e7eb',
                                                    borderRadius: '8px',
                                                }}
                                            />
                                            <Legend />
                                            <Bar dataKey="avg_lead_time" fill="#3b82f6" name="Avg Lead Time (Days)" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <EmptyState message="No trend data available" />
                                )}
                            </div>

                            {/* Yield Trend Chart */}
                            <div className="bg-white rounded-lg shadow-md p-6">
                                <h3 className="text-xl font-bold text-gray-900 mb-4">Yield Trend</h3>
                                {analytics.monthly_trends.length > 0 ? (
                                    <ResponsiveContainer width="100%" height={300}>
                                        <LineChart data={analytics.monthly_trends}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                            <XAxis
                                                dataKey="month_name"
                                                stroke="#6b7280"
                                                style={{ fontSize: '12px' }}
                                            />
                                            <YAxis
                                                stroke="#6b7280"
                                                style={{ fontSize: '12px' }}
                                                domain={[90, 100]}
                                                label={{ value: 'Yield %', angle: -90, position: 'insideLeft' }}
                                            />
                                            <Tooltip
                                                formatter={(value: number) => `${value.toFixed(2)}%`}
                                                contentStyle={{
                                                    backgroundColor: '#fff',
                                                    border: '1px solid #e5e7eb',
                                                    borderRadius: '8px',
                                                }}
                                            />
                                            <Legend />
                                            <Line
                                                type="monotone"
                                                dataKey="avg_yield_rate"
                                                stroke="#10b981"
                                                strokeWidth={2}
                                                name="Avg Yield Rate (%)"
                                                dot={{ r: 4 }}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <EmptyState message="No trend data available" />
                                )}
                            </div>
                        </div>

                        {/* Section C: Problematic Orders Table */}
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5 text-yellow-600" />
                                Orders Requiring Attention
                            </h3>
                            {problematicOrders.length > 0 ? (
                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Order #
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Material
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Type
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Lead Time
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Yield Rate
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Status
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {problematicOrders.map((order) => (
                                                <tr key={order.order_id} className="hover:bg-gray-50">
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                        {order.order_id}
                                                    </td>
                                                    <td className="px-6 py-4 text-sm text-gray-600">
                                                        <div className="max-w-xs truncate" title={order.material_description}>
                                                            {order.material_description}
                                                        </div>
                                                        <div className="text-xs text-gray-400">{order.material_code}</div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                                        <span className="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                                                            {order.order_type}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                                        {order.lead_time_production.toFixed(1)} days
                                                    </td>
                                                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getYieldColor(order.yield_rate)}`}>
                                                        {order.yield_rate.toFixed(2)}%
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                                        {getYieldBadge(order.yield_status)}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <EmptyState message="No problematic orders found" />
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default ProductionDashboard;
