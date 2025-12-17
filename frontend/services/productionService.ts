/**
 * Production Analytics API Service
 * 
 * Provides functions to fetch production data from the backend API
 * 
 * @module ProductionService
 */

const API_BASE_URL = 'http://localhost:8000';

export interface ProductionOrder {
    order_id: string;
    material_code: string;
    material_description: string;
    order_type: string;
    sales_order_id?: string;
    mrp_controller: string;
    release_date: string;
    actual_finish_date: string;
    prep_time: number;
    production_time: number;
    delivery_time: number;
    total_lead_time: number;
    timeline_summary: string;
    order_qty: number;
    delivered_qty: number;
    yield_variance: number;
    yield_rate: number;
    yield_status: string;
}

export interface MTOLifecycle {
    month: string;
    month_name: string;
    prep_time: number;
    production_time: number;
    delivery_time: number;
    order_count: number;
}

export interface MTSEfficiency {
    month: string;
    month_name: string;
    production_time: number;
    order_count: number;
}

export interface ProductionAnalytics {
    summary_metrics: {
        total_orders: number;
        avg_prep_time: number;
        avg_production_time: number;
        avg_delivery_time: number;
        avg_total_lead_time: number;
        avg_yield_rate: number;
        mts_orders: number;
        mto_orders: number;
    };
    mto_lifecycle: MTOLifecycle[];
    mts_efficiency: MTSEfficiency[];
    order_details: ProductionOrder[];
}

export interface MrpController {
    mrp_controller: string;
    total_orders: number;
    avg_lead_time: number;
    avg_yield_rate: number;
}

export interface MrpPerformanceData {
    controllers: MrpController[];
}

/**
 * Fetch production analytics data with MTO/MTS lifecycle analysis
 * 
 * @param startDate - Start date in YYYY-MM-DD format (optional)
 * @param endDate - End date in YYYY-MM-DD format (optional)
 * @param mrpFilter - MRP controller filter (P01/P02/P03) (optional)
 * @returns Production analytics data
 */
export async function fetchProductionAnalytics(
    startDate?: string,
    endDate?: string,
    mrpFilter?: string
): Promise<ProductionAnalytics> {
    try {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (mrpFilter && mrpFilter !== 'All') params.append('mrp_filter', mrpFilter);

        const url = `${API_BASE_URL}/api/production/analytics${params.toString() ? `?${params.toString()}` : ''}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        // Backend returns {status, data: {...}}, extract data property
        return result.data || result;
    } catch (error) {
        console.error('Error fetching production analytics:', error);
        throw error;
    }
}

/**
 * Fetch MRP controller performance data
 * 
 * @returns MRP performance data grouped by controller
 */
export async function fetchMrpPerformance(): Promise<MrpPerformanceData> {
    try {
        const url = `${API_BASE_URL}/api/production/mrp-performance`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching MRP performance:', error);
        throw error;
    }
}

/**
 * Upload production data file
 * 
 * @param file - Excel file containing production data
 * @returns Upload result with statistics
 */
export async function uploadProductionData(file: File): Promise<{
    status: string;
    total_rows_in_file: number;
    imported_new: number;
    skipped_existing: number;
    message: string;
}> {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/import/production`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error uploading production data:', error);
        throw error;
    }
}
