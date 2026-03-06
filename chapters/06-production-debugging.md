# Chapter 6: Debugging Production Issues

## You Can't Attach a Debugger to Production

In development, you set breakpoints and step through code. In production, you need different tools. Here's your toolkit for debugging live systems without bringing them down.

## The First 5 Minutes

When something breaks in production, resist the urge to start reading code. Follow this order:

```
1. What's the impact? (All users? Some users? One user?)
2. When did it start? (Check deploy history, cron jobs, config changes)
3. What changed? (New deployment? Database migration? Dependency update?)
4. Check dashboards (Error rate, latency, CPU, memory, disk)
5. Check logs (Filter by time range + error level)
```

80% of production issues are caused by something that changed recently. If you deployed 30 minutes ago and errors started 30 minutes ago — rollback first, investigate later.

## Technique 1: Log-Based Debugging

Your first and best tool. If your logging is solid (see Chapter 5), you can trace almost any issue.

```bash
# Find all errors in the last hour
grep "ERROR" /var/log/app.log | tail -100

# Search by user ID
grep "user_id=USR-892" /var/log/app.log

# Search by correlation ID (trace a full request)
grep "corr_id=abc-123" /var/log/*.log

# Count errors by type
grep "ERROR" /var/log/app.log | awk '{print $NF}' | sort | uniq -c | sort -rn

# Watch logs in real-time
tail -f /var/log/app.log | grep "ERROR"
```

For structured logs (JSON), use `jq`:

```bash
# Find slow requests
cat app.log | jq 'select(.latency_ms > 5000)'

# Count errors by endpoint
cat app.log | jq 'select(.level == "ERROR") | .path' | sort | uniq -c | sort -rn
```

## Technique 2: Observability Triad

### Metrics (What's happening?)

Metrics tell you the symptoms. Dashboards should show:

```
RED method for services:
  Rate    → requests per second (is traffic normal?)
  Errors  → error rate / percentage (is it increasing?)
  Duration → response time / latency (is it getting slower?)

USE method for resources:
  Utilization → CPU %, memory %, disk %
  Saturation  → queue depth, thread pool usage
  Errors      → hardware errors, OOM kills
```

### Logs (Why is it happening?)

Logs give you the details. Filter by time range of the anomaly in metrics, then search for errors.

### Traces (Where in the system?)

Distributed traces show you the full journey of a request across services:

```
[API Gateway] 230ms total
  └─ [Auth Service] 15ms ✅
  └─ [Order Service] 200ms ⚠️ SLOW
       └─ [Database Query] 180ms ❌ THIS IS THE BOTTLENECK
  └─ [Email Service] 12ms ✅
```

Tools: Jaeger, Zipkin, Datadog APM, AWS X-Ray.

## Technique 3: Feature Flags as Debug Tools

```python
# Increase logging for a specific user without redeploying
if feature_flags.is_enabled("debug_logging", user_id=user.id):
    logger.setLevel(DEBUG)
    logger.debug("Full request context", extra={
        "headers": dict(request.headers),
        "body": request.body,
        "session": session.data,
    })
```

This lets you get verbose logs for one specific user experiencing a bug without flooding your log storage.

## Technique 4: Database Query Analysis

Slow queries are the #1 cause of production performance issues.

```sql
-- PostgreSQL: find slow queries
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- MySQL: enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- queries over 1 second

-- Check for missing indexes
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 'USR-892';
-- If you see "Seq Scan" on a large table → missing index
```

## Technique 5: Safely Debugging Live Traffic

### Canary Testing
Route 1% of traffic to a debug build with extra logging:

```
Load Balancer
  ├── 99% → Production servers
  └── 1%  → Canary server (extra logging, profiling enabled)
```

### Shadow Traffic (Dark Launching)
Copy production traffic to a test environment without affecting users:

```
Request → Production Server → Response to user
              ↓ (copy)
         Test Server → Results logged but discarded
```

### Replay Suspicious Requests
Save and replay the exact request that caused an error:

```bash
# Save from logs
curl -X POST https://api.example.com/orders \
  -H "Content-Type: application/json" \
  -H "X-Debug: true" \
  -d '{"user_id": "USR-892", "items": [...]}'
```

## Technique 6: Process of Elimination

When you can't find the bug directly, eliminate possibilities:

```
Is it a code bug?
  → Does rolling back the last deploy fix it? Yes → dig into that diff.
  → No → it's not the code.

Is it a data issue?
  → Does it affect all users or specific ones? Specific → check their data.
  → Does it work with test data? Yes → something about production data is different.

Is it an infrastructure issue?
  → Are other services on the same host affected? Yes → check host health.
  → Did cloud provider report an incident? Check status page.

Is it a dependency issue?
  → Is the external API responding? Check their status page.
  → Are timeouts increasing? Yes → the dependency is slow/down.
```

## The Rollback Decision

**When to rollback immediately:**
- Error rate spiked right after a deploy
- Data corruption is occurring
- Users are unable to complete critical actions (checkout, login)

**When to investigate first:**
- Error rate is slightly elevated but stable
- Issue affects a small percentage of users
- You have a strong hypothesis and can verify quickly

**The golden rule:** If you're debating whether to rollback, rollback. You can always redeploy after fixing the issue. You can't undo corrupted data or lost revenue.

## Post-Incident: The Blameless Postmortem

After the fire is out, document:

```
1. Timeline — What happened and when (with timestamps)
2. Impact — Who was affected, for how long, what was lost
3. Root cause — What actually broke and why
4. Detection — How was it discovered? How can we detect it faster?
5. Resolution — What fixed it?
6. Prevention — What changes prevent this class of issue?
7. Action items — Specific, assigned tasks with deadlines
```

The goal isn't blame — it's making the system more resilient.

---

**Next:** [Chapter 7 — Memory Leaks & Performance](07-memory-and-performance.md)