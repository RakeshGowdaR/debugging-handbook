# Debugging Checklist

Use this step-by-step when you encounter any bug. Print it. Tape it to your monitor.

---

## Phase 1: Understand the Bug (5 min)

- [ ] **What is the expected behavior?**
- [ ] **What is the actual behavior?**
- [ ] **What is the exact error message?** (Copy it, don't paraphrase)
- [ ] **When did it start happening?** (After a deploy? After a data change? Random?)
- [ ] **Who is affected?** (All users? One user? One browser? One region?)

## Phase 2: Reproduce (10 min)

- [ ] **Can you reproduce it locally?**
- [ ] If not, what's different? (Environment, data, config, timing)
- [ ] **What are the minimal steps to trigger it?**
- [ ] **Can you write a failing test?**

## Phase 3: Gather Evidence (10 min)

- [ ] **Check logs** — Search by user ID, request ID, timestamp
- [ ] **Check recent changes** — `git log --since="2 days ago"`, deploy history
- [ ] **Check monitoring** — Error rates, latency, CPU/memory, disk
- [ ] **Check dependencies** — Database, cache, external APIs, queues

## Phase 4: Form & Test Hypotheses (15 min)

- [ ] **Write down your hypothesis** (forces clarity)
- [ ] **What would confirm it?** (A log entry, a query result, a specific behavior)
- [ ] **What would disprove it?** (If X is the cause, then Y should also be true)
- [ ] **Test it** — Change ONE thing and observe
- [ ] If disproved → form a new hypothesis, repeat

## Phase 5: Fix & Verify (15 min)

- [ ] **Implement the smallest fix** that addresses the root cause
- [ ] **Verify the failing test now passes**
- [ ] **Check for similar bugs** elsewhere in the codebase
- [ ] **Add logging / monitoring** to catch this class of bug in the future
- [ ] **Document** — What was the bug? Root cause? How was it found? How was it fixed?

## If You're Stuck After 30 Minutes

- [ ] Take a 10-minute break (seriously)
- [ ] Explain the problem to someone (rubber duck debugging)
- [ ] List every assumption you've made → verify each one
- [ ] Read the code line by line (not what you think it says — what it actually says)
- [ ] Check: is the bug where you think it is, or one layer deeper?

---

## Red Flags That Suggest Specific Bug Types

| You Notice... | Investigate... |
|--------------|----------------|
| "Works on my machine" | Environment, config, data differences |
| Works first time, fails later | Mutable state, connection leaks, caching |
| Fails intermittently | Race condition, timeout, resource exhaustion |
| Wrong numbers | Floating point, off-by-one, integer overflow |
| Garbled text | Encoding (UTF-8 vs ASCII vs Latin-1) |
| Memory keeps growing | Memory leak, unbounded cache, event listeners |
| Suddenly slow | N+1 queries, missing index, large payload, GC pressure |
