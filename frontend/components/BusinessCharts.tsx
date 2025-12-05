import React from 'react';
import { BarChart3, PieChart, ShoppingBag, Users } from 'lucide-react';
import { ComposedChart, Line, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RePieChart, Pie, Cell, Legend } from 'recharts';
import { formatVND, formatCompactVND } from '@/lib/utils';

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

interface BusinessChartsProps {
    charts: DashboardCharts;
}

const CHART_COLORS = {
    revenue: '#10b981',
    profit: '#3b82f6',
    marketing: '#f43f5e',
    products: '#f59e0b',
    salesmen: '#8b5cf6',
    channels: ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']
};

const BusinessCharts: React.FC<BusinessChartsProps> = ({ charts }) => {
    return (
        <>
            {/* Main Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                {/* Monthly Trend Chart */}
                <section className="lg:col-span-2 bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow" aria-label="Chart showing actual vs forecasted revenue">
                    <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-gray-800">
                        <BarChart3 size={22} className="text-indigo-500" />
                        Sales Revenue
                    </h3>
                    <div className="h-80" role="img" aria-label="Chart showing actual vs forecasted revenue">
                        <ResponsiveContainer width="100%" height="100%">
                            <ComposedChart data={charts.monthly_trend} margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                                <XAxis
                                    dataKey="name"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#6b7280', fontSize: 12 }}
                                    dy={10}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#6b7280', fontSize: 12 }}
                                    tickFormatter={(value) => formatCompactVND(value)}
                                />
                                <Tooltip
                                    cursor={{ fill: '#f3f4f6' }}
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                    formatter={(value: number) => formatVND(value)}
                                />
                                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                                <Area
                                    type="monotone"
                                    dataKey="revenue"
                                    name="Actual Revenue"
                                    fill={CHART_COLORS.revenue}
                                    stroke={CHART_COLORS.revenue}
                                    fillOpacity={0.2}
                                    strokeWidth={2}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="profit"
                                    name="Profit"
                                    stroke={CHART_COLORS.profit}
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: "#fff", stroke: CHART_COLORS.profit, strokeWidth: 2 }}
                                />
                            </ComposedChart>
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
                <section className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow" aria-label="Top 10 Best-Selling Products">
                    <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-gray-800">
                        <ShoppingBag size={22} className="text-amber-500" />
                        Top 10 Best-Selling Products
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
                <section className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow" aria-label="Top 10 Salesmen by Performance">
                    <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-gray-800">
                        <Users size={22} className="text-purple-500" />
                        Top 10 Salesmen
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
        </>
    );
};

export default BusinessCharts;
