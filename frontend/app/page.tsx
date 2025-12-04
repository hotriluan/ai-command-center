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
 * @version 2.1.0
 */

'use client';

import React, { useEffect, useState } from 'react';
import ChatWidget from '../components/ChatWidget';
import SalesPerformanceWidget from '../components/SalesPerformanceWidget';
import KPISection from '../components/KPISection';
import BusinessCharts from '../components/BusinessCharts';
import YearSelector from '../components/YearSelector';

// --- Interfaces ---

interface KPIData {
    revenue: number;
    revenue_growth: number;
    profit: number;
    profit_growth: number;
    marketing: number;
    margin: number;
}

interface ChartDataPoint {
    name: string;
    value?: number;
    revenue?: number;
    profit?: number;
    [key: string]: any;
}

interface DashboardCharts {
    monthly_trend: ChartDataPoint[];
    channel_distribution: ChartDataPoint[];
    branch_distribution: ChartDataPoint[];
    top_products: ChartDataPoint[];
    top_salesmen: ChartDataPoint[];
}

interface SalesPerformance {
    name: string;
    semester: number;
    actual: number;
    target: number;
    rate: number;
    status: 'success' | 'warning' | 'destructive';
}

interface DashboardData {
    kpi: KPIData;
    charts: DashboardCharts;
    sales_performance: SalesPerformance[];
}

/**
 * Executive Dashboard 2.0 - Main Component
 */
const Page: React.FC = () => {
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    // Year Filter State
    const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
    const [availableYears, setAvailableYears] = useState<number[]>([]);

    /**
     * Fetches dashboard data from backend API
     */
    /**
     * Fetch available years on mount
     */
    const fetchAvailableYears = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/available-years');
            const data = await response.json();
            setAvailableYears(data.years || []);
            if (data.default_year) {
                setSelectedYear(data.default_year);
            }
        } catch (err) {
            console.error('Error fetching years:', err);
        }
    };

    /**
     * Fetches dashboard data from backend API (year-aware)
     */
    const fetchData = async () => {
        try {
            setLoading(true);
            const [dashboardRes, forecastRes] = await Promise.all([
                fetch(`http://localhost:8000/api/dashboard?year=${selectedYear}`),
                fetch(`http://localhost:8000/api/forecast?year=${selectedYear}`)
            ]);

            if (!dashboardRes.ok) throw new Error(`Dashboard API error! status: ${dashboardRes.status}`);

            const dashboardData = await dashboardRes.json();

            // Integrate Forecast Data
            if (forecastRes.ok) {
                const forecastData = await forecastRes.json();
                if (forecastData && forecastData.length > 0) {
                    // Replace monthly_trend with forecast data for the main chart
                    dashboardData.charts.monthly_trend = forecastData;
                }
            }

            setData(dashboardData);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch data');
            console.error('Error fetching dashboard data:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAvailableYears();
    }, []);

    useEffect(() => {
        if (selectedYear) {
            fetchData();
        }
    }, [selectedYear]);


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
    const salesPerformance = data?.sales_performance || [];

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 font-sans text-gray-900">
            <div className="container mx-auto px-6 py-8 max-w-7xl">
                {/* Header */}
                <header className="mb-10">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
                        <div>
                            <h1 className="text-4xl font-bold text-gray-900 tracking-tight bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                                Executive Dashboard 2.0
                            </h1>
                            <p className="text-gray-600 mt-2 font-medium">Real-time business intelligence with full transparency</p>
                        </div>

                        {/* Year Selector */}
                        <YearSelector
                            selectedYear={selectedYear}
                            onYearChange={setSelectedYear}
                        />
                    </div>

                    {/* Data Management Link */}
                    <a
                        href="/import"
                        className="flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg shadow-md hover:shadow-xl transition-all text-sm font-semibold"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        📊 Data Management
                    </a>
                </header>

                {/* KPI Cards */}
                <KPISection kpi={kpi} />

                {/* Sales Performance Widget */}
                {salesPerformance.length > 0 && (
                    <div className="mb-8">
                        <SalesPerformanceWidget data={salesPerformance} />
                    </div>
                )}

                {/* Business Charts */}
                <BusinessCharts charts={charts} />
            </div>

            {/* AI Chat Widget */}
            <ChatWidget />
        </div >
    );
};

export default Page;