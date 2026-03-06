/**
 * Bug Pattern: Closure Over Loop Variable
 * Difficulty: Beginner-Intermediate
 * Language: JavaScript
 *
 * THE SCENARIO:
 * You're creating click handlers for 5 buttons,
 * each should alert its own number. But they all alert "5".
 */

// ============================================================
// THE BUGGY CODE
// ============================================================

// Simulating button click handlers
var handlers_buggy = [];

for (var i = 0; i < 5; i++) {
  handlers_buggy.push(function() {
    return "Button " + i + " clicked";
  });
}

// Every handler returns "Button 5 clicked"!
console.log("--- BUGGY ---");
handlers_buggy.forEach(function(handler, index) {
  console.log("  Handler " + index + ": " + handler());
});

// WHY: `var i` is function-scoped, not block-scoped.
// All 5 closures share the SAME `i` variable.
// By the time any handler runs, the loop has finished and i === 5.


// ============================================================
// THE FIXES
// ============================================================

// Fix 1: Use `let` (block scoping) — the modern, preferred fix
var handlers_let = [];

for (let i = 0; i < 5; i++) {
  handlers_let.push(function() {
    return "Button " + i + " clicked";
  });
}

console.log("\n--- FIX 1: let ---");
handlers_let.forEach(function(handler, index) {
  console.log("  Handler " + index + ": " + handler());
});


// Fix 2: IIFE (Immediately Invoked Function Expression) — for legacy code
var handlers_iife = [];

for (var i = 0; i < 5; i++) {
  (function(capturedIndex) {
    handlers_iife.push(function() {
      return "Button " + capturedIndex + " clicked";
    });
  })(i);
}

console.log("\n--- FIX 2: IIFE ---");
handlers_iife.forEach(function(handler, index) {
  console.log("  Handler " + index + ": " + handler());
});


// Fix 3: Array methods (functional approach) — cleanest
var handlers_functional = Array.from({ length: 5 }, function(_, i) {
  return function() {
    return "Button " + i + " clicked";
  };
});

console.log("\n--- FIX 3: Array.from ---");
handlers_functional.forEach(function(handler, index) {
  console.log("  Handler " + index + ": " + handler());
});


// ============================================================
// THE LESSON
// ============================================================

/*
KEY TAKEAWAYS:

1. `var` is function-scoped, `let` is block-scoped
   - In a loop, `var` creates ONE variable shared by all iterations
   - `let` creates a NEW variable for each iteration

2. Closures capture the VARIABLE, not its VALUE at the time of capture
   - When you reference `i` inside a closure, it's a live reference
   - It will always read the current value of `i`, not the value when the closure was created

3. This bug commonly appears in:
   - Event handler setup loops
   - setTimeout/setInterval inside loops
   - Dynamic callback creation
   - forEach with async operations using external counter

4. Default to `let` and `const` — never use `var` in modern JavaScript
*/
