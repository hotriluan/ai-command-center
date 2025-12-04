-- Database Optimization Script
-- Purpose: Add indexes for fast year-based filtering

-- Index for date-based filtering (year, month)
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_data(year, month_number);

-- Index for salesman filtering
CREATE INDEX IF NOT EXISTS idx_sales_man ON sales_data(salesman_name);

-- Index for description lookup
CREATE INDEX IF NOT EXISTS idx_sales_desc ON sales_data(description);

-- Composite index for performance queries
CREATE INDEX IF NOT EXISTS idx_sales_composite ON sales_data(salesman_name, year, month_number);

-- Index on product_cost for faster joins
CREATE INDEX IF NOT EXISTS idx_product_cost_desc ON product_cost(description);
