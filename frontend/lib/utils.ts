export const formatVND = (value: number) => {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND',
        maximumFractionDigits: 0,
        notation: "standard"
    }).format(value);
};

export const formatCompactVND = (value: number) => {
    if (value >= 1_000_000_000) {
        return `${(value / 1_000_000_000).toFixed(1)}B`;
    } else if (value >= 1_000_000) {
        return `${(value / 1_000_000).toFixed(1)}M`;
    } else {
        return formatVND(value);
    }
};

export interface GrowthData {
    value: number;
    isPositive: boolean;
}

export const getGrowthData = (growthValue: number): GrowthData => {
    return {
        value: Math.abs(growthValue),
        isPositive: growthValue >= 0
    };
};
