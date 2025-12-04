-- Re-Architected View: view_sales_performance_v2
-- Purpose: Accurate monthly performance with proper monthly targets

-- Drop old view
DROP VIEW IF EXISTS view_sales_performance;
DROP VIEW IF EXISTS view_sales_performance_v2;

-- Create new view with monthly_targets join
CREATE VIEW view_sales_performance_v2 AS
SELECT 
    s.salesman_name,
    s.year,
    s.month_number,
    -- Semester Logic
    CASE WHEN s.month_number <= 6 THEN 1 ELSE 2 END as semester,
    
    -- Revenue (Aggregated from Sales Data)
    SUM(s.net_value) as total_revenue,
    
    -- Profit (Revenue - COGS)
    SUM(s.net_value - (s.billing_qty * COALESCE(pc.cogs, 0))) as total_profit,
    
    -- Target (Directly from monthly_targets table)
    COALESCE(MAX(mt.target_amount), 0) as total_target,
    
    -- Achievement % (Standard Formula)
    CASE 
        WHEN COALESCE(MAX(mt.target_amount), 0) > 0 
        THEN ROUND((SUM(s.net_value) * 1.0 / MAX(mt.target_amount)) * 100, 2)
        ELSE 0 
    END as achievement_percentage

FROM sales_data s
LEFT JOIN product_cost pc ON s.description = pc.description
-- CRITICAL: Join with monthly_targets (not sales_target)
LEFT JOIN monthly_targets mt ON s.salesman_name = mt.user_name 
                             AND s.year = mt.year 
                             AND s.month_number = mt.month_number
GROUP BY s.salesman_name, s.year, s.month_number;
