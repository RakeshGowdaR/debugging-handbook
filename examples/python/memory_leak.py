"""
Bug Pattern: Memory Leak
Difficulty: Intermediate
Language: Python

THE SCENARIO:
Your web service processes requests fine for the first hour.
Then it starts slowing down. After 4 hours, it crashes with OOMKilled.
Memory usage graph goes up and never comes down.
"""

import sys
import time
import weakref
from functools import lru_cache

# ============================================================
# THE BUGGY CODE
# ============================================================

class RequestCache:
    """Cache API responses to avoid duplicate calls."""
    
    def __init__(self):
        self.cache = {}
    
    def get_or_fetch(self, url, fetch_fn):
        if url not in self.cache:
            response = fetch_fn(url)
            self.cache[url] = response  # Stored forever!
        return self.cache[url]


# Simulate requests with unique URLs
cache = RequestCache()

def simulate_api_response(url):
    """Simulate a large API response."""
    return {"url": url, "data": "x" * 10000}  # ~10KB per response


print("--- BUGGY VERSION: Memory grows forever ---")
for i in range(1000):
    # Each unique URL adds ~10KB that's never freed
    url = f"https://api.example.com/products/{i}?timestamp={time.time()}"
    cache.get_or_fetch(url, simulate_api_response)

print(f"  Cache size: {len(cache.cache)} entries")
print(f"  Memory used by cache: ~{sys.getsizeof(cache.cache) // 1024}KB for dict alone")
print(f"  Actual memory: ~{len(cache.cache) * 10}KB (including values)")
print(f"  After 1M requests: ~10GB. OOMKilled.")


# ============================================================
# THE FIXES
# ============================================================

# Fix 1: LRU Cache with max size
print("\n--- FIX 1: LRU Cache with max size ---")

class BoundedCache:
    """Cache with maximum size. Evicts oldest entries."""
    
    def __init__(self, max_size=100):
        from collections import OrderedDict
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get_or_fetch(self, url, fetch_fn):
        if url in self.cache:
            self.cache.move_to_end(url)  # Mark as recently used
            return self.cache[url]
        
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Remove oldest
        
        response = fetch_fn(url)
        self.cache[url] = response
        return response


bounded_cache = BoundedCache(max_size=100)
for i in range(1000):
    url = f"https://api.example.com/products/{i}"
    bounded_cache.get_or_fetch(url, simulate_api_response)

print(f"  Cache size after 1000 requests: {len(bounded_cache.cache)} (capped at 100)")
print(f"  Memory stays constant regardless of request count.")


# Fix 2: TTL-based expiration
print("\n--- FIX 2: TTL-based Cache ---")

class TTLCache:
    """Cache with time-based expiration."""
    
    def __init__(self, ttl_seconds=60):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get_or_fetch(self, url, fetch_fn):
        if url in self.cache:
            value, timestamp = self.cache[url]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[url]  # Expired
        
        response = fetch_fn(url)
        self.cache[url] = (response, time.time())
        return response
    
    def cleanup_expired(self):
        """Call periodically to remove expired entries."""
        now = time.time()
        expired = [k for k, (_, ts) in self.cache.items() if now - ts >= self.ttl]
        for k in expired:
            del self.cache[k]
        return len(expired)


ttl_cache = TTLCache(ttl_seconds=2)
for i in range(100):
    url = f"https://api.example.com/products/{i}"
    ttl_cache.get_or_fetch(url, simulate_api_response)

print(f"  Cache size immediately: {len(ttl_cache.cache)}")
time.sleep(2.5)
removed = ttl_cache.cleanup_expired()
print(f"  Cache size after TTL: {len(ttl_cache.cache)} ({removed} expired entries removed)")


# ============================================================
# THE LESSON
# ============================================================
"""
KEY TAKEAWAYS:

1. Any collection that grows without a bound is a memory leak
   - Dictionaries used as caches
   - Lists that accumulate log entries
   - Sets that track "seen" items

2. Every cache MUST have an eviction strategy:
   - Max size (LRU, LFU)
   - TTL (time-based expiration)
   - Or both (max size + TTL)

3. Use functools.lru_cache for simple cases:
   @lru_cache(maxsize=128)
   def expensive_function(arg):
       ...

4. Monitor memory in production:
   - Track process RSS over time
   - Alert if memory grows >X% per hour
   - Use tracemalloc to find what's allocating

5. In Python, even "deleted" objects may not free memory
   immediately — the GC runs periodically. For large cleanups,
   call gc.collect() explicitly.
"""
