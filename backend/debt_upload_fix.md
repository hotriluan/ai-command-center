
# Debt Report Upload Error Fix

## Problem
**Error**: `TypeError: '<' not supported between instances of 'NoneType' and 'NoneType'`  
**Location**: `sqlalchemy\engine\default.py ... sorted(rows, key=operator.itemgetter(-1))`  
**Root Cause**: Dirty data in ZRFI005.XLSX with trailing empty rows causing NaN/None values that SQLAlchemy cannot sort.

## Solution Applied

### File Modified
`backend/debt_services.py` - Function: `import_debt_data()`

### Changes Made (Lines 37-56)

```python
# ===== ROBUST DATA CLEANING =====
# Step 1: Drop completely empty rows
df.dropna(how='all', inplace=True)

# Step 2: Filter rows with missing critical columns
# Customer Code and Customer Name are mandatory
critical_columns = ['Customer Code', 'Customer Name']
df.dropna(subset=critical_columns, inplace=True)

# Step 3: Convert pandas NaN to Python None for SQL NULL compatibility
df = df.where(pd.notnull(df), None)

# Step 4: Remove rows where Customer Code is empty string after stripping
df = df[df['Customer Code'].astype(str).str.strip() != '']

# Reset index after filtering
df.reset_index(drop=True, inplace=True)

print(f"Data cleaning: {len(df)} valid rows after filtering")
# ===== END DATA CLEANING =====
```

## What This Fixes

1. **Empty Rows**: Removes completely blank rows that Excel often adds at the end
2. **Missing Critical Data**: Ensures every record has Customer Code and Customer Name
3. **NaN Handling**: Converts pandas NaN to Python None for SQL compatibility
4. **Empty Strings**: Removes rows with whitespace-only Customer Codes
5. **Index Reset**: Prevents index gaps that could cause iteration issues

## Expected Behavior

- **Before**: Upload fails with TypeError when encountering empty rows
- **After**: Upload succeeds, logging "Data cleaning: X valid rows after filtering"
- Invalid rows are silently filtered out, only clean data is imported

## Testing

The server should auto-reload with `--reload` flag. To test:
1. Upload the ZRFI005.XLSX file via the API
2. Check terminal output for "Data cleaning: X valid rows after filtering"
3. Verify import completes without TypeError

## Additional Notes

- The fix is defensive and handles common Excel export issues
- No changes needed to the database schema or API endpoints
- The cleaning logic runs before any database operations, preventing partial imports
