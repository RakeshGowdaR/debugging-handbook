# Chapter 3: Binary Search Debugging

## Find Any Bug in O(log n) Steps

Binary search isn't just for sorted arrays. It's a universal strategy for narrowing down bugs. The idea: instead of checking every line, every commit, or every config — cut the search space in half with each step.

## Git Bisect: Find the Commit That Broke Things

If something worked before and doesn't now, `git bisect` will find the exact commit that caused it.

```bash
# Start bisecting
git bisect start

# Mark the current (broken) state as bad
git bisect bad

# Mark a known good commit (it worked 2 weeks ago)
git bisect good abc123f

# Git checks out a commit halfway between good and bad
# Test it, then tell git:
git bisect good   # if this commit works fine
git bisect bad    # if this commit is broken

# Repeat 5-10 times. Git will identify the exact breaking commit.
# With 1000 commits, you'll find it in ~10 steps.

# When done:
git bisect reset
```

### Automate It

If you have a test that catches the bug:

```bash
git bisect start HEAD abc123f
git bisect run python -m pytest tests/test_checkout.py::test_coupon
# Git runs the test automatically at each step and finds the breaking commit
```

## Binary Search in Code

When you have a long function and don't know which part is broken:

```python
def process_order(order):
    validated = validate(order)
    enriched = enrich(validated)
    priced = calculate_pricing(enriched)
    taxed = apply_tax(priced)
    discounted = apply_discounts(taxed)
    finalized = finalize(discounted)
    return finalized
```

Instead of checking every step, add a checkpoint in the middle:

```python
def process_order(order):
    validated = validate(order)
    enriched = enrich(validated)
    priced = calculate_pricing(enriched)

    print(f"DEBUG MIDPOINT: {priced}")  # Is the data correct here?

    taxed = apply_tax(priced)
    discounted = apply_discounts(taxed)
    finalized = finalize(discounted)
    return finalized
```

**If the midpoint looks correct** → Bug is in the second half (apply_tax, apply_discounts, or finalize).

**If the midpoint looks wrong** → Bug is in the first half (validate, enrich, or calculate_pricing).

Now add a checkpoint in the middle of the remaining half. In 2-3 steps, you've found the exact function.

## Binary Search in Configs / Inputs

### Scenario: App crashes with a specific data file

```
1000-line CSV causes crash.
→ Does the first 500 lines crash? No.
→ Does lines 500-1000 crash? Yes.
→ Does lines 500-750 crash? No.
→ Does lines 750-1000 crash? Yes.
→ Does lines 750-875 crash? Yes.
→ ...
→ Line 823 has an emoji in the address field. Parser chokes on UTF-8.
```

### Scenario: App fails with certain environment variables

```
20 environment variables set.
→ Comment out the last 10. Still fails? Bug is in the first 10.
→ Comment out 5 of those 10. Still fails? Bug is in those 5.
→ ...
→ DATABASE_URL has a special character in the password that needs escaping.
```

## When NOT to Use Binary Search

Binary search works when the problem is deterministic and the search space is ordered. It's less useful for:

- **Intermittent bugs** — The bug might not appear at the midpoint even if the cause is there
- **Multiple interacting causes** — Two changes together cause the bug, neither alone does
- **Performance regressions** — Gradual degradation across many commits (though bisect can still help if you define a threshold)

For these, use logging, tracing, and the techniques in later chapters.

---

**Next:** [Chapter 4 — Reading Error Messages](04-reading-error-messages.md)
