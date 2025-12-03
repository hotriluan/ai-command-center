/**
 * AI Command Center - Executive Dashboard
 * 
 * A comprehensive business intelligence dashboard featuring:
 * - Real-time KPI tracking with trend indicators
 * - Interactive charts for revenue, profit, and performance metrics
 * - AI-powered analytics chatbot
 * - Full number display with semantic color coding
 * 
 * @module ExecutiveDashboard
 * @author AI Command Center Team
 * @version 2.0.0
 */

'use client';

import React, { useEffect, useState, useRef } from 'react';
import { DollarSign, TrendingUp, Target, Percent, Upload, Loader2, BarChart3, PieChart, Users, ShoppingBag } from 'lucide-react';
import ChatWidget from '../components/ChatWidget';
import KPICard from '../components/KPICard';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RePieChart, Pie, Cell, Legend } from 'recharts';
import { formatVND, formatCompactVND, getGrowthData } from '../utils/format';

// --- Interfaces matching Backend Structure ---

/**
 * Key Performance Indicator data structure
 */
interface KPIData {
    revenue: number;
    revenue_growth: number;
    profit: number;
    profit_growth: number;
    marketing: number;
    margin: number;
}

/**
 * Chart data point structure for various visualizations
 */
interface ChartDataPoint {
    name: string;
    value?: number;
    revenue?: number;
    profit?: number;
    [key: string]: any;
}

/**
 * Complete dashboard charts collection
 */
interface DashboardCharts {
    monthly_trend: ChartDataPoint[];
    channel_distribution: ChartDataPoint[];
    branch_distribution: ChartDataPoint[];
    top_products: ChartDataPoint[];
    top_salesmen: ChartDataPoint[];
}

/**
 * Main dashboard data structure
 */
interface DashboardData {
    kpi: KPIData;
    charts: DashboardCharts;
}

/**
 * Semantic color palette for consistent branding
 * - Revenue: Green (positive income)
 * - Profit: Blue (business profit)
 * - Marketing: Red/Pink (expense indicator)
 * - Products: Amber
 * - Salesmen: Purple
 */
const CHART_COLORS = {
    revenue: '#10b981',
    profit: '#3b82f6',
    marketing: '#f43f5e',
    products: '#f59e0b',
    salesmen: '#8b5cf6',
    channels: ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']
};

/**
 * Executive Dashboard 2.0 - Main Component
 * 
 * Features:
 * - Full number display (no truncation)
 * - Trend indicators with semantic colors
 * - Real-time data fetching
 * - Responsive design
 * - Premium UI/UX
 */
const Page: React.FC = () => {
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [isUploading, setIsUploading] = useState<boolean>(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    /**
     * Fetches dashboard data from backend API
     */
    const fetchData = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:8000/api/dashboard');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const result = await response.json();
            setData(result);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch data');
            console.error('Error fetching dashboard data:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    /**
     * Handles Excel file upload for data import
     */
    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/api/upload', { method: 'POST', body: formData });
            if (!response.ok) throw new Error('Upload failed');
            await fetchData();
            alert('Data loaded successfully!');
        } catch (err) {
            console.error('Error uploading file:', err);
            alert('Failed to upload data.');
        } finally {
            setIsUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    // Loading State
    if (loading && !data) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-200 border-t-indigo-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 font-medium">Loading Executive Dashboard...</p>
                </div>
            </div>
        );
    }

    // Error State
    if (error && !data) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
                    <h3 className="text-red-800 font-semibold mb-2">Connection Error</h3>
                    <p className="text-red-600">{error}</p>
                </div>
            </div>
        );
    }

    // Safe data access with defaults
    const kpi = data?.kpi || { revenue: 0, revenue_growth: 0, profit: 0, profit_growth: 0, marketing: 0, margin: 0 };
    const charts = data?.charts || { monthly_trend: [], channel_distribution: [], branch_distribution: [], top_products: [], top_salesmen: [] };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 font-sans text-gray-900">
            <div className="container mx-auto px-6 py-8 max-w-7xl">
                {/* Header */}
                <header className="mb-10 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div>
                        <h1 className="text-4xl font-bold text-gray-900 tracking-tight bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                            Executive Dashboard 2.0
                        </h1>
                        <p className="text-gray-600 mt-2 font-medium">Real-time business intelligence with full transparency</p>
                    </div>
                    <div>
                        <input type="file" accept=".xlsx, .xls" ref={fileInputRef} onChange={handleFileUpload} className="hidden" />
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            disabled={isUploading}
                            className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg shadow-md hover:shadow-lg transition-all text-sm font-semibold disabled:opacity-70 disabled:cursor-not-allowed"
                            aria-label="Upload Excel data file"
                        >
                            {isUploading ? <Loader2 size={18} className="animate-spin" /> : <Upload size={18} />}
                            {isUploading ? 'Processing Data...' : 'Upload Excel Data'}
                        </button>
                    </div>
                </header>

                {/* KPI Cards - Executive Dashboard 2.0 */}
                <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8" aria-label="Key Performance Indicators">
                    <KPICard
                        title="Total Revenue"
                        value={formatVND(kpi.revenue)}
                        growth={getGrowthData(kpi.revenue_growth)}
                        icon={DollarSign}
                        iconColor="text-emerald-500"
                        valueColor="text-emerald-600"
                    />
                    <KPICard
                        title="Gross Profit"
                        value={formatVND(kpi.profit)}
                        growth={getGrowthData(kpi.profit_growth)}
                        icon={TrendingUp}
                        iconColor="text-blue-500"
                        valueColor="text-blue-600"
                    />
                    <KPICard
                        title="Marketing Spend"
                        value={formatVND(kpi.marketing)}
                        icon={Target}
                        iconColor="text-rose-500"
                        valueColor="text-rose-600"
                    />
                    <KPICard
                        title="Profit Margin"
                        value={`${kpi.margin.toFixed(1)}%`}
                        icon={Percent}
                        iconColor="text-amber-500"
                        valueColor="text-amber-600"
                    />
                </section>

                {/* Main Charts Row */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                    {/* Monthly Trend Chart */}
                    <section className="lg:col-span-2 bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow" aria-label="Monthly Revenue and Profit Trend">
                        <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-gray-800">
                            <BarChart3 size={22} className="text-indigo-500" />
                            Monthly Revenue & Profit Trend
                        </h3>
                        <div className="h-80" role="img" aria-label="Bar chart showing monthly revenue and profit trends">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={charts.monthly_trend} margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                                    <XAxis
                                        dataKey="name"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#6b7280', fontSize: 12, fontWeight: 500 }}
                                        dy={10}
                                    />
                                    <YAxis
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#6b7280', fontSize: 12 }}
                                        tickFormatter={formatCompactVND}
                                        width={70}
                                    />
                                    <Tooltip
                                        formatter={(value: number) => formatVND(value)}
                                        contentStyle={{
                                            borderRadius: '12px',
                                            border: 'none',
                                            boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                                            padding: '12px'
                                        }}
                                        labelStyle={{ fontWeight: 600, marginBottom: '4px' }}
                                    />
                                    <Legend
                                        wrapperStyle={{ paddingTop: '20px' }}
                                        iconType="circle"
                                    />
                                    <Bar
                                        dataKey="revenue"
                                        name="Revenue"
                                        fill={CHART_COLORS.revenue}
                                        radius={[6, 6, 0, 0]}
                                        barSize={32}
                                    />
                                    <Bar
                                        dataKey="profit"
                                        name="Profit"
                                        fill={CHART_COLORS.profit}
                                        radius={[6, 6, 0, 0]}
                                        barSize={32}
                                    />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </section>

                    {/* Channel Distribution Pie Chart */}
                    <section className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow" aria-label="Revenue by Channel Distribution">
                        <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-gray-800">
                            <PieChart size={22} className="text-indigo-500" />
                            Revenue by Channel
                        </h3>
                        <div className="h-80" role="img" aria-label="Pie chart showing revenue distribution by channel">
                            <ResponsiveContainer width="100%" height="100%">
                                <RePieChart>
                                    <Pie
                                        data={charts.channel_distribution}
                                        cx="45%"
                                        cy="50%"
                                        innerRadius={65}
                                        outerRadius={85}
                                        paddingAngle={4}
                                        dataKey="value"
                                    >
                                        {charts.channel_distribution.map((entry, index) => (
                                            <Cell
                                                key={`cell-${index}`}
                                                fill={CHART_COLORS.channels[index % CHART_COLORS.channels.length]}
                                            />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        formatter={(value: number) => formatVND(value)}
                                        contentStyle={{
                                            borderRadius: '12px',
                                            border: 'none',
                                            boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                                            padding: '12px'
                                        }}
                                    />
                                    <Legend
                                        layout="vertical"
                                        verticalAlign="middle"
                                        align="right"
                                        wrapperStyle={{ fontSize: '12px', fontWeight: 500 }}
                                    />
                                </RePieChart>
                            </ResponsiveContainer>
                        </div>
                    </section>
                </div>

                {/* Secondary Charts Row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Top Products Chart */}
                    <section className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow" aria-label="Top 5 Best-Selling Products">
                        <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-gray-800">
                            <ShoppingBag size={22} className="text-amber-500" />
                            Top 5 Best-Selling Products
                        </h3>
                        <div className="h-64" role="img" aria-label="Horizontal bar chart showing top 5 products by revenue">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={charts.top_products} layout="vertical" margin={{ left: 40, right: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e5e7eb" />
                                    <XAxis type="number" hide />
                                    <YAxis
                                        dataKey="name"
                                        type="category"
                                        width={150}
                                        tick={{ fontSize: 11, fontWeight: 500 }}
                                    />
                                    <Tooltip
                                        formatter={(value: number) => formatVND(value)}
                                        contentStyle={{
                                            borderRadius: '12px',
                                            border: 'none',
                                            boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                                            padding: '12px'
                                        }}
                                    />
                                    <Bar
                                        dataKey="value"
                                        fill={CHART_COLORS.products}
                                        radius={[0, 6, 6, 0]}
                                        barSize={22}
                                    />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </section>

                    {/* Top Salesmen Chart */}
                    <section className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow" aria-label="Top 5 Salesmen by Performance">
                        <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-gray-800">
                            <Users size={22} className="text-purple-500" />
                            Top 5 Salesmen
                        </h3>
                        <div className="h-64" role="img" aria-label="Horizontal bar chart showing top 5 salesmen by revenue">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={charts.top_salesmen} layout="vertical" margin={{ left: 40, right: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e5e7eb" />
                                    <XAxis type="number" hide />
                                    <YAxis
                                        dataKey="name"
                                        type="category"
                                        width={150}
                                        tick={{ fontSize: 11, fontWeight: 500 }}
                                    />
                                    <Tooltip
                                        formatter={(value: number) => formatVND(value)}
                                        contentStyle={{
                                            borderRadius: '12px',
                                            border: 'none',
                                            boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                                            padding: '12px'
                                        }}
                                    />
                                    <Bar
                                        dataKey="value"
                                        fill={CHART_COLORS.salesmen}
                                        radius={[0, 6, 6, 0]}
                                        barSize={22}
                                    />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </section>
                </div>
            </div>

            {/* AI Chat Widget */}
            <ChatWidget />
        </div>
    );
};

export default Page;