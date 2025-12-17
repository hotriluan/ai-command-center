# Cache Stats Endpoint - Manual Addition Required

## Add this code to main.py

**Location:** Before the `if __name__ == "__main__":` line (around line 492)

```python
# --- PHASE 2A: CACHE MONITORING ---

@app.get("/api/cache/stats")
def get_cache_stats():
    """
    Get cache performance statistics
    Returns hit rate, cache size, and request counts
    """
    return cache.get_stats()
```

## Steps:

1. Open `backend/main.py`
2. Find the line: `if __name__ == "__main__":`
3. Add the code above BEFORE that line
4. Save the file
5. Restart backend server

## Verify:

```bash
curl http://localhost:8000/api/cache/stats
```

Expected output:
```json
{
  "hits": 0,
  "misses": 0,
  "sets": 0,
  "invalidations": 0,
  "hit_rate": 0,
  "total_requests": 0,
  "cache_size": 0
}
```
