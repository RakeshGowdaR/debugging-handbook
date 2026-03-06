# Chapter 4: Reading Error Messages

## Most Developers Don't Actually Read Them

Error messages contain the answer 80% of the time. But developers glance at the first line, panic, and start Googling. Slow down. Read the whole thing.

## Anatomy of an Error Message

Every error message has three parts: **WHAT** happened (error type), **WHERE** it happened (file, line, function), and **WHY** (context).

### Python — Read Stack Traces Bottom-Up

```
Traceback (most recent call last):
  File "app.py", line 45, in process_order
    total = calculate_total(order.items)
  File "pricing.py", line 12, in calculate_total
    return sum(item.price * item.qty for item in items)
AttributeError: 'NoneType' object has no attribute 'price'
```

The last line is the error. The lines above show the call chain. Here: `items` contains a `None` value, and `.price` was called on it.

### JavaScript — Find YOUR Code

```
TypeError: Cannot read properties of undefined (reading 'map')
    at UserList (UserList.jsx:14:28)          ← YOUR code
    at renderWithHooks (react-dom.js:1234)    ← framework internals (skip)
```

**Ignore framework internals.** Find the first line referencing your code. Here: `UserList.jsx` line 14 — `.map()` called on `undefined`.

### Java — Check "Caused By"

```
Exception in thread "main" java.lang.NullPointerException:
  Cannot invoke "String.length()" because "str" is null
    at com.app.Parser.parse(Parser.java:23)
Caused by: ...    ← ROOT CAUSE is here
```

The top exception is often a wrapper. The real bug is in "Caused by."

## Common Error Messages Decoded

### Python

| Error | What It Really Means |
|-------|---------------------|
| `AttributeError: 'NoneType' has no attribute 'x'` | You have `None` where you expected an object |
| `KeyError: 'name'` | Dictionary doesn't have key `'name'` |
| `IndexError: list index out of range` | Accessed `list[5]` but list is shorter |
| `TypeError: unsupported operand type(s)` | Mixing types: `"5" + 5` or `None + 1` |
| `ImportError: No module named 'x'` | Package not installed, or wrong virtual environment |
| `RecursionError: maximum recursion depth` | Infinite recursion — missing base case |

### JavaScript

| Error | What It Really Means |
|-------|---------------------|
| `TypeError: x is not a function` | Calling something that isn't a function (typo? wrong import?) |
| `TypeError: Cannot read properties of undefined` | Variable is `undefined` — previous step returned nothing |
| `ReferenceError: x is not defined` | Variable doesn't exist in scope (typo? missing import?) |
| `SyntaxError: Unexpected token` | Malformed JSON, missing comma/bracket |
| `Unhandled Promise Rejection` | Async operation failed with no `.catch()` |

### HTTP Status Codes

```
400 Bad Request        → Your request body/params are wrong. Read the response body.
401 Unauthorized       → Missing or invalid auth token.
403 Forbidden          → Valid auth, but no permission for this resource.
404 Not Found          → Wrong URL or deleted resource.
422 Unprocessable      → Validation failed. Response body has details.
429 Too Many Requests  → Rate limited. Check Retry-After header.
500 Internal Server    → Bug on the server. Not your fault (usually).
502 Bad Gateway        → Server behind load balancer is down.
503 Service Unavailable → Server overloaded or in maintenance.
```

**The response body matters more than the status code.** A 400 with `{"error": "email already registered"}` tells you exactly what to fix.

## How to Google an Error

```
❌ Bad:  "my app is broken"
❌ Bad:  Paste the entire 50-line stack trace

✅ Good: Error TYPE + MESSAGE, minus your specific values
         "AttributeError: 'NoneType' object has no attribute" python

✅ Good: Include language/framework
         "Cannot read properties of undefined" react hooks

✅ Good: Add context if the error is generic
         "ECONNREFUSED" docker compose postgres
```

Strip out your variable names, file paths, and line numbers. Keep the error pattern.

## The 30-Second Error Reading Habit

1. **Read the error type** — What category? (Null, Type, Key, Network)
2. **Read the message** — What specific thing went wrong?
3. **Find YOUR code** in the stack trace — Skip framework lines
4. **Check that exact line** — What could be null/undefined/missing there?
5. **Check the input** — What data was passed to this function?

This takes 30 seconds and solves most bugs without Googling.

---

**Next:** [Chapter 5 — Logging That Actually Helps](05-logging-strategies.md)
