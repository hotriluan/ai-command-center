import React, { useState, useMemo } from 'react';
import { Search, Filter, ArrowUpDown, Target, User, Award, AlertCircle } from 'lucide-react';
import { formatVND, formatCompactVND } from '@/lib/utils';

interface SalesPerformance {
    name: string;
    semester: number;
    actual: number;
    target: number;
    rate: number;
    status: 'success' | 'warning' | 'destructive';
}

interface SalesPerformanceWidgetProps {
    data: SalesPerformance[];
}

const SalesPerformanceWidget: React.FC<SalesPerformanceWidgetProps> = ({ data }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [semesterFilter, setSemesterFilter] = useState<number | 'all'>('all');
    const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');

    // Filter and Sort Logic
    const filteredData = useMemo(() => {
        let result = [...data];

        // 1. Filter by Name
        if (searchTerm) {
            result = result.filter(item =>
                item.name.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        // 2. Filter by Semester
        if (semesterFilter !== 'all') {
            result = result.filter(item => item.semester === semesterFilter);
        }

        // 3. Sort by Achievement Rate
        result.sort((a, b) => {
            return sortOrder === 'desc'
                ? b.rate - a.rate
                : a.rate - b.rate;
        });

        return result;
    }, [data, searchTerm, semesterFilter, sortOrder]);

    // Helper for Avatar Initials
    const getInitials = (name: string) => {
        return name
            .split(' ')
            .map(n => n[0])
            .join('')
            .substring(0, 2)
            .toUpperCase();
    };

    // Helper for Status Badge
    const getStatusBadge = (rate: number) => {
        if (rate >= 100) return { label: 'Excellent', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' };
        if (rate >= 80) return { label: 'Good', color: 'bg-amber-100 text-amber-700 border-amber-200' };
        return { label: 'Lagging', color: 'bg-red-100 text-red-700 border-red-200' };
    };

    if (!data || data.length === 0) return null;

    return (
        <section className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden flex flex-col h-[600px]" aria-label="Sales Performance Widget">
            {/* Header / Toolbar */}
            <div className="p-5 border-b border-gray-100 bg-gray-50/50 space-y-4 md:space-y-0 md:flex md:items-center md:justify-between">
                <div>
                    <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                        <Target className="text-indigo-600" size={20} />
                        Sales Performance
                        <span className="text-xs font-normal text-gray-500 bg-gray-200 px-2 py-0.5 rounded-full">
                            {filteredData.length} Results
                        </span>
                    </h3>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                    {/* Search */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                        <input
                            type="text"
                            placeholder="Search salesman..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none w-full sm:w-48"
                        />
                    </div>

                    {/* Semester Filter */}
                    <div className="relative">
                        <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                        <select
                            value={semesterFilter}
                            onChange={(e) => setSemesterFilter(e.target.value === 'all' ? 'all' : Number(e.target.value))}
                            className="pl-9 pr-8 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none appearance-none bg-white cursor-pointer"
                        >
                            <option value="all">All Semesters</option>
                            <option value={1}>Semester 1</option>
                            <option value={2}>Semester 2</option>
                        </select>
                    </div>

                    {/* Sort Toggle */}
                    <button
                        onClick={() => setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc')}
                        className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        title={sortOrder === 'desc' ? "Sort Lowest First" : "Sort Highest First"}
                    >
                        <ArrowUpDown size={16} />
                        {sortOrder === 'desc' ? 'Highest' : 'Lowest'}
                    </button>
                </div>
            </div>

            {/* List View */}
            <div className="flex-1 overflow-y-auto p-2 space-y-2 custom-scrollbar">
                {filteredData.length > 0 ? (
                    filteredData.map((item, idx) => {
                        const badge = getStatusBadge(item.rate);
                        return (
                            <div
                                key={`${item.name}-${item.semester}-${idx}`}
                                className="group p-4 bg-white border border-gray-100 rounded-lg hover:border-indigo-200 hover:shadow-md transition-all duration-200"
                            >
                                <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                                    {/* Avatar & Name */}
                                    <div className="flex items-center gap-3 min-w-[200px]">
                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shadow-sm ${item.rate >= 100 ? 'bg-emerald-100 text-emerald-600' :
                                            item.rate >= 80 ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-500'
                                            }`}>
                                            {getInitials(item.name)}
                                        </div>
                                        <div>
                                            <h4 className="font-semibold text-gray-900 text-sm">{item.name}</h4>
                                            <span className="text-xs text-gray-500 font-medium">Semester {item.semester}</span>
                                        </div>
                                    </div>

                                    {/* Progress & Stats */}
                                    <div className="flex-1 grid grid-cols-1 md:grid-cols-12 gap-4 items-center">

                                        {/* Values */}
                                        <div className="md:col-span-4 flex flex-col md:items-end">
                                            <div className="text-sm font-bold text-gray-800">
                                                {formatCompactVND(item.actual)}
                                                <span className="text-gray-400 font-normal mx-1">/</span>
                                                {formatCompactVND(item.target)}
                                            </div>
                                            <div className="text-xs text-gray-500">Actual vs Target</div>
                                        </div>

                                        {/* Progress Bar */}
                                        <div className="md:col-span-5 w-full">
                                            <div className="flex justify-between text-xs mb-1 font-medium">
                                                <span className={`${item.rate >= 100 ? 'text-emerald-600' :
                                                    item.rate >= 80 ? 'text-amber-600' : 'text-red-600'
                                                    }`}>
                                                    {item.rate.toFixed(1)}% Achievement
                                                </span>
                                            </div>
                                            <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                                                <div
                                                    className={`h-full rounded-full transition-all duration-500 ${item.rate >= 100 ? 'bg-gradient-to-r from-emerald-500 to-emerald-400' :
                                                        item.rate >= 80 ? 'bg-gradient-to-r from-amber-500 to-amber-400' :
                                                            'bg-gradient-to-r from-red-500 to-red-400'
                                                        }`}
                                                    style={{ width: `${Math.min(item.rate, 100)}%` }}
                                                />
                                            </div>
                                        </div>

                                        {/* Badge */}
                                        <div className="md:col-span-3 flex justify-end">
                                            <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${badge.color}`}>
                                                {badge.label}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })
                ) : (
                    <div className="flex flex-col items-center justify-center h-full text-gray-400 py-12">
                        <Search size={48} className="mb-4 opacity-20" />
                        <p className="text-lg font-medium">No results found</p>
                        <p className="text-sm">Try adjusting your search or filters</p>
                    </div>
                )}
            </div>
        </section>
    );
};

export default SalesPerformanceWidget;
