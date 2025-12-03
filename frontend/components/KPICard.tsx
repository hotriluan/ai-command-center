/**
 * KPICard Component
 * 
 * A premium card component for displaying Key Performance Indicators (KPIs)
 * with trend indicators, semantic colors, and decorative background icons.
 * 
 * Features:
 * - Full number display without truncation
 * - Growth badges with trend arrows (up/down)
 * - Semantic color coding
 * - Hover effects and animations
 * - Accessible with ARIA labels
 * 
 * @module components/KPICard
 * @author AI Command Center Team
 */

'use client';

import React from 'react';
import { TrendingUp, TrendingDown, LucideIcon } from 'lucide-react';

/**
 * Props for the KPICard component
 */
interface KPICardProps {
    /** The title/label of the KPI (e.g., "Total Revenue") */
    title: string;
    /** The formatted value to display (e.g., "225.700.000.000 ₫") */
    value: string;
    /** Optional growth data for trend indicator */
    growth?: {
        /** Absolute growth percentage value */
        value: number;
        /** Whether growth is positive (true) or negative (false) */
        isPositive: boolean;
    };
    /** Lucide icon component to display */
    icon: LucideIcon;
    /** Tailwind color class for the icon (e.g., "text-emerald-500") */
    iconColor: string;
    /** Tailwind color class for the value text (e.g., "text-emerald-600") */
    valueColor: string;
}

/**
 * KPICard Component
 * 
 * Displays a key performance indicator with optional growth trend
 * 
 * @param props - Component props
 * @returns Rendered KPI card component
 */
const KPICard: React.FC<KPICardProps> = ({
    title,
    value,
    growth,
    icon: Icon,
    iconColor,
    valueColor
}) => {
    const titleId = `kpi-title-${title.replace(/\s+/g, '-').toLowerCase()}`;

    return (
        <div
            className="relative bg-white rounded-xl shadow-sm border border-gray-100 p-6 transition-all hover:shadow-lg hover:border-gray-200 overflow-hidden group"
            role="article"
            aria-label={`${title}: ${value}`}
        >
            {/* Background Icon - Decorative */}
            <div className="absolute top-4 right-4 opacity-5 group-hover:opacity-10 transition-opacity" aria-hidden="true">
                <Icon size={80} className={iconColor} />
            </div>

            {/* Content */}
            <div className="relative z-10">
                {/* Title */}
                <p className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wide" id={titleId}>
                    {title}
                </p>

                {/* Main Value - Full Number Display */}
                <h3
                    className={`text-2xl lg:text-3xl font-bold ${valueColor} mb-3 tracking-tight break-words leading-tight`}
                    aria-describedby={titleId}
                >
                    {value}
                </h3>

                {/* Growth Badge */}
                {growth && (
                    <div
                        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${growth.isPositive
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : 'bg-red-50 text-red-700 border border-red-200'
                            }`}
                        role="status"
                        aria-label={`Growth: ${growth.isPositive ? 'positive' : 'negative'} ${growth.value.toFixed(1)} percent`}
                    >
                        {growth.isPositive ? (
                            <TrendingUp size={14} strokeWidth={2.5} aria-hidden="true" />
                        ) : (
                            <TrendingDown size={14} strokeWidth={2.5} aria-hidden="true" />
                        )}
                        <span>
                            {growth.isPositive ? '+' : '-'}{Math.abs(growth.value).toFixed(1)}% vs last month
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default KPICard;
