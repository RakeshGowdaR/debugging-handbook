# Chapter 2: Reproducing Bugs

## If You Can't Reproduce It, You Can't Fix It

This is the most important and most skipped step in debugging. Developers jump straight to reading code and guessing. Resist that urge. Reproducing the bug first gives you a reliable feedback loop — you'll know immediately when your fix works.

## The Reproduction Spectrum

```
Easy                                              Hard
|-------|---------|------------|------------|---------|
Always  | Usually | Sometimes  | Rarely     | "Works
happens | happens | happens    | happens    | on my
                                             machine"
```

The harder a bug is to reproduce, the more likely it involves:
- Timing / race conditions
- Environment-specific configuration
- Specific data patterns
- State that accumulates over time

## Step-by-Step Reproduction Strategy

### 1. Get the Exact Steps

Don't accept "it's broken." Get specifics:

```
Bad:  "The checkout is broken."
Good: "When I add 3 items to cart, apply coupon SAVE20,
       then click checkout with a saved Visa card,
       I get a blank page."
```

### 2. Match the Environment

The most common reason for "works on my machine":

| Factor | What to Check |
|--------|---------------|
| OS / Browser | Same OS version? Same browser? Mobile vs desktop? |
| Data | Same user account? Same test data? Empty vs populated DB? |
| Config | Same environment variables? Same feature flags? |
| State | Fresh install vs long-running? Logged in vs logged out? |
| Network | VPN? Proxy? Firewall rules? Slow connection? |
| Time | Time zone? Daylight saving? End of month? |

### 3. Minimize the Reproduction

Once you can reproduce, strip away everything unnecessary:

```
Original: "Log in as admin, go to settings, change theme to dark,
           go to dashboard, filter by date range, export to CSV,
           then try to re-import — it fails."

Minimized: "Import any CSV with a date column where dates
            are in DD/MM/YYYY format — it fails.
            (The app expects MM/DD/YYYY.)"
```

A minimal reproduction:
- Makes the bug obvious
- Eliminates red herrings
- Often reveals the root cause before you read any code

### 4. Write a Failing Test

The best reproduction is an automated one:

```python
# This test should pass but doesn't — that's our bug
def test_coupon_applies_to_discounted_items():
    cart = Cart()
    cart.add(Item("Shirt", price=50.00, discount=0.10))  # $45 after 10% off
    cart.apply_coupon("SAVE20")  # 20% off total

    # Expected: 20% off $45 = $36
    # Actual:   20% off $50 = $40 (coupon ignores item discount)
    assert cart.total == 36.00
```

## Dealing with Hard-to-Reproduce Bugs

### Heisenbugs (Disappear When You Observe Them)

These are usually timing-related. Adding logging or breakpoints changes the timing enough to hide the bug.

**Strategy:** Use non-invasive observation — check logs after the fact, use recording tools, add lightweight counters.

### Environment-Specific Bugs

**Strategy:** Match the environment exactly. Use Docker, VMs, or feature flags to replicate the exact conditions.

```bash
# Reproduce with the exact same environment
docker run -e DB_HOST=prod-replica -e FEATURE_NEW_CHECKOUT=true \
  --memory=512m myapp:v2.3.1
```

### Data-Dependent Bugs

**Strategy:** Get the actual data (anonymized if needed). Don't assume your test data triggers the same paths.

```sql
-- Find the exact records that cause issues
SELECT * FROM orders
WHERE created_at BETWEEN '2024-01-01' AND '2024-01-02'
  AND status = 'FAILED'
  AND error_message LIKE '%null%';
```

### Time-Dependent Bugs

Some bugs only appear at specific times — end of month, midnight, DST transitions, leap years.

```python
# Instead of waiting for midnight, mock the clock
from unittest.mock import patch
from datetime import datetime

@patch('myapp.utils.now')
def test_midnight_rollover(mock_now):
    mock_now.return_value = datetime(2024, 12, 31, 23, 59, 59)
    result = process_daily_report()
    # Bug: report date uses "tomorrow" which crosses into next year
    assert result.year == 2024  # FAILS — returns 2025
```

---

**Next:** [Chapter 3 — Binary Search Debugging](03-binary-search-debugging.md)
