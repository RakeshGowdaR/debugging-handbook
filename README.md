# 🐛 Debugging Handbook

A practical, no-fluff guide to debugging real software problems. Every technique here comes from real production incidents — not textbook theory.

> **"Debugging is twice as hard as writing the code in the first place."** — Brian Kernighan

---

## Why This Exists

Most debugging guides teach you how to use a debugger. This one teaches you **how to think** when things break. Whether it's a 3 AM production outage or a bug that only appears on Tuesdays, the mental models here will help you find the root cause faster.

---

## Table of Contents

### Chapters

| # | Chapter | What You'll Learn |
|---|---------|-------------------|
| 1 | [The Debugging Mindset](chapters/01-debugging-mindset.md) | How to approach bugs systematically instead of guessing |
| 2 | [Reproducing Bugs](chapters/02-reproducing-bugs.md) | The most critical (and most skipped) step |
| 3 | [Binary Search Debugging](chapters/03-binary-search-debugging.md) | Halving your search space to find bugs in minutes |
| 4 | [Reading Error Messages](chapters/04-reading-error-messages.md) | What error messages actually tell you (and what they hide) |
| 5 | [Logging That Actually Helps](chapters/05-logging-strategies.md) | Structured logging, correlation IDs, and log levels done right |
| 6 | [Debugging Production Issues](chapters/06-production-debugging.md) | Safe techniques when you can't attach a debugger |
| 7 | [Memory Leaks & Performance](chapters/07-memory-and-performance.md) | Finding leaks, profiling hotspots, and reading flame graphs |
| 8 | [Debugging Distributed Systems](chapters/08-distributed-systems.md) | Tracing requests across services, race conditions, network failures |
| 9 | [Common Bug Patterns](chapters/09-common-bug-patterns.md) | Off-by-one, null references, race conditions, and 20+ more |

### Quick References

| Cheatsheet | Description |
|------------|-------------|
| [Debugging Checklist](cheatsheets/debugging-checklist.md) | Step-by-step checklist for any bug |
| [Language-Specific Tips](cheatsheets/language-specific.md) | Python, JavaScript, Java, Go — common gotchas per language |
| [Tool Cheatsheet](cheatsheets/tools-cheatsheet.md) | Quick reference for gdb, strace, tcpdump, Chrome DevTools, etc. |

### Code Examples

Real buggy code with walkthroughs showing how to find and fix each issue.

```
examples/
├── python/
│   ├── null_reference_bug.py        # The classic NoneType error
│   ├── race_condition.py            # Threading bug with shared state
│   ├── memory_leak.py               # Subtle leak with growing cache
│   └── silent_exception.py          # Bug hidden by bare except
├── javascript/
│   ├── async_debugging.js           # Promise chain losing errors
│   ├── closure_trap.js              # The infamous loop variable bug
│   └── type_coercion_bug.js         # When '1' + 1 = '11'
└── java/
    ├── concurrent_modification.java # Modifying collections during iteration
    └── equals_hashcode_bug.java     # Why HashMap "loses" your objects
```

---

## How to Use This Repo

**If you're fighting a bug right now** → Start with the [Debugging Checklist](cheatsheets/debugging-checklist.md)

**If you want to get better at debugging** → Read the chapters in order, then try to find the bugs in `examples/` without looking at the solutions

**If you're preparing for interviews** → Chapter 9 (Common Bug Patterns) covers the most frequently asked debugging scenarios

---

## Contributing

Found a bug pattern that should be here? Have a war story worth sharing? Contributions are welcome!

1. Fork this repo
2. Add your content (follow the existing chapter format)
3. Include a real-world example if possible
4. Submit a PR

Please keep examples practical and production-relevant. We're not looking for contrived puzzles — we want the kind of bugs that make senior engineers sweat.

---

## License

MIT — use this however you want. If it helps you debug faster, that's all that matters.
