# Chapter 1: The Debugging Mindset

## Think Like a Detective, Not a Guesser

The biggest difference between a junior and senior developer debugging isn't knowledge — it's approach. Juniors change random things and hope. Seniors follow a systematic process.

## The Scientific Method for Bugs

Every debugging session should follow this loop:

```
1. Observe    → What exactly is happening?
2. Hypothesize → What could cause this behavior?
3. Predict    → If my hypothesis is right, what else should be true?
4. Test       → Run an experiment to confirm or eliminate
5. Repeat     → Narrow down until you find the root cause
```

### Example: API Returns 500 Error

❌ **The guessing approach:**
> "Hmm, 500 error. Maybe the database is down? Let me restart it. Still broken. Maybe it's the cache? Let me clear it. Still broken. Maybe it's the deployment?"

✅ **The systematic approach:**
> "500 error. Let me check the logs — I see a NullPointerException in UserService.java line 47. The `user.getAddress()` call is null. When is address null? When users sign up via OAuth, we skip the address step. This endpoint assumes all users have addresses."

## The Golden Rules

### Rule 1: Understand What Should Happen Before Diagnosing What Went Wrong

If you don't know the expected behavior, you can't identify the bug. Before debugging:
- Read the spec / ticket / requirements
- Understand the happy path
- Know what the correct output looks like

### Rule 2: Change One Thing at a Time

When you change multiple things simultaneously, you can't tell which change fixed the bug. Even worse — you might introduce a new bug while fixing the old one.

### Rule 3: Don't Trust Anything — Verify

"The config is correct" — did you actually check?
"That service is running" — did you ping it?
"The data is there" — did you query it?

The number of times the bug is in the thing you assumed was fine is humbling.

### Rule 4: Rubber Duck Debugging Works

Explaining the problem out loud (to a duck, a colleague, or yourself) forces you to articulate your assumptions. The bug often hides in the gap between what you think the code does and what it actually does.

```
What I think happens:
  1. User clicks submit
  2. Form data is validated
  3. API call is made
  4. Response is shown

What actually happens:
  1. User clicks submit
  2. Form data is validated
  3. API call is made
  4. ← Component re-renders here due to state change
  5. A SECOND API call is made
  6. First response is shown, then immediately overwritten by second
```

### Rule 5: The Bug Is Almost Never Where You Think It Is

Your first instinct about where the bug is — ignore it. Or at least, verify it before going down that rabbit hole. The bug that looks like a frontend issue is often a backend issue. The "database problem" is often a query problem. The "network issue" is often a DNS issue.

## When You're Stuck

If you've been debugging for more than 30 minutes without progress:

1. **Take a break.** Seriously. Walk away for 10 minutes.
2. **Explain the problem to someone else.** You'll often find the answer mid-sentence.
3. **Question your assumptions.** List every assumption you've made and verify each one.
4. **Read the code, don't skim it.** Read every line in the path. Not what you think it says — what it actually says.
5. **Check what changed recently.** `git log`, deployment history, config changes, dependency updates.

---

**Next:** [Chapter 2 — Reproducing Bugs](02-reproducing-bugs.md)
