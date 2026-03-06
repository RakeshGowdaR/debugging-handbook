/**
 * Bug Pattern: Lost Errors in Promise Chains
 * Difficulty: Intermediate
 * Language: JavaScript
 * 
 * THE SCENARIO:
 * You're building an API that fetches a user, then their orders,
 * then calculates a summary. Sometimes it returns undefined instead
 * of the summary, and no errors appear in the logs.
 */

// ============================================================
// THE BUGGY CODE
// ============================================================

function fetchUser(userId) {
  return new Promise((resolve, reject) => {
    if (userId === "invalid") reject(new Error("User not found"));
    resolve({ id: userId, name: "Alice", tier: "premium" });
  });
}

function fetchOrders(user) {
  return new Promise((resolve) => {
    if (user.tier === "premium") {
      resolve([
        { id: 1, total: 99.99 },
        { id: 2, total: 149.50 },
        { id: 3, total: -20.00 }, // Refund — will cause bug in summary
      ]);
    }
    resolve([]);
  });
}

function calculateSummary(orders) {
  const total = orders.reduce((sum, o) => sum + o.total, 0);
  const avgOrder = total / orders.length; // NaN if orders is empty!
  
  // Bug: this throws for negative totals but nobody catches it
  if (total < 0) throw new Error("Negative total — data integrity issue");

  return { totalSpent: total, averageOrder: avgOrder, orderCount: orders.length };
}


// Bug 1: No .catch() — errors vanish silently
function getUserSummary_buggy(userId) {
  return fetchUser(userId)
    .then(user => fetchOrders(user))
    .then(orders => calculateSummary(orders));
    // ← No .catch()! If anything throws, the error disappears
}


// This silently fails — no error in console, result is undefined
getUserSummary_buggy("invalid")
  .then(summary => {
    console.log("Buggy result:", summary); // Never runs — but no error either
  });

// Bug 2: .catch() that swallows the error
function getUserSummary_swallowed(userId) {
  return fetchUser(userId)
    .then(user => fetchOrders(user))
    .then(orders => calculateSummary(orders))
    .catch(err => {
      console.log("Something went wrong"); // Logs generic message
      // ← Returns undefined! Caller has no idea there was an error
    });
}


// ============================================================
// THE FIX
// ============================================================

// Fix 1: Use async/await with try/catch (clearest approach)
async function getUserSummary_fixed(userId) {
  try {
    const user = await fetchUser(userId);
    const orders = await fetchOrders(user);
    
    if (orders.length === 0) {
      return { totalSpent: 0, averageOrder: 0, orderCount: 0 };
    }
    
    return calculateSummary(orders);
  } catch (error) {
    console.error(`Failed to get summary for user ${userId}:`, error.message);
    throw error; // RE-THROW so the caller knows it failed
  }
}

// Fix 2: If using .then(), always have .catch() that either re-throws or returns a meaningful value
function getUserSummary_fixed_promise(userId) {
  return fetchUser(userId)
    .then(user => fetchOrders(user))
    .then(orders => {
      if (orders.length === 0) {
        return { totalSpent: 0, averageOrder: 0, orderCount: 0 };
      }
      return calculateSummary(orders);
    })
    .catch(err => {
      console.error(`Failed for user ${userId}:`, err.message);
      throw err; // Re-throw — don't swallow!
    });
}


// Demonstration
async function demo() {
  console.log("--- FIXED VERSION ---");
  
  // Valid user
  try {
    const result = await getUserSummary_fixed("user123");
    console.log("Valid user:", result);
  } catch (e) {
    console.log("Error:", e.message);
  }

  // Invalid user — error is properly surfaced
  try {
    const result = await getUserSummary_fixed("invalid");
    console.log("Result:", result);
  } catch (e) {
    console.log("Properly caught:", e.message);
  }
}

demo();


// ============================================================
// THE LESSON
// ============================================================

/*
KEY TAKEAWAYS:

1. EVERY promise chain needs error handling
   - Unhandled promise rejections silently disappear (or crash Node.js)

2. .catch() that returns undefined is WORSE than no .catch()
   - The caller thinks the operation succeeded with undefined result
   - Either re-throw the error, or return a meaningful fallback

3. async/await + try/catch is clearer than .then/.catch chains
   - Easier to read, easier to debug, harder to miss errors

4. Handle edge cases before they become errors
   - Empty arrays: check length before dividing
   - Null values: validate before accessing properties

5. Always include context in error messages
   - Bad:  "Something went wrong"
   - Good: "Failed to get summary for user USR-123: User not found"
*/
