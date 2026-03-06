# Chapter 8: Debugging Distributed Systems

## Why Distributed Debugging Is Hard

In a monolith, a bug happens in one place. In a distributed system, a single user request might touch 5 services, 3 databases, and 2 message queues. The bug could be in any of them — or in the space between them.

```
User request → API Gateway → Auth Service → Order Service → Payment Service
                                                ↓
                                          Inventory Service → Message Queue → Email Service
```

When the order fails, which service caused it? Was it a timeout? A data inconsistency? A race condition between services?

## The Distributed Debugging Toolkit

### 1. Distributed Tracing

A trace follows a single request across all services. Every service adds a span with timing and metadata.

```
Trace ID: abc-123
├── [API Gateway] 450ms
│   ├── [Auth Service] 15ms → 200 OK
│   └── [Order Service] 420ms → 500 ERROR
│       ├── [Database Query] 5ms → OK
│       ├── [Payment Service] 400ms → TIMEOUT ← ROOT CAUSE
│       └── [Inventory Service] — never called (previous step failed)
```

Implementation: pass a trace ID through all services via headers.

```python
# Middleware that propagates trace context
@app.middleware("http")
async def tracing_middleware(request, call_next):
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    span_id = str(uuid.uuid4())
    
    # Attach to all outgoing requests
    with trace_context(trace_id=trace_id, span_id=span_id):
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
    return response
```

Tools: OpenTelemetry, Jaeger, Zipkin, Datadog APM, AWS X-Ray.

### 2. Correlation IDs

Even without full tracing, a correlation ID links logs across services:

```
# Service A
INFO  corr_id=xyz-789 service=api-gateway   "POST /orders received"

# Service B
INFO  corr_id=xyz-789 service=order-service "Creating order ORD-5521"

# Service C
ERROR corr_id=xyz-789 service=payment-svc   "Charge failed: card_declined"
```

Search by `corr_id=xyz-789` across all service logs and you see the full story.

### 3. Health Checks and Dependency Mapping

```
GET /health → {"status": "healthy", "dependencies": {
    "database": "connected",
    "redis": "connected",
    "payment-api": "timeout",      ← problem is here
    "email-service": "connected"
}}
```

When something is wrong, check all downstream dependencies first.

## Common Distributed System Bugs

### Timeout Cascades

```
Service A calls Service B (timeout: 30s)
Service B calls Service C (timeout: 30s)
Service C is slow (takes 25s)

Result: A waits 30s for B, which waits 30s for C
        Total: 55s+ of waiting. Thread pools exhaust.
        Everything appears down.

Fix: Set decreasing timeouts
  A → B: 10s
  B → C: 5s
  If C is slow, B fails fast, A fails fast, threads are freed.
```

### Split Brain

```
Network partition splits your cluster:
  Partition A: Nodes 1, 2 think Node 3 is dead → elect new leader
  Partition B: Node 3 thinks Nodes 1, 2 are dead → remains leader
  
  Two leaders accepting writes → data divergence → corruption

Fix: Quorum-based decisions (majority required)
  3 nodes: need 2 to agree (Node 3 alone can't form quorum → stops accepting writes)
```

### Message Ordering Issues

```
Service A publishes: "Create User" then "Update User Email"
Message queue delivers: "Update User Email" then "Create User"

Result: Update fails because user doesn't exist yet.

Fixes:
  - Use a message queue that guarantees ordering (Kafka partitions)
  - Make handlers idempotent (can process in any order)
  - Include version numbers in messages
```

### Idempotency Failures

```
Client sends payment request → network timeout → client retries
Server processed the first request but client didn't get the response.
Second request creates a DUPLICATE charge.

Fix: Idempotency keys
  Client generates a unique key per operation.
  Server checks: "Have I seen this key before?"
    Yes → return the previous result
    No  → process and store the result
```

```python
@app.post("/payments")
async def create_payment(request):
    idempotency_key = request.headers.get("Idempotency-Key")
    
    # Check if we already processed this
    existing = await redis.get(f"idem:{idempotency_key}")
    if existing:
        return json.loads(existing)  # Return previous result
    
    # Process the payment
    result = await payment_service.charge(request.body)
    
    # Store result for idempotency (TTL: 24 hours)
    await redis.setex(f"idem:{idempotency_key}", 86400, json.dumps(result))
    
    return result
```

### Data Inconsistency Across Services

```
Order Service: order.status = "PAID"
Payment Service: payment.status = "FAILED"

How? Order service updated its DB, then payment service call failed,
but the order DB wasn't rolled back.

Fixes:
  - Saga pattern: each service has a compensating action
    If payment fails → Order Service runs "cancel order" compensation
  - Outbox pattern: write event to DB in same transaction as state change
    A background process publishes the event to other services
```

## Debugging Strategy for Distributed Systems

```
1. Start with the symptom
   "Users get 500 errors on checkout"

2. Find the failing service
   Check API gateway logs → Order Service returns 500

3. Trace the request
   corr_id=abc → Order Service called Payment Service → timeout after 10s

4. Check the downstream dependency
   Payment Service health check → external payment API is responding in 15s (normally 200ms)

5. Identify the root cause
   Payment provider is having an outage (check their status page)

6. Apply immediate fix
   Enable fallback: queue the payment for retry, show "payment processing" to user

7. Apply permanent fix
   Add circuit breaker on payment calls, add fallback queue, add alerting on payment latency
```

---

**Previous:** [Chapter 7 — Memory Leaks & Performance](07-memory-and-performance.md)
**Next:** [Chapter 9 — Common Bug Patterns](09-common-bug-patterns.md)
