"""
Cache Manager - Thread-safe in-memory cache with TTL
Phase 2A: Query Result Caching
"""

import time
from typing import Any, Optional
from threading import Lock
from datetime import datetime


class SimpleCache:
    """
    Thread-safe in-memory cache with TTL (Time-To-Live)
    
    Features:
    - Automatic expiration based on TTL
    - Thread-safe operations
    - Pattern-based invalidation
    - Cache statistics tracking
    """
    
    def __init__(self, default_ttl: int = 600):
        """
        Initialize cache
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 10 minutes)
        """
        self.cache = {}
        self.lock = Lock()
        self.default_ttl = default_ttl
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'invalidations': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        with self.lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                
                # Check if expired
                if time.time() < expiry:
                    self.stats['hits'] += 1
                    return value
                else:
                    # Remove expired entry
                    del self.cache[key]
                    self.stats['misses'] += 1
                    return None
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        with self.lock:
            expiry = time.time() + (ttl or self.default_ttl)
            self.cache[key] = (value, expiry)
            self.stats['sets'] += 1
    
    def invalidate(self, pattern: str = None):
        """
        Invalidate cache entries
        
        Args:
            pattern: If provided, only invalidate keys containing this pattern.
                    If None, invalidate all entries.
        """
        with self.lock:
            if pattern:
                # Invalidate matching keys
                keys_to_delete = [k for k in self.cache if pattern in k]
                for k in keys_to_delete:
                    del self.cache[k]
                self.stats['invalidations'] += len(keys_to_delete)
            else:
                # Invalidate all
                count = len(self.cache)
                self.cache.clear()
                self.stats['invalidations'] += count
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats including hit rate
        """
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'invalidations': self.stats['invalidations'],
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests,
                'cache_size': len(self.cache)
            }
    
    def clear_stats(self):
        """Reset statistics counters"""
        with self.lock:
            self.stats = {
                'hits': 0,
                'misses': 0,
                'sets': 0,
                'invalidations': 0
            }


# Cache TTL configurations (in seconds)
CACHE_TTL = {
    'dashboard': 900,      # 15 minutes - stable data
    'analytics': 600,      # 10 minutes - frequently viewed
    'debt': 1800,          # 30 minutes - rarely changes
    'forecast': 3600,      # 1 hour - expensive computation
    'default': 600         # 10 minutes - fallback
}


# Global cache instance
cache = SimpleCache(default_ttl=CACHE_TTL['default'])


def get_cache_key(endpoint: str, **params) -> str:
    """
    Generate cache key from endpoint and parameters
    
    Args:
        endpoint: API endpoint name
        **params: Query parameters
        
    Returns:
        Cache key string
    """
    # Sort params for consistent keys
    param_str = ':'.join(f"{k}={v}" for k, v in sorted(params.items()) if v is not None)
    return f"{endpoint}:{param_str}" if param_str else endpoint
