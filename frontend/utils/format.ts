/**
 * Currency Formatting Utilities for Vietnamese Dong (VND)
 * Provides consistent number formatting across the application
 * @module utils/format
 */

/**
 * Formats a number as Vietnamese Dong with full number display (no abbreviation)
 * @param value - The numeric value to format
 * @returns Formatted currency string (e.g., "225.700.000.000 ₫")
 * @example
 * formatVND(225700000000) // Returns "225.700.000.000 ₫"
 */
export const formatVND = (value: number): string => {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND',
        maximumFractionDigits: 0,
        notation: 'standard' // FORCE FULL NUMBERS (e.g. 100.000.000 ₫)
    }).format(value);
};

/**
 * Formats a number as Vietnamese Dong with compact notation for space-constrained displays
 * @param value - The numeric value to format
 * @returns Compact formatted currency string (e.g., "225,7 tỉ ₫")
 * @example
 * formatCompactVND(225700000000) // Returns "225,7 tỉ ₫"
 */
export const formatCompactVND = (value: number): string => {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND',
        notation: 'compact',
        maximumFractionDigits: 1
    }).format(value);
};

/**
 * Formats a number as a percentage with sign indicator
 * @param value - The percentage value to format
 * @returns Formatted percentage string with +/- sign (e.g., "+12.5%" or "-3.2%")
 * @example
 * formatPercent(12.5) // Returns "+12.5%"
 * formatPercent(-3.2) // Returns "-3.2%"
 */
export const formatPercent = (value: number): string => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
};

/**
 * Growth data structure for trend indicators
 */
export interface GrowthData {
    /** Absolute value of growth percentage */
    value: number;
    /** Whether the growth is positive (true) or negative (false) */
    isPositive: boolean;
}

/**
 * Converts a growth value into a structured GrowthData object
 * @param growthValue - The growth percentage (can be positive or negative)
 * @returns GrowthData object with absolute value and direction
 * @example
 * getGrowthData(12.5) // Returns { value: 12.5, isPositive: true }
 * getGrowthData(-5.3) // Returns { value: 5.3, isPositive: false }
 */
export const getGrowthData = (growthValue: number): GrowthData => {
    return {
        value: Math.abs(growthValue),
        isPositive: growthValue >= 0
    };
};
