# Chapter 9: Common Bug Patterns

A catalog of bugs that appear in almost every codebase. Learn to recognize the pattern, and you'll spot these instantly.

---

## 1. Null / None Reference

**The pattern:** Assuming a value exists when it might be null.

```python
# Bug
def get_display_name(user):
    return user["profile"]["display_name"].upper()

# Crash if: user is None, user has no "profile" key, or display_name is None

# Fix: defensive access
def get_display_name(user):
    if user and "profile" in user and user["profile"].get("display_name"):
        return user["profile"]["display_name"].upper()
    return "Anonymous"
```

**How to spot it:** Look for chains of attribute/key access without null checks. In stack traces, look for `NoneType has no attribute`, `TypeError: Cannot read property of undefined`, `NullPointerException`.

---

## 2. Off-by-One Errors

**The pattern:** Loop boundaries, array indices, or range calculations are off by exactly 1.

```python
# Bug: skips the last element
items = ["a", "b", "c", "d"]
for i in range(0, len(items) - 1):  # range(0, 3) → processes indices 0, 1, 2
    print(items[i])                   # misses items[3]

# Bug: fencepost error
# "How many fence sections between 5 posts?" → 4, not 5
num_sections = num_posts      # wrong
num_sections = num_posts - 1  # correct
```

**How to spot it:** Check every `<` vs `<=`, every `range(n)` vs `range(n+1)`, every `length` vs `length - 1`. Draw it out on paper if needed.

---

## 3. Race Conditions

**The pattern:** Two threads/processes access shared state, and the result depends on timing.

```python
# Bug: two threads can read balance before either writes
balance = 100

def withdraw(amount):
    global balance
    if balance >= amount:    # Thread A reads 100, Thread B reads 100
        balance -= amount    # Thread A: 100-80=20, Thread B: 100-80=20
        return True          # Both succeed, but balance should be -60
    return False

# Thread A: withdraw(80) → succeeds
# Thread B: withdraw(80) → also succeeds (overdraft!)

# Fix: use a lock
import threading
lock = threading.Lock()

def withdraw(amount):
    global balance
    with lock:
        if balance >= amount:
            balance -= amount
            return True
        return False
```

**How to spot it:** Shared mutable state + concurrency = danger. Look for global variables, class attributes, database rows, or files accessed by multiple threads/processes without synchronization.

---

## 4. Silent Exception Swallowing

**The pattern:** A bare `except` hides errors, making bugs invisible.

```python
# Bug: you'll never know what went wrong
def save_user(user):
    try:
        db.insert(user)
        cache.invalidate(user.id)
        email.send_welcome(user.email)
    except:
        pass  # Silently swallows ALL errors

# Fix: catch specific exceptions, log everything else
def save_user(user):
    try:
        db.insert(user)
    except IntegrityError:
        logger.warning("Duplicate user", user_id=user.id)
        raise
    
    try:
        cache.invalidate(user.id)
    except CacheError as e:
        logger.error("Cache invalidation failed", user_id=user.id, error=str(e))
        # Cache failure is non-critical, continue
    
    try:
        email.send_welcome(user.email)
    except EmailError as e:
        logger.error("Welcome email failed", user_id=user.id, error=str(e))
        # Queue for retry
```

---

## 5. Floating Point Comparison

**The pattern:** Comparing floats for equality fails due to precision.

```python
# Bug
>>> 0.1 + 0.2 == 0.3
False
>>> 0.1 + 0.2
0.30000000000000004

# Fix: use tolerance for comparison
import math
math.isclose(0.1 + 0.2, 0.3)  # True

# For money: NEVER use floats. Use integers (cents) or Decimal.
from decimal import Decimal
price = Decimal("19.99")
tax = Decimal("0.08")
total = price * (1 + tax)  # Exact: Decimal('21.5892')
```

---

## 6. String Encoding Issues

**The pattern:** Mixing bytes and strings, or assuming ASCII when data is UTF-8.

```python
# Bug: crashes on non-ASCII names
def process_name(name):
    return name.encode('ascii')  # Fails on "José", "München", "日本語"

# Fix: use UTF-8 everywhere
def process_name(name):
    return name.encode('utf-8')
```

**How to spot it:** `UnicodeDecodeError`, `UnicodeEncodeError`, garbled text (mojibake: "JosÃ©" instead of "José"), or `\x` sequences in output.

---

## 7. Mutable Default Arguments (Python-Specific)

**The pattern:** Default mutable arguments are shared across all calls.

```python
# Bug: all users share the same list!
def add_item(item, items=[]):
    items.append(item)
    return items

add_item("a")  # ["a"]
add_item("b")  # ["a", "b"]  ← "a" leaked from previous call!

# Fix: use None as default
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

---

## 8. Closure Over Loop Variable

**The pattern:** Closures capture the variable reference, not its value.

```javascript
// Bug: all callbacks print 5
for (var i = 0; i < 5; i++) {
  setTimeout(function() {
    console.log(i);  // All print 5 (i is 5 when callbacks run)
  }, 100);
}

// Fix 1: use let (block scoping)
for (let i = 0; i < 5; i++) {
  setTimeout(function() {
    console.log(i);  // Prints 0, 1, 2, 3, 4
  }, 100);
}

// Fix 2: IIFE to capture value
for (var i = 0; i < 5; i++) {
  (function(j) {
    setTimeout(function() {
      console.log(j);  // Prints 0, 1, 2, 3, 4
    }, 100);
  })(i);
}
```

---

## 9. Time Zone Bugs

**The pattern:** Storing or comparing times without timezone info.

```python
from datetime import datetime, timezone

# Bug: naive datetime loses timezone context
created_at = datetime.now()  # Local time — but which timezone?

# Fix: always use UTC for storage, convert for display
created_at = datetime.now(timezone.utc)

# Bug: comparing naive and aware datetimes
utc_time = datetime.now(timezone.utc)
local_time = datetime.now()
if utc_time > local_time:  # TypeError: can't compare offset-naive and offset-aware
    pass
```

**Rule of thumb:** Store as UTC. Display in user's timezone. Never mix naive and aware datetimes.

---

## 10. SQL Injection

**The pattern:** Concatenating user input into SQL queries.

```python
# Bug: SQL injection vulnerability
query = f"SELECT * FROM users WHERE name = '{user_input}'"
# If user_input = "'; DROP TABLE users; --"
# Query becomes: SELECT * FROM users WHERE name = ''; DROP TABLE users; --'

# Fix: always use parameterized queries
cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))
```

---

## 11. Integer Overflow

**The pattern:** Arithmetic exceeds the type's max value and wraps around.

```java
// Bug in Java/C/C++
int maxInt = Integer.MAX_VALUE;  // 2,147,483,647
int result = maxInt + 1;         // -2,147,483,648 (wraps around!)

// This breaks: vote counts, timestamps, file sizes, financial calculations
// Fix: use long, or check before arithmetic
if (a > 0 && b > Integer.MAX_VALUE - a) {
    throw new ArithmeticException("Integer overflow");
}
```

**Note:** Python handles this automatically with arbitrary-precision integers. JavaScript uses 64-bit floats, so it loses precision above 2^53.

---

## 12. Modifying a Collection While Iterating

```java
// Bug: ConcurrentModificationException
List<String> items = new ArrayList<>(Arrays.asList("a", "b", "c"));
for (String item : items) {
    if (item.equals("b")) {
        items.remove(item);  // Crashes!
    }
}

// Fix: use iterator's remove method
Iterator<String> it = items.iterator();
while (it.hasNext()) {
    if (it.next().equals("b")) {
        it.remove();  // Safe
    }
}

// Or in Python:
items = ["a", "b", "c"]
items = [x for x in items if x != "b"]  # Create new list
```

---

## Quick Pattern Recognition Guide

| Symptom | Likely Bug Pattern |
|---------|-------------------|
| Works locally, fails in production | Environment config, timezone, encoding |
| Works the first time, fails after | Mutable state, caching, connection pool exhaustion |
| Intermittent failures | Race condition, timeout, resource leak |
| Wrong numbers / calculations | Floating point, off-by-one, integer overflow |
| Data corruption | Race condition, SQL injection, encoding |
| Memory grows over time | Memory leak, unbounded cache, event listener not removed |
| "Impossible" state | Null reference, unhandled edge case, assumption violated |

---

**Previous:** [Chapter 8 — Debugging Distributed Systems](08-distributed-systems.md)
