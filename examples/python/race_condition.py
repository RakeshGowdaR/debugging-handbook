"""
Bug Pattern: Race Condition
Difficulty: Intermediate
Language: Python

THE SCENARIO:
You're building a ticket booking system. Multiple users can browse
available seats, but when two users try to book the same seat
simultaneously, both succeed — and you've double-booked.
"""

import threading
import time

# ============================================================
# THE BUGGY CODE
# ============================================================

class TicketSystem:
    def __init__(self):
        self.available_seats = {"A1": True, "A2": True, "A3": True}
        self.bookings = []
    
    def book_seat(self, user, seat):
        """Book a seat for a user."""
        # Check if seat is available
        if self.available_seats.get(seat):
            # Simulate processing delay (payment, validation, etc.)
            time.sleep(0.1)
            
            # Mark as booked
            self.available_seats[seat] = False
            self.bookings.append({"user": user, "seat": seat})
            print(f"  ✅ {user} booked seat {seat}")
            return True
        else:
            print(f"  ❌ {user} failed — seat {seat} already taken")
            return False


# Simulate two users trying to book the same seat at the same time
print("--- BUGGY VERSION: Race Condition ---")
system = TicketSystem()

threads = [
    threading.Thread(target=system.book_seat, args=("Alice", "A1")),
    threading.Thread(target=system.book_seat, args=("Bob", "A1")),
]

for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"  Bookings: {system.bookings}")
print(f"  DOUBLE BOOKED! Both users got seat A1." if len(system.bookings) > 1 else "  Got lucky this time.")


# ============================================================
# THE FIX
# ============================================================

class TicketSystemFixed:
    def __init__(self):
        self.available_seats = {"A1": True, "A2": True, "A3": True}
        self.bookings = []
        self.lock = threading.Lock()  # Mutex to protect shared state
    
    def book_seat(self, user, seat):
        """Book a seat for a user — thread-safe."""
        with self.lock:  # Only one thread can execute this block at a time
            if self.available_seats.get(seat):
                time.sleep(0.1)  # Processing delay
                self.available_seats[seat] = False
                self.bookings.append({"user": user, "seat": seat})
                print(f"  ✅ {user} booked seat {seat}")
                return True
            else:
                print(f"  ❌ {user} failed — seat {seat} already taken")
                return False


print("\n--- FIXED VERSION: With Lock ---")
system_fixed = TicketSystemFixed()

threads = [
    threading.Thread(target=system_fixed.book_seat, args=("Alice", "A1")),
    threading.Thread(target=system_fixed.book_seat, args=("Bob", "A1")),
]

for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"  Bookings: {system_fixed.bookings}")
print(f"  Correctly handled — only one booking.")


# ============================================================
# THE LESSON
# ============================================================
"""
KEY TAKEAWAYS:

1. The "check-then-act" pattern is ALWAYS a race condition:
     if resource_available:     ← Thread A checks (True)
         use_resource()         ← Thread B checks (True) before A acts
                                ← Both proceed = bug

2. In production, this happens with:
   - Database reads followed by writes (use SELECT FOR UPDATE)
   - Cache checks followed by expensive computation (use distributed locks)
   - File existence checks followed by file creation (use atomic operations)

3. The fix is to make check-and-act ATOMIC:
   - Threading: use locks/mutexes
   - Database: use transactions with row-level locking
   - Distributed: use Redis SETNX, database advisory locks, or Zookeeper

4. Race conditions are hard to reproduce because they depend on timing.
   If a bug is intermittent, suspect a race condition first.
"""
