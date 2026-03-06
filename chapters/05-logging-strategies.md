# Chapter 5: Logging That Actually Helps

## Most Logs Are Useless. Here's How to Fix That.

Bad logging:
```
INFO: Processing...
INFO: Done.
ERROR: Something went wrong
```

Good logging:
```
INFO: Processing order order_id=ORD-4521 user_id=USR-892 items=3 total=149.99
INFO: Payment charged order_id=ORD-4521 provider=stripe charge_id=ch_3K2j amount=149.99 latency_ms=230
ERROR: Inventory update failed order_id=ORD-4521 sku=SHIRT-BLU-M available=0 requested=1 error="out of stock"
```

The difference? The second one tells you **what happened, to whom, and why** — without needing to reproduce anything.

## The Four Rules of Useful Logs

### Rule 1: Include Identifiers in Every Log Line

Every log line should answer: **which** user? **which** request? **which** record?

```python
# ❌ Useless in production
logger.info("User logged in")
logger.error("Payment failed")

# ✅ Actionable in production
logger.info("User logged in", extra={"user_id": user.id, "ip": request.ip, "method": "oauth"})
logger.error("Payment failed", extra={"user_id": user.id, "order_id": order.id, "error": str(e), "provider": "stripe"})
```

### Rule 2: Use Structured Logging

Plaintext logs are hard to search. Structured logs (JSON) can be queried:

```python
import structlog

logger = structlog.get_logger()

# This outputs searchable JSON
logger.info("order.created", order_id="ORD-4521", user_id="USR-892", total=149.99)

# {"event": "order.created", "order_id": "ORD-4521", "user_id": "USR-892", "total": 149.99, "timestamp": "2024-..."}
```

Now you can search: `order_id=ORD-4521` and get every log line for that order across all services.

### Rule 3: Use Correlation IDs to Trace Requests

When a request touches multiple services, a single ID ties all the logs together:

```python
# Generate at the API gateway / first service
import uuid

@app.middleware("http")
async def add_correlation_id(request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    # Attach to all logs for this request
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

Now search by correlation_id and see the full journey of a request:

```
correlation_id=abc-123 service=api-gateway  "Received POST /checkout"
correlation_id=abc-123 service=order-svc    "Order created ORD-4521"
correlation_id=abc-123 service=payment-svc  "Charge initiated $149.99"
correlation_id=abc-123 service=payment-svc  "Charge succeeded ch_3K2j"
correlation_id=abc-123 service=inventory    "Stock updated SKU-001 qty=-1"
correlation_id=abc-123 service=email-svc    "Confirmation sent user@example.com"
```

### Rule 4: Log at the Right Level

```
DEBUG  → Detailed internal state (variable values, loop iterations)
         Only enable in development or temporarily in production.

INFO   → Business events (user signed up, order placed, job completed).
         The "story" of what your system is doing.

WARN   → Something unexpected but handled (retry succeeded, fallback used, deprecated API called).
         Investigate if frequency increases.

ERROR  → Something failed and needs attention (payment failed, DB timeout, unhandled exception).
         Should trigger an alert.

FATAL  → System cannot continue (DB connection lost, out of memory, corrupt config).
         Should page someone.
```

## What to Log at Key Points

```python
# Entry points — log inputs
logger.info("api.request", method=request.method, path=request.path, user_id=user.id)

# Decision points — log why a branch was taken
logger.info("pricing.discount_applied", reason="loyalty_tier", discount=0.15, user_tier="gold")

# External calls — log request and response
logger.info("external.call", service="stripe", action="charge", amount=149.99, latency_ms=230)

# Errors — log everything needed to reproduce
logger.error("order.failed",
    order_id=order.id, user_id=user.id,
    step="inventory_check", error=str(e),
    sku=item.sku, requested_qty=item.qty, available_qty=stock.qty
)

# Exit points — log outcomes
logger.info("api.response", status=200, latency_ms=total_ms, order_id=order.id)
```

## Anti-Patterns

```python
# ❌ Logging sensitive data
logger.info(f"User login: password={password}")  # NEVER

# ❌ Logging inside tight loops
for item in million_items:
    logger.debug(f"Processing {item}")  # Will destroy performance

# ❌ String concatenation (evaluated even if level is filtered)
logger.debug("User " + str(user) + " did " + str(action))  # Slow
logger.debug("User %s did %s", user, action)  # Fast — only evaluated if DEBUG is enabled

# ❌ Catching and logging without context
except Exception as e:
    logger.error(str(e))  # "KeyError: 'name'" — useless without context

# ✅ Catching with full context
except Exception as e:
    logger.error("order.processing_failed",
        order_id=order.id, step="enrichment",
        error_type=type(e).__name__, error=str(e),
        exc_info=True  # Includes stack trace
    )
```

---

**Next:** [Chapter 6 — Debugging Production Issues](06-production-debugging.md)
