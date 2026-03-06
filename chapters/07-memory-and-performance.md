# Chapter 7: Memory Leaks & Performance

## Memory Leaks

A memory leak happens when your program allocates memory but never releases it. Over time, the app uses more and more RAM until it crashes or gets killed by the OS.

## How to Spot a Memory Leak

```
Symptom: App gets slower over time, then crashes
Symptom: Memory usage graph goes up and never comes down
Symptom: OOMKilled in container logs
```

### Python: Common Leak Patterns

**1. Growing collections that are never cleaned:**

```python
# ❌ Cache that grows forever
cache = {}

def process_request(request_id, data):
    result = expensive_computation(data)
    cache[request_id] = result  # Never removed!
    return result

# ✅ Use LRU cache with max size
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_computation(data):
    # ...

# ✅ Or use TTL-based cache (see system-design-concepts examples)
```

**2. Event listeners never removed:**

```python
# ❌ Listener accumulates on every call
class DataProcessor:
    def start(self):
        event_bus.on("data_ready", self.handle_data)  # Added every call!

# ✅ Remove listener when done
class DataProcessor:
    def start(self):
        event_bus.on("data_ready", self.handle_data)

    def stop(self):
        event_bus.off("data_ready", self.handle_data)
```

**3. Circular references (in languages without cycle-aware GC):**

```python
# Python's GC handles most cycles, but these can delay collection
class Node:
    def __init__(self):
        self.parent = None
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self  # Circular: parent → child → parent
```

### JavaScript: Common Leak Patterns

```javascript
// ❌ Closures holding references to large objects
function createHandler() {
    const hugeData = loadMegabytesOfData();
    return function onClick() {
        console.log(hugeData.length);  // hugeData can never be GC'd
    };
}

// ❌ DOM elements removed but still referenced
const elements = [];
function addElement() {
    const el = document.createElement('div');
    document.body.appendChild(el);
    elements.push(el);  // Even after removing from DOM, array holds reference
}

// ❌ setInterval never cleared
function startPolling() {
    setInterval(() => {
        fetch('/api/status');  // Runs forever, even if component unmounts
    }, 1000);
}

// ✅ Always return cleanup function
function startPolling() {
    const id = setInterval(() => fetch('/api/status'), 1000);
    return () => clearInterval(id);
}
```

## Finding Memory Leaks

### Python

```python
# tracemalloc — built-in memory profiler
import tracemalloc

tracemalloc.start()

# ... run your code ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 10 memory consumers:")
for stat in top_stats[:10]:
    print(stat)
```

```bash
# objgraph — visualize object references
pip install objgraph

import objgraph
objgraph.show_most_common_types(limit=20)  # What objects exist?
objgraph.show_growth(limit=10)              # What's growing?
```

### JavaScript (Browser)

```
Chrome DevTools → Memory tab:
1. Take heap snapshot (before suspected leak)
2. Perform the action that leaks
3. Take another heap snapshot
4. Compare snapshots — look for objects that increased
5. "Retained size" shows memory held by each object
```

### Java

```bash
# Get heap dump
jmap -dump:live,format=b,file=heap.hprof <pid>

# Analyze with Eclipse MAT or VisualVM
# Look for: Dominator tree, biggest objects, leak suspects report
```

## Performance: Finding Slow Code

### The Performance Investigation Order

```
1. Measure first — don't guess where it's slow
2. Check the database — 90% of slowness is bad queries
3. Check network calls — external API latency, DNS resolution
4. Check algorithms — O(n²) loops, unnecessary work
5. Check memory — GC pauses, cache thrashing
```

### Python Profiling

```python
# cProfile — built-in, low overhead
import cProfile

cProfile.run('process_orders()', sort='cumulative')

# Output shows time per function:
#    ncalls  tottime  cumtime  filename:lineno(function)
#     1000    0.001    5.432  orders.py:12(process_order)
#     1000    5.200    5.200  db.py:45(execute_query)   ← BOTTLENECK
#     1000    0.150    0.150  pricing.py:8(calculate)
```

```python
# line_profiler — line-by-line timing
# pip install line_profiler

@profile
def process_order(order):
    user = get_user(order.user_id)       # Line 1: 0.5ms
    items = get_items(order.item_ids)     # Line 2: 200ms  ← SLOW
    total = calculate_total(items)        # Line 3: 0.1ms
    return create_invoice(user, total)    # Line 4: 1.2ms
```

### JavaScript Profiling

```
Chrome DevTools → Performance tab:
1. Click Record
2. Perform the slow action
3. Stop recording
4. Look at the flame chart:
   - Wide bars = slow functions
   - Tall stacks = deep call chains
   - Yellow = JavaScript, Purple = rendering, Green = painting
```

### Common Performance Fixes

| Problem | Symptom | Fix |
|---------|---------|-----|
| N+1 queries | 100 DB calls for 100 items | Batch into 1 query with `IN` clause |
| Missing DB index | Query takes seconds | Add index on filtered/sorted columns |
| Unnecessary re-renders | UI is janky | Memoize, use `shouldComponentUpdate` |
| Large payload | Slow API responses | Paginate, compress, select only needed fields |
| Synchronous I/O | Thread blocked | Use async I/O |
| Regex backtracking | CPU spike on certain inputs | Simplify regex, add timeout |
| Repeated computation | Same calculation done 1000x | Cache the result |

---

**Next:** [Chapter 8 — Debugging Distributed Systems](08-distributed-systems.md)
