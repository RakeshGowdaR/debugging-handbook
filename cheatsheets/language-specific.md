# Language-Specific Debugging Tips

Quick reference for common gotchas and debugging techniques per language.

---

## Python

### Common Gotchas
- **Mutable default arguments** — `def f(items=[])` shares the list across calls. Use `None`.
- **Late binding closures** — `lambda: i` in a loop captures the variable, not the value.
- **Integer caching** — `a = 256; b = 256; a is b` → True. `a = 257; b = 257; a is b` → False. Use `==` not `is` for value comparison.
- **String is not bytes** — `"hello".encode()` → bytes. Mixing them causes `TypeError`.
- **GIL** — Threads don't run Python code in parallel. Use `multiprocessing` for CPU-bound work.
- **Silent `except`** — Bare `except:` catches `SystemExit` and `KeyboardInterrupt`. Always catch specific exceptions.

### Debugging Tools
```bash
# Interactive debugger
python -m pdb script.py          # Start with debugger
import pdb; pdb.set_trace()      # Breakpoint in code (Python <3.7)
breakpoint()                     # Breakpoint (Python 3.7+)

# pdb commands: n(ext), s(tep), c(ontinue), p(rint), l(ist), w(here), q(uit)

# Memory profiling
python -m tracemalloc script.py
python -m memory_profiler script.py  # pip install memory_profiler

# CPU profiling
python -m cProfile -s cumulative script.py

# Type checking (catch bugs before runtime)
mypy script.py                   # pip install mypy
```

---

## JavaScript / TypeScript

### Common Gotchas
- **`==` vs `===`** — `"1" == 1` is `true`. Always use `===`.
- **`typeof null === "object"`** — Historical bug, will never be fixed.
- **`this` context** — Arrow functions inherit `this`, regular functions don't. `class` methods need binding or arrow syntax.
- **Floating point** — `0.1 + 0.2 !== 0.3`. Use `Math.abs(a - b) < Number.EPSILON` or integers (cents for money).
- **`async` without `await`** — Forgetting `await` returns a Promise object instead of the value.
- **Array `sort()`** — Default sort is lexicographic: `[10, 2, 1].sort()` → `[1, 10, 2]`. Pass a comparator: `.sort((a, b) => a - b)`.

### Debugging Tools
```javascript
// Console methods beyond console.log
console.table(arrayOfObjects)    // Pretty table in console
console.time('label')            // Start timer
console.timeEnd('label')         // End timer, print duration
console.trace()                  // Print stack trace
console.group('label')           // Group related logs
console.assert(condition, msg)   // Log only if assertion fails

// debugger statement
function buggyFunction(data) {
    debugger;  // Pauses here if DevTools is open
    return data.map(x => x.id);
}
```

```
Chrome DevTools tips:
- Sources → Breakpoints → right-click → "Edit condition" for conditional breakpoints
- Network → right-click request → "Copy as cURL" to replay in terminal
- Console → $0 references the currently selected DOM element
- Performance → Record → look for long tasks (>50ms)
```

---

## Java

### Common Gotchas
- **String comparison** — `==` compares references, not content. Use `.equals()`.
- **Integer caching** — `Integer.valueOf(127) == Integer.valueOf(127)` → `true`. `valueOf(128) == valueOf(128)` → `false`. Use `.equals()`.
- **`hashCode`/`equals` contract** — If you override `equals`, you MUST override `hashCode`. Otherwise, `HashMap` and `HashSet` break silently.
- **ConcurrentModificationException** — Can't modify a collection while iterating with for-each. Use `Iterator.remove()` or collect changes separately.
- **Autoboxing NPE** — `Integer x = null; int y = x;` → `NullPointerException` on unboxing.
- **Checked exceptions** — Wrapping in `RuntimeException` hides the real error. Preserve the cause chain.

### Debugging Tools
```bash
# Thread dump (find deadlocks, stuck threads)
jstack <pid>

# Heap dump (find memory leaks)
jmap -dump:live,format=b,file=heap.hprof <pid>

# GC logging
java -Xlog:gc*:file=gc.log -jar app.jar

# Remote debugging
java -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005 -jar app.jar
# Then attach IntelliJ/VS Code debugger to port 5005

# Flight recorder (low-overhead production profiling)
java -XX:StartFlightRecording=duration=60s,filename=recording.jfr -jar app.jar
```

---

## Go

### Common Gotchas
- **Goroutine leaks** — A goroutine blocked on a channel that nobody reads from lives forever. Always ensure channels are drained or use `context.WithCancel`.
- **Nil interface vs nil pointer** — An interface holding a nil pointer is NOT nil: `var p *MyStruct = nil; var i interface{} = p; i == nil` → `false`.
- **Range variable reuse** — `for _, v := range items { go func() { use(v) }() }` — all goroutines see the last value. Capture: `go func(v Item) { use(v) }(v)`.
- **Slice append gotcha** — `append` may or may not create a new backing array. When sharing slices, copy explicitly.
- **Error handling** — Not checking an error return is a bug. Use `errcheck` linter.

### Debugging Tools
```bash
# Built-in profiling
import _ "net/http/pprof"  # Add to your app
go tool pprof http://localhost:6060/debug/pprof/heap     # Memory
go tool pprof http://localhost:6060/debug/pprof/profile   # CPU (30s sample)
go tool pprof http://localhost:6060/debug/pprof/goroutine # Goroutine dump

# Race detector
go run -race main.go       # Detects data races at runtime
go test -race ./...        # Run tests with race detector

# Delve debugger
dlv debug main.go          # Start debugger
dlv attach <pid>           # Attach to running process
```
