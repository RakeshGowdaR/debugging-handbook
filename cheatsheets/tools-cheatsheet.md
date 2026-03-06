# Debugging Tools Cheatsheet

Quick reference for essential debugging tools. Keep this bookmarked.

---

## Command Line

### grep — Search through text

```bash
grep "ERROR" app.log                       # Find lines with "ERROR"
grep -i "error" app.log                    # Case-insensitive
grep -n "error" app.log                    # Show line numbers
grep -r "TODO" src/                        # Recursive search in directory
grep -A 3 "ERROR" app.log                  # Show 3 lines After match
grep -B 2 "ERROR" app.log                  # Show 2 lines Before match
grep -C 2 "ERROR" app.log                  # Show 2 lines of Context (before + after)
grep -c "ERROR" app.log                    # Count matches
grep -v "DEBUG" app.log                    # Invert: show lines WITHOUT "DEBUG"
grep "error\|warning\|fatal" app.log       # Multiple patterns (OR)
```

### curl — Test APIs

```bash
curl https://api.example.com/users                         # GET
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'                                   # POST with JSON
curl -v https://api.example.com/health                     # Verbose (see headers)
curl -o /dev/null -s -w "%{http_code} %{time_total}s\n" \
  https://api.example.com/health                           # Just status + timing
curl -H "Authorization: Bearer TOKEN" https://api.example.com/me  # With auth
```

### Network Debugging

```bash
# DNS lookup
dig example.com
nslookup example.com

# Check if a port is open
nc -zv hostname 5432              # Is PostgreSQL reachable?
telnet hostname 6379              # Is Redis reachable?

# See active connections
ss -tuln                          # Listening ports
ss -tunp                          # Active connections with process
netstat -tlnp                     # Same (older systems)

# Trace network path
traceroute example.com
mtr example.com                   # Interactive traceroute

# Capture packets
tcpdump -i eth0 port 80           # HTTP traffic
tcpdump -i eth0 host 10.0.0.5    # Traffic to/from specific host
tcpdump -i any -w capture.pcap    # Save to file (open in Wireshark)
```

### Process Debugging

```bash
# Find processes
ps aux | grep python               # Find Python processes
pgrep -f "my_app"                  # Find by name pattern
top -p <pid>                       # Monitor specific process
htop                               # Interactive process monitor

# System calls (what is the process doing?)
strace -p <pid>                    # Trace system calls (Linux)
strace -p <pid> -e trace=network   # Only network calls
strace -c -p <pid>                 # Summary of syscall time

# Open files and connections
lsof -p <pid>                      # All open files/sockets
lsof -i :8080                      # What's using port 8080?

# Disk and memory
df -h                              # Disk usage
du -sh /var/log/*                  # Directory sizes
free -h                            # Memory usage
```

### Docker Debugging

```bash
docker logs <container> --tail 100          # Last 100 log lines
docker logs <container> --since 1h          # Logs from last hour
docker logs <container> -f                  # Follow logs (live)
docker exec -it <container> bash            # Shell into container
docker inspect <container>                  # Full container config
docker stats                                # CPU/memory per container
docker top <container>                      # Processes in container
docker network inspect bridge               # Network configuration
docker system df                            # Disk usage by Docker
```

### Git Debugging

```bash
git log --oneline --since="3 days ago"      # Recent commits
git log --all --oneline -- path/to/file     # History of specific file
git diff HEAD~5 -- path/to/file             # Changes in last 5 commits
git blame path/to/file                      # Who changed each line
git bisect start                            # Binary search for breaking commit
git stash list                              # Check for stashed changes
git reflog                                  # Recover "lost" commits
```

---

## Browser DevTools (Chrome)

### Console

```javascript
// Beyond console.log
console.table(data)              // Display as table
console.dir(element)             // DOM element properties
console.time('op'); /* ... */ console.timeEnd('op')  // Timing
copy(object)                     // Copy object to clipboard
$('selector')                    // querySelector shortcut
$$('selector')                   // querySelectorAll shortcut
$0                               // Currently selected element
$_                               // Last evaluated expression
```

### Network Tab
- Filter by XHR to see API calls only
- Right-click → Copy as cURL → replay in terminal
- Throttle to simulate slow connections
- Check "Preserve log" to keep logs across page navigation

### Performance Tab
- Record → perform action → stop
- Look for: long tasks (>50ms), layout thrashing, excessive re-renders
- Flame chart: wide bars = slow functions

### Memory Tab
- Heap snapshot: compare two snapshots to find leaks
- Allocation timeline: see what's being allocated over time

---

## Database

### PostgreSQL

```sql
-- Active queries (find long-running)
SELECT pid, now() - pg_stat_activity.query_start AS duration,
       query, state
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Kill a stuck query
SELECT pg_cancel_backend(pid);     -- Graceful
SELECT pg_terminate_backend(pid);  -- Force

-- Table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Missing indexes (sequential scans on large tables)
SELECT relname, seq_scan, seq_tup_read, idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > 1000
ORDER BY seq_tup_read DESC;
```

### Redis

```bash
redis-cli INFO memory              # Memory usage
redis-cli INFO keyspace            # Key counts per DB
redis-cli MONITOR                  # Watch all commands (careful in prod!)
redis-cli SLOWLOG GET 10           # Last 10 slow commands
redis-cli --bigkeys                # Find largest keys
redis-cli DEBUG SLEEP 0            # Check if Redis is responsive
```
