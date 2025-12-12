
# Performance Audit Report

## 1. Executive Summary
**Finding**: Critical Performance Issues Detected.
**Average Latency**: ~4,500ms (4.5 seconds) per request.
**Root Cause**: Inefficient Schema (TEXT columns) and Missing Indexes on Join Keys.

## 2. Detailed Findings

### A. Schema Issues (Critical)
The migration from SQLite created columns as `TEXT` by default. In MySQL, `TEXT` columns:
1.  Cannot be fully indexed without prefix length.
2.  Force temporary tables to disk during sorting/grouping (which Dashboard does extensively).
3.  Are significantly slower for JOIN operations.

**Affected Columns:**
- `sales_data.dist` (TEXT) - Used in Group By
- `sales_data.salesman_name` (TEXT) - Used in Group By & Join
- `sales_data.description` (TEXT) - Used in Join with `product_cost`
- `product_cost.description` (TEXT) - Used in Join

### B. Missing Indexes
While `year` index exists, indexes are missing for:
- `salesman_name` (Needed for View joins)
- `dist` (Needed for Channel Analysis)
- `description` (Needed for Product Matrix and COGS join)

### C. Connection Overhead
SQLAlchemy is using default settings. For high-concurrency or repetitive API calls, connection pooling is essential.

## 3. Fix Plan

### Step 1: Schema Optimization
Convert all Low-Cardinality TEXT columns to `VARCHAR(255)`.

### Step 2: Index Creation
Create indexes on the newly converted `VARCHAR` columns.

### Step 3: Connection Pooling
Enable SQLAlchemy QueuePool with:
- `pool_size=10`
- `max_overflow=20`
- `pool_recycle=3600`

## 4. Expected Outcome
Latency reduction from **4.5s** to **<200ms**.
