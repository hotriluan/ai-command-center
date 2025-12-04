import React from 'react';
import { DollarSign, TrendingUp, Percent } from 'lucide-react';
import KPICard from './KPICard';
import { formatVND, getGrowthData } from '@/lib/utils';

interface KPIData {
    revenue: number;
    revenue_growth: number;
    profit: number;
    profit_growth: number;
    marketing: number;
    margin: number;
}

interface KPISectionProps {
    kpi: KPIData;
}

const KPISection: React.FC<KPISectionProps> = ({ kpi }) => {
    return (
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8" aria-label="Key Performance Indicators">
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
                title="Profit Margin"
                value={`${kpi.margin.toFixed(1)}%`}
                icon={Percent}
                iconColor="text-amber-500"
                valueColor="text-amber-600"
            />
        </section>
    );
};

export default KPISection;
