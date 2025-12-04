-- Migration: Create view_sales_performance
-- Purpose: Pre-calculated performance metrics to handle Revenue vs Target queries
-- Fixes: SQLite integer division and complex join issues

-- Drop view if exists (for re-running migration)
DROP VIEW IF EXISTS view_sales_performance;

-- Create the performance view
CREATE VIEW view_sales_performance AS
SELECT 
    s.salesman_name,
    s.year,
    -- Calculate semester from month_number (1-6 = semester 1, 7-12 = semester 2)
    CASE 
        WHEN s.month_number <= 6 THEN 1
        ELSE 2
    END AS semester,
    -- Aggregate actual revenue by salesman, year, and semester
    SUM(s.net_value) AS actual_revenue,
    -- Get target amount from sales_target table
    COALESCE(t.target_amount, 0) AS target_amount,
    -- Calculate achievement percentage with proper float division
    CASE 
        WHEN COALESCE(t.target_amount, 0) > 0 THEN 
            ROUND((CAST(SUM(s.net_value) AS REAL) / t.target_amount) * 100, 2)
        ELSE 
            0
    END AS achievement_percentage
FROM 
    sales_data s
LEFT JOIN 
    sales_target t 
    ON s.salesman_name = t.salesman_name 
    AND s.year = t.year
    AND CASE 
            WHEN s.month_number <= 6 THEN 1
            ELSE 2
        END = t.semester
WHERE 
    s.salesman_name IS NOT NULL
GROUP BY 
    s.salesman_name, 
    s.year, 
    semester,
    t.target_amount;
