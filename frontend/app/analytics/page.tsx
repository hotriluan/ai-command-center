/**
 * Advanced Analytics Page
 * Features: Product Matrix, Sales Leaderboard, Seasonality, Channel Analysis, Credit Control
 * FULLY INTEGRATED: All tabs working with complete Channel Analysis
 */

'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, Target, Calendar, BarChart3 } from 'lucide-react';
import {
    ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell,
    BarChart, Bar, ReferenceLine, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import YearSelector from '../../components/YearSelector';
import ChatWidget from '../../components/ChatWidget';

// ============= INTERFACES =============

interface ProductMatrixData {
    name: string;
    revenue: number;
    margin: number;
    quantity: number;
    profit: number;
}

interface LeaderboardData {
    name: string;
    actual: number;
    target: number;
    achievement_rate: number;
    status: 'success' | 'warning' | 'danger';
}

interface SeasonalityData {
    year: number;
    month: number;
    revenue: number;
}

interface DebtKPIs {
    total_outstanding: number;
    total_collected: number;
    bad_debt: number;
    collection_rate: number;
}

interface DebtOverview {
    status: string;
    report_date: string;
    kpis: DebtKPIs;
    channel_breakdown: Array<{
        channel: string;
        outstanding: number;
        collected: number;
    }>;
    aging_breakdown: {
        [key: string]: number;
    };
}

interface TopDebtor {
    customer_name: string;
    customer_code: string;
    channel: string;
    total_debt: number;
    overdue: number;
}

// Channel Analysis interfaces
interface ChannelOverview {
    channel: string;
    revenue: number;
    profit: number;
    margin: number;
    deals: number;
}

interface ChannelRadarData {
    channel: string;
    Revenue: number;
    Profit: number;
    Volume: number;
    Margin: number;
}

interface ChannelMonthlyTrend {
    month: number;
    Industry: number;
    Retail: number;
    Project: number;
}

interface ChannelData {
    overview: ChannelOverview[];
    monthly_trend: ChannelMonthlyTrend[];
    radar_data: ChannelRadarData[];
}

const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const AnalyticsPage: React.FC = () => {
    // State management
    const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
    const [selectedSemester, setSelectedSemester] = useState<number | null>(null);
    const [productMatrix, setProductMatrix] = useState<ProductMatrixData[]>([]);
    const [leaderboard, setLeaderboard] = useState<LeaderboardData[]>([]);
    const [seasonality, setSeasonality] = useState<SeasonalityData[]>([]);
    const [loading, setLoading] = useState(true);

    // Tab state
    const [activeTab, setActiveTab] = useState<'products' | 'leaderboard' | 'seasonality' | 'channel' | 'credit'>('products');

    // Credit Control state
    const [debtData, setDebtData] = useState<DebtOverview | null>(null);
    const [topDebtors, setTopDebtors] = useState<TopDebtor[]>([]);
    const [debtLoading, setDebtLoading] = useState(false);
    const [selectedDebtDate, setSelectedDebtDate] = useState<string | null>(null);

    // Channel Analysis state
    const [channelData, setChannelData] = useState<ChannelData | null>(null);
    const [channelLoading, setChannelLoading] = useState(false);

    // ============= DATA FETCHING =============

    // Fetch analytics data (Product, Leaderboard, Seasonality)
    const fetchAnalytics = async () => {
        setLoading(true);
        try {
            const semesterParam = selectedSemester !== null ? `&semester=${selectedSemester}` : '';
            const [matrixRes, waterfallRes, seasonalityRes] = await Promise.all([
                fetch(`http://localhost:8000/api/analytics/product-matrix?year=${selectedYear}${semesterParam}`),
                fetch(`http://localhost:8000/api/analytics/target-waterfall?year=${selectedYear}${semesterParam}`),
                fetch(`http://localhost:8000/api/analytics/seasonality?year=${selectedYear}${semesterParam}`)
            ]);

            const [matrixData, waterfallData, seasonalityData] = await Promise.all([
                matrixRes.json(),
                waterfallRes.json(),
                seasonalityRes.json()
            ]);

            setProductMatrix(matrixData.data || []);
            setLeaderboard(waterfallData.data || []);
            setSeasonality(seasonalityData.data || []);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    // Fetch debt data for Credit Control tab
    const fetchDebtData = async (date?: string) => {
        setDebtLoading(true);
        try {
            const dateParam = date ? `?report_date=${date}` : '';
            const [overviewRes, debtorsRes] = await Promise.all([
                fetch(`http://localhost:8000/api/debt/overview${dateParam}`),
                fetch(`http://localhost:8000/api/debt/top-customers${dateParam}`)
            ]);

            const [overviewData, debtorsData] = await Promise.all([
                overviewRes.json(),
                debtorsRes.json()
            ]);

            if (overviewData.status === 'success') {
                setDebtData(overviewData);
                if (!selectedDebtDate && overviewData.report_date) {
                    setSelectedDebtDate(overviewData.report_date);
                }
            }

            setTopDebtors(debtorsData.data || []);
        } catch (error) {
            console.error('Error fetching debt data:', error);
        } finally {
            setDebtLoading(false);
        }
    };

    // Fetch channel performance data
    const fetchChannelData = async () => {
        setChannelLoading(true);
        try {
            const semesterParam = selectedSemester !== null ? `&semester=${selectedSemester}` : '';
            const response = await fetch(`http://localhost:8000/api/analytics/channel-performance?year=${selectedYear}${semesterParam}`);
            const data = await response.json();

            if (data.status === 'success') {
                setChannelData(data.data);
            }
        } catch (error) {
            console.error('Error fetching channel data:', error);
        } finally {
            setChannelLoading(false);
        }
    };

    // Effects
    useEffect(() => {
        fetchAnalytics();
    }, [selectedYear, selectedSemester]);

    useEffect(() => {
        if (activeTab === 'credit') {
            fetchDebtData(selectedDebtDate || undefined);
        }
    }, [activeTab, selectedDebtDate]);

    useEffect(() => {
        if (activeTab === 'channel') {
            fetchChannelData();
        }
    }, [activeTab, selectedYear, selectedSemester]);

    // Calculate averages for reference lines
    const avgRevenue = productMatrix.length > 0
        ? productMatrix.reduce((sum, p) => sum + p.revenue, 0) / productMatrix.length
        : 0;
    const avgMargin = productMatrix.length > 0
        ? productMatrix.reduce((sum, p) => sum + p.margin, 0) / productMatrix.length
        : 0;

    // ============= CUSTOM TOOLTIPS =============

    const LeaderboardTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            const gap = data.actual - data.target;
            return (
                <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
                    <p className="font-bold text-gray-900 mb-2">{data.name}</p>
                    <p className="text-sm text-gray-600">Revenue: {(data.actual / 1e9).toFixed(2)}B VND</p>
                    <p className="text-sm text-gray-600">Target: {(data.target / 1e9).toFixed(2)}B VND</p>
                    <p className={`text-sm font-semibold ${gap >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        Gap: {gap >= 0 ? '+' : ''}{(gap / 1e9).toFixed(2)}B VND
                    </p>
                    <p className="text-sm font-bold text-indigo-600 mt-1">
                        Achievement: {data.achievement_rate.toFixed(1)}%
                    </p>
                </div>
            );
        }
        return null;
    };

    const BubbleTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
                    <p className="font-bold text-gray-900 mb-2">{data.name}</p>
                    <p className="text-sm text-gray-600">Revenue: {(data.revenue / 1e9).toFixed(2)}B VND</p>
                    <p className="text-sm text-gray-600">Margin: {data.margin.toFixed(1)}%</p>
                    <p className="text-sm text-gray-600">Quantity: {data.quantity.toLocaleString()}</p>
                </div>
            );
        }
        return null;
    };

    // ============= LOADING STATE =============

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-200 border-t-indigo-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 font-medium">Loading Advanced Analytics...</p>
                </div>
            </div>
        );
    }

    // ============= MAIN RENDER =============

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
            <div className="container mx-auto px-6 py-8 max-w-7xl">
                {/* Header */}
                <header className="mb-8">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h1 className="text-4xl font-bold text-gray-900 tracking-tight bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                                Advanced Business Analytics
                            </h1>
                            <p className="text-gray-600 mt-2 font-medium">Deep insights into product performance, channels, targets, and trends</p>
                        </div>
                        <div className="flex gap-3">
                            <YearSelector selectedYear={selectedYear} onYearChange={setSelectedYear} />
                            <div className="bg-white rounded-lg shadow-md border border-gray-200 px-4 py-2">
                                <label className="text-xs text-gray-600 font-medium block mb-1">Semester</label>
                                <select
                                    value={selectedSemester === null ? '' : selectedSemester}
                                    onChange={(e) => setSelectedSemester(e.target.value === '' ? null : parseInt(e.target.value))}
                                    className="text-sm font-semibold text-gray-900 bg-transparent border-none focus:outline-none cursor-pointer"
                                >
                                    <option value="">Whole Year</option>
                                    <option value="1">Semester 1</option>
                                    <option value="2">Semester 2</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <a href="/" className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800 font-medium transition-colors">
                        ← Back to Dashboard
                    </a>
                </header>

                {/* Tab Navigation */}
                <div className="flex gap-2 mb-6 flex-wrap">
                    <button
                        onClick={() => setActiveTab('products')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'products' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
                            }`}
                    >
                        Product Matrix
                    </button>
                    <button
                        onClick={() => setActiveTab('leaderboard')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'leaderboard' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
                            }`}
                    >
                        Sales Leaderboard
                    </button>
                    <button
                        onClick={() => setActiveTab('seasonality')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'seasonality' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
                            }`}
                    >
                        Seasonality
                    </button>
                    <button
                        onClick={() => setActiveTab('channel')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'channel' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
                            }`}
                    >
                        Channel Analysis
                    </button>
                    <button
                        onClick={() => setActiveTab('credit')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'credit' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
                            }`}
                    >
                        Credit Control
                    </button>
                </div>

                {/* Product Portfolio Matrix Tab */}
                {activeTab === 'products' && (
                    <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-gray-200">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="bg-indigo-100 p-3 rounded-lg">
                                <TrendingUp className="w-6 h-6 text-indigo-600" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900">Product Portfolio Matrix</h2>
                                <p className="text-sm text-gray-600">Top 50 Products: Revenue vs Profit Margin (bubble size = quantity)</p>
                            </div>
                        </div>
                        <ResponsiveContainer width="100%" height={500}>
                            <ScatterChart margin={{ top: 20, right: 30, bottom: 60, left: 60 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    type="number"
                                    dataKey="revenue"
                                    name="Revenue"
                                    label={{ value: 'Revenue (VND)', position: 'insideBottom', offset: -10 }}
                                    tickFormatter={(value) => `${(value / 1e9).toFixed(1)}B`}
                                />
                                <YAxis
                                    type="number"
                                    dataKey="margin"
                                    name="Margin"
                                    label={{ value: 'Profit Margin (%)', angle: -90, position: 'insideLeft' }}
                                />
                                <ReferenceLine x={avgRevenue} stroke="#94a3b8" strokeDasharray="5 5" label="Avg Revenue" />
                                <ReferenceLine y={avgMargin} stroke="#94a3b8" strokeDasharray="5 5" label="Avg Margin" />
                                <Tooltip content={<BubbleTooltip />} />
                                <Legend />
                                <Scatter name="Products" data={productMatrix} fill="#8884d8">
                                    {productMatrix.map((entry, index) => (
                                        <Cell
                                            key={`cell-${index}`}
                                            fill={entry.margin > 20 ? '#10b981' : entry.margin > 10 ? '#f59e0b' : '#ef4444'}
                                        />
                                    ))}
                                </Scatter>
                            </ScatterChart>
                        </ResponsiveContainer>
                        <div className="mt-4 flex gap-4 text-sm">
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                                <span>High Margin (&gt;20%)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 bg-amber-500 rounded-full"></div>
                                <span>Medium Margin (10-20%)</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                                <span>Low Margin (&lt;10%) - Revenue Trap</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Sales Leaderboard Tab */}
                {activeTab === 'leaderboard' && (
                    <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-gray-200">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="bg-green-100 p-3 rounded-lg">
                                <Target className="w-6 h-6 text-green-600" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900">Sales Leaderboard</h2>
                                <p className="text-sm text-gray-600">Ranking by % Achievement (Best to Worst)</p>
                            </div>
                        </div>
                        {leaderboard.length > 0 ? (
                            <ResponsiveContainer width="100%" height={Math.max(400, leaderboard.length * 50)}>
                                <BarChart data={leaderboard} layout="vertical" margin={{ top: 20, right: 80, left: 120, bottom: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis type="number" label={{ value: 'Achievement %', position: 'insideBottom', offset: -10 }} />
                                    <YAxis type="category" dataKey="name" width={110} />
                                    <Tooltip content={<LeaderboardTooltip />} />
                                    <Legend />
                                    <Bar dataKey="achievement_rate" name="Achievement %" radius={[0, 8, 8, 0]}>
                                        {leaderboard.map((entry, index) => (
                                            <Cell
                                                key={`cell-${index}`}
                                                fill={entry.status === 'success' ? '#10b981' : entry.status === 'warning' ? '#f59e0b' : '#ef4444'}
                                            />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <p className="text-center text-gray-500 py-8">No leaderboard data available</p>
                        )}
                    </div>
                )}

                {/* Seasonality Tab */}
                {activeTab === 'seasonality' && (
                    <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-gray-200">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="bg-purple-100 p-3 rounded-lg">
                                <Calendar className="w-6 h-6 text-purple-600" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900">Revenue Seasonality</h2>
                                <p className="text-sm text-gray-600">Monthly revenue patterns across years</p>
                            </div>
                        </div>
                        {seasonality.length > 0 ? (
                            <ResponsiveContainer width="100%" height={400}>
                                <BarChart data={seasonality} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis
                                        dataKey="month"
                                        tickFormatter={(month) => MONTH_NAMES[month - 1]}
                                    />
                                    <YAxis tickFormatter={(value) => `${(value / 1e9).toFixed(1)}B`} />
                                    <Tooltip
                                        formatter={(value: number) => `${(value / 1e9).toFixed(2)}B VND`}
                                        labelFormatter={(month) => MONTH_NAMES[month - 1]}
                                    />
                                    <Legend />
                                    <Bar dataKey="revenue" fill="#8b5cf6" name="Revenue" radius={[8, 8, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <p className="text-center text-gray-500 py-8">No seasonality data available</p>
                        )}
                    </div>
                )}

                {/* Channel Analysis Tab - NEW */}
                {activeTab === 'channel' && (
                    <div>
                        {channelLoading ? (
                            <div className="h-64 flex items-center justify-center">
                                <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-200 border-t-indigo-600"></div>
                            </div>
                        ) : channelData ? (
                            <>
                                {/* Row 1: Channel Overview Cards */}
                                <div className="grid grid-cols-3 gap-6 mb-6">
                                    {channelData.overview
                                        .slice()
                                        .sort((a, b) => {
                                            const order = ['Industry', 'Retail', 'Project'];
                                            return order.indexOf(a.channel) - order.indexOf(b.channel);
                                        })
                                        .map((channel) => (
                                            <div key={channel.channel} className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-indigo-500">
                                                <h3 className="text-lg font-semibold text-gray-700 mb-3">{channel.channel}</h3>
                                                <div className="space-y-2">
                                                    <div>
                                                        <p className="text-sm text-gray-600">Revenue</p>
                                                        <p className="text-2xl font-bold text-gray-900">{(channel.revenue / 1e9).toFixed(2)}B</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-sm text-gray-600">Profit Margin</p>
                                                        <p className="text-xl font-semibold text-indigo-600">{channel.margin.toFixed(1)}%</p>
                                                    </div>
                                                    <div className="text-xs text-gray-500">
                                                        {channel.deals.toLocaleString()} deals
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                </div>

                                {/* Row 2: Visualizations */}
                                <div className="grid grid-cols-2 gap-6 mb-6">
                                    {/* Radar Chart */}
                                    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                                        <h3 className="text-xl font-bold text-gray-900 mb-4">Channel Performance Radar</h3>
                                        <p className="text-sm text-gray-600 mb-4">Normalized comparison across metrics (0-100 scale)</p>
                                        <ResponsiveContainer width="100%" height={350}>
                                            <RadarChart data={channelData.radar_data}>
                                                <PolarGrid />
                                                <PolarAngleAxis dataKey="channel" />
                                                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                                                <Radar name="Revenue" dataKey="Revenue" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                                                <Radar name="Profit" dataKey="Profit" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                                                <Radar name="Volume" dataKey="Volume" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.3} />
                                                <Legend />
                                                <Tooltip />
                                            </RadarChart>
                                        </ResponsiveContainer>
                                    </div>

                                    {/* Stacked Bar Chart */}
                                    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                                        <h3 className="text-xl font-bold text-gray-900 mb-4">Monthly Revenue Trend</h3>
                                        <p className="text-sm text-gray-600 mb-4">Revenue contribution by channel over time</p>
                                        <ResponsiveContainer width="100%" height={350}>
                                            <BarChart data={channelData.monthly_trend} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis
                                                    dataKey="month"
                                                    tickFormatter={(month) => MONTH_NAMES[month - 1]}
                                                />
                                                <YAxis tickFormatter={(value) => `${(value / 1e9).toFixed(1)}B`} />
                                                <Tooltip
                                                    formatter={(value: number) => `${(value / 1e9).toFixed(2)}B VND`}
                                                    labelFormatter={(month) => MONTH_NAMES[month - 1]}
                                                />
                                                <Legend />
                                                <Bar dataKey="Industry" stackId="a" fill="#3b82f6" />
                                                <Bar dataKey="Retail" stackId="a" fill="#10b981" />
                                                <Bar dataKey="Project" stackId="a" fill="#8b5cf6" />
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>

                                {/* Row 3: Profitability Table */}
                                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                                    <h3 className="text-xl font-bold text-gray-900 mb-4">Profitability Comparison</h3>
                                    <div className="overflow-auto">
                                        <table className="w-full text-sm">
                                            <thead className="bg-gray-50">
                                                <tr>
                                                    <th className="px-4 py-3 text-left font-semibold text-gray-700">Channel</th>
                                                    <th className="px-4 py-3 text-right font-semibold text-gray-700">Revenue</th>
                                                    <th className="px-4 py-3 text-right font-semibold text-gray-700">Profit</th>
                                                    <th className="px-4 py-3 text-right font-semibold text-gray-700">Margin %</th>
                                                    <th className="px-4 py-3 text-right font-semibold text-gray-700">Deals</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {channelData.overview
                                                    .slice()
                                                    .sort((a, b) => {
                                                        const order = ['Industry', 'Retail', 'Project'];
                                                        return order.indexOf(a.channel) - order.indexOf(b.channel);
                                                    })
                                                    .map((channel) => {
                                                        const formatter = new Intl.NumberFormat('vi-VN', { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 0 });
                                                        return (
                                                            <tr key={channel.channel} className="border-t border-gray-200 hover:bg-gray-50">
                                                                <td className="px-4 py-3 font-medium text-gray-900">{channel.channel}</td>
                                                                <td className="px-4 py-3 text-right text-gray-900">{formatter.format(channel.revenue)}</td>
                                                                <td className="px-4 py-3 text-right text-gray-900">{formatter.format(channel.profit)}</td>
                                                                <td className="px-4 py-3 text-right font-semibold text-indigo-600">{channel.margin.toFixed(0)}%</td>
                                                                <td className="px-4 py-3 text-right text-gray-600">{channel.deals.toLocaleString()}</td>
                                                            </tr>
                                                        );
                                                    })}
                                                {/* Grand Total Row */}
                                                <tr className="border-t-2 border-gray-300 bg-gray-50 font-bold">
                                                    <td className="px-4 py-3 text-gray-900">Grand Total</td>
                                                    <td className="px-4 py-3 text-right text-gray-900">
                                                        {(() => {
                                                            const formatter = new Intl.NumberFormat('vi-VN', { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 0 });
                                                            const totalRevenue = channelData.overview.reduce((sum, ch) => sum + ch.revenue, 0);
                                                            return formatter.format(totalRevenue);
                                                        })()}
                                                    </td>
                                                    <td className="px-4 py-3 text-right text-gray-900">
                                                        {(() => {
                                                            const formatter = new Intl.NumberFormat('vi-VN', { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 0 });
                                                            const totalProfit = channelData.overview.reduce((sum, ch) => sum + ch.profit, 0);
                                                            return formatter.format(totalProfit);
                                                        })()}
                                                    </td>
                                                    <td className="px-4 py-3 text-right text-indigo-600">
                                                        {(() => {
                                                            const totalRevenue = channelData.overview.reduce((sum, ch) => sum + ch.revenue, 0);
                                                            const totalProfit = channelData.overview.reduce((sum, ch) => sum + ch.profit, 0);
                                                            const avgMargin = totalRevenue > 0 ? (totalProfit / totalRevenue * 100) : 0;
                                                            return avgMargin.toFixed(0);
                                                        })()}%
                                                    </td>
                                                    <td className="px-4 py-3 text-right text-gray-600">
                                                        {channelData.overview.reduce((sum, ch) => sum + ch.deals, 0).toLocaleString()}
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="bg-white rounded-xl shadow-lg p-8 text-center">
                                <p className="text-gray-600">No channel data available.</p>
                            </div>
                        )}
                    </div>
                )}


                {/* Credit Control Tab */}
                {activeTab === 'credit' && (
                    <div>
                        {/* Snapshot Date Selector */}
                        {selectedDebtDate && (
                            <div className="bg-white rounded-lg shadow-md border border-gray-200 px-4 py-3 mb-6 inline-block">
                                <label className="text-xs text-gray-600 font-medium block mb-1">Snapshot Date</label>
                                <input
                                    type="date"
                                    value={selectedDebtDate}
                                    onChange={(e) => setSelectedDebtDate(e.target.value)}
                                    className="text-sm font-semibold text-gray-900 bg-transparent border-none focus:outline-none cursor-pointer"
                                />
                            </div>
                        )}

                        {debtLoading ? (
                            <div className="h-64 flex items-center justify-center">
                                <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-200 border-t-indigo-600"></div>
                            </div>
                        ) : debtData ? (
                            <>
                                {/* Row 1: KPI Cards */}
                                <div className="grid grid-cols-4 gap-4 mb-6">
                                    <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-red-500">
                                        <h3 className="text-sm font-medium text-gray-600 mb-2">Total Outstanding</h3>
                                        <p className="text-3xl font-bold text-gray-900">{(debtData.kpis.total_outstanding / 1e9).toFixed(2)}B</p>
                                        <p className="text-xs text-gray-500 mt-1">VND</p>
                                    </div>
                                    <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
                                        <h3 className="text-sm font-medium text-gray-600 mb-2">Total Collected</h3>
                                        <p className="text-3xl font-bold text-gray-900">{(debtData.kpis.total_collected / 1e9).toFixed(2)}B</p>
                                        <p className="text-xs text-gray-500 mt-1">VND</p>
                                    </div>
                                    <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
                                        <h3 className="text-sm font-medium text-gray-600 mb-2">Collection Rate</h3>
                                        <p className="text-3xl font-bold text-gray-900">{debtData.kpis.collection_rate.toFixed(0)}%</p>
                                        <p className="text-xs text-gray-500 mt-1">Efficiency</p>
                                    </div>
                                    <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-orange-500">
                                        <h3 className="text-sm font-medium text-gray-600 mb-2">Bad Debt (&gt;180 Days)</h3>
                                        <p className="text-3xl font-bold text-gray-900">{(debtData.kpis.bad_debt / 1e9).toFixed(2)}B</p>
                                        <p className="text-xs text-orange-600 mt-1">{((debtData.kpis.bad_debt / debtData.kpis.total_outstanding) * 100).toFixed(1)}% of total</p>
                                    </div>
                                </div>

                                {/* Row 2: Collection Efficiency Chart */}
                                <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-gray-200">
                                    <h3 className="text-xl font-bold text-gray-900 mb-4">Collection Efficiency by Channel</h3>
                                    <ResponsiveContainer width="100%" height={350}>
                                        <BarChart data={debtData.channel_breakdown} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="channel" />
                                            <YAxis tickFormatter={(value) => `${(value / 1e9).toFixed(1)}B`} />
                                            <Tooltip formatter={(value: number) => `${(value / 1e9).toFixed(2)}B VND`} />
                                            <Legend />
                                            <Bar dataKey="outstanding" fill="#ff4d4f" name="Outstanding" radius={[8, 8, 0, 0]} />
                                            <Bar dataKey="collected" fill="#52c41a" name="Collected" radius={[8, 8, 0, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>

                                {/* Row 3: Aging Structure + Top Debtors */}
                                <div className="grid grid-cols-2 gap-6 mb-6">
                                    {/* Aging Structure */}
                                    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                                        <h3 className="text-xl font-bold text-gray-900 mb-4">Aging Structure</h3>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <BarChart data={Object.entries(debtData.aging_breakdown).map(([name, value]) => ({ name, value }))} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                                                <YAxis tickFormatter={(value) => `${(value / 1e9).toFixed(1)}B`} />
                                                <Tooltip formatter={(value: number) => `${(value / 1e9).toFixed(2)}B VND`} />
                                                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                                                    {Object.keys(debtData.aging_breakdown).map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={['#52c41a', '#73d13d', '#faad14', '#ff7a45', '#ff4d4f', '#cf1322'][index]} />
                                                    ))}
                                                </Bar>
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>

                                    {/* Top 10 Debtors Table */}
                                    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                                        <h3 className="text-xl font-bold text-gray-900 mb-4">Top 10 Debtors</h3>
                                        <div className="overflow-auto max-h-[300px]">
                                            <table className="w-full text-sm">
                                                <thead className="bg-gray-50 sticky top-0">
                                                    <tr>
                                                        <th className="px-4 py-2 text-left font-semibold text-gray-700">Customer</th>
                                                        <th className="px-4 py-2 text-left font-semibold text-gray-700">Channel</th>
                                                        <th className="px-4 py-2 text-right font-semibold text-gray-700">Total Debt</th>
                                                        <th className="px-4 py-2 text-right font-semibold text-gray-700">Overdue</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {topDebtors.map((debtor) => (
                                                        <tr key={debtor.customer_code} className="border-t border-gray-200 hover:bg-gray-50">
                                                            <td className="px-4 py-2 text-gray-900">{debtor.customer_name}</td>
                                                            <td className="px-4 py-2">
                                                                <span className={`px-2 py-1 rounded text-xs font-medium ${debtor.channel === 'Industry' ? 'bg-blue-100 text-blue-800' :
                                                                    debtor.channel === 'Retail' ? 'bg-green-100 text-green-800' :
                                                                        debtor.channel === 'Project' ? 'bg-purple-100 text-purple-800' :
                                                                            'bg-gray-100 text-gray-800'
                                                                    }`}>
                                                                    {debtor.channel}
                                                                </span>
                                                            </td>
                                                            <td className="px-4 py-2 text-right font-semibold text-gray-900">{(debtor.total_debt / 1e9).toFixed(2)}B</td>
                                                            <td className="px-4 py-2 text-right">
                                                                <span className={`font-semibold ${debtor.overdue > 0 ? 'text-red-600' : 'text-green-600'}`}>
                                                                    {(debtor.overdue / 1e9).toFixed(2)}B
                                                                </span>
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>

                                {/* Row 4: Division Performance Summary */}
                                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                                    <h3 className="text-xl font-bold text-gray-900 mb-4">Division Performance Summary</h3>
                                    <div className="overflow-auto">
                                        <table className="w-full text-sm">
                                            <thead className="bg-gray-50">
                                                <tr>
                                                    <th className="px-4 py-3 text-left font-semibold text-gray-700">Division</th>
                                                    <th className="px-4 py-3 text-right font-semibold text-gray-700">Total Target</th>
                                                    <th className="px-4 py-3 text-right font-semibold text-gray-700">Total Realization</th>
                                                    <th className="px-4 py-3 text-right font-semibold text-gray-700">Collection Rate</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {[...debtData.channel_breakdown]
                                                    .sort((a, b) => {
                                                        const order = ['Industry', 'Retail', 'Project', 'Others'];
                                                        return order.indexOf(a.channel) - order.indexOf(b.channel);
                                                    })
                                                    .map((channel) => {
                                                        const collectionRate = channel.outstanding > 0 ? ((channel.collected / channel.outstanding) * 100) : 0;
                                                        const fullFormatter = new Intl.NumberFormat('vi-VN', { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 0 });
                                                        return (
                                                            <tr key={channel.channel} className="border-t border-gray-200 hover:bg-gray-50">
                                                                <td className="px-4 py-3 font-medium text-gray-900">{channel.channel}</td>
                                                                <td className="px-4 py-3 text-right text-gray-900">{fullFormatter.format(channel.outstanding)}</td>
                                                                <td className="px-4 py-3 text-right text-gray-900">{fullFormatter.format(channel.collected)}</td>
                                                                <td className="px-4 py-3 text-right font-semibold text-indigo-600">{collectionRate.toFixed(0)}%</td>
                                                            </tr>
                                                        );
                                                    })}
                                                {/* Grand Total Row */}
                                                <tr className="border-t-2 border-gray-300 bg-gray-50 font-bold">
                                                    <td className="px-4 py-3 text-gray-900">Grand Total</td>
                                                    <td className="px-4 py-3 text-right text-gray-900">
                                                        {(() => {
                                                            const fullFormatter = new Intl.NumberFormat('vi-VN', { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 0 });
                                                            return fullFormatter.format(debtData.channel_breakdown.reduce((sum, ch) => sum + ch.outstanding, 0));
                                                        })()}
                                                    </td>
                                                    <td className="px-4 py-3 text-right text-gray-900">
                                                        {(() => {
                                                            const fullFormatter = new Intl.NumberFormat('vi-VN', { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 0 });
                                                            return fullFormatter.format(debtData.channel_breakdown.reduce((sum, ch) => sum + ch.collected, 0));
                                                        })()}
                                                    </td>
                                                    <td className="px-4 py-3 text-right text-indigo-600">
                                                        {(() => {
                                                            const totalOutstanding = debtData.channel_breakdown.reduce((sum, ch) => sum + ch.outstanding, 0);
                                                            const totalCollected = debtData.channel_breakdown.reduce((sum, ch) => sum + ch.collected, 0);
                                                            const grandCollectionRate = totalOutstanding > 0 ? ((totalCollected / totalOutstanding) * 100) : 0;
                                                            return grandCollectionRate.toFixed(0);
                                                        })()}%
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="bg-white rounded-xl shadow-lg p-8 text-center">
                                <p className="text-gray-600">No debt data available. Please upload a debt report first.</p>
                                <a href="/import" className="inline-block mt-4 text-indigo-600 hover:text-indigo-800 font-medium">
                                    → Go to Data Management
                                </a>
                            </div>
                        )}
                    </div>
                )}

                {/* Floating Chat Widget */}
                <ChatWidget />
            </div>
        </div>
    );
};

export default AnalyticsPage;
