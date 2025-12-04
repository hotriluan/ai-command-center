/**
 * Year Selector Component
 * Allows users to filter dashboard data by year
 */

'use client';

import React, { useEffect, useState } from 'react';
import { Calendar } from 'lucide-react';

interface YearSelectorProps {
    selectedYear: number;
    onYearChange: (year: number) => void;
}

const YearSelector: React.FC<YearSelectorProps> = ({ selectedYear, onYearChange }) => {
    const [availableYears, setAvailableYears] = useState<number[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAvailableYears();
    }, []);

    const fetchAvailableYears = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/available-years');
            const data = await response.json();
            setAvailableYears(data.years || []);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching years:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center gap-2 text-gray-500">
                <Calendar className="w-5 h-5 animate-pulse" />
                <span className="text-sm">Loading...</span>
            </div>
        );
    }

    return (
        <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-indigo-600" />
            <select
                value={selectedYear}
                onChange={(e) => onYearChange(Number(e.target.value))}
                className="bg-white border-2 border-indigo-200 rounded-lg px-4 py-2 text-gray-900 font-semibold focus:outline-none focus:border-indigo-500 hover:border-indigo-400 transition-colors cursor-pointer"
            >
                {availableYears.map((year) => (
                    <option key={year} value={year}>
                        {year}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default YearSelector;
