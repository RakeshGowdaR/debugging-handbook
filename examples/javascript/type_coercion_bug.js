/**
 * Bug Pattern: Type Coercion
 * Difficulty: Beginner
 * Language: JavaScript
 *
 * THE SCENARIO:
 * Your shopping cart total is showing wrong numbers.
 * Items cost $10, $20, $30 but the total shows "102030" instead of 60.
 */

// ============================================================
// THE BUGGY CODE
// ============================================================

// API returns prices as strings (common with JSON from some backends)
const cartItems = [
    { name: "T-Shirt", price: "10.00" },
    { name: "Jeans",   price: "20.00" },
    { name: "Shoes",   price: "30.00" },
];

// Bug: string concatenation instead of addition
function calculateTotal_buggy(items) {
    let total = 0;
    for (const item of items) {
        total += item.price;  // "0" + "10.00" + "20.00" + "30.00"
    }
    return total;
}

console.log("--- BUGGY VERSION ---");
const buggyTotal = calculateTotal_buggy(cartItems);
console.log(`  Total: ${buggyTotal}`);         // "010.0020.0030.00"
console.log(`  Type: ${typeof buggyTotal}`);    // "string" ← should be number!

// More type coercion traps:
console.log("\n--- TYPE COERCION TRAPS ---");
console.log(`  "5" + 3     = ${("5" + 3)}`);        // "53"  (string concat)
console.log(`  "5" - 3     = ${("5" - 3)}`);        // 2     (numeric subtract)
console.log(`  "5" * "3"   = ${("5" * "3")}`);      // 15    (numeric multiply)
console.log(`  true + true = ${(true + true)}`);     // 2     (true → 1)
console.log(`  [] + []     = "${([] + [])}" (empty string)`);
console.log(`  [] + {}     = "${([] + {})}"`);       // "[object Object]"
console.log(`  null == undefined: ${null == undefined}`);  // true
console.log(`  null === undefined: ${null === undefined}`); // false
console.log(`  NaN === NaN: ${NaN === NaN}`);        // false!


// ============================================================
// THE FIXES
// ============================================================

// Fix 1: Explicitly convert types
function calculateTotal_fixed(items) {
    let total = 0;
    for (const item of items) {
        total += parseFloat(item.price);  // Convert string to number
    }
    return total;
}

// Fix 2: Use Number() for conversion
function calculateTotal_number(items) {
    return items.reduce((sum, item) => sum + Number(item.price), 0);
}

// Fix 3: Use unary + operator (concise but less readable)
function calculateTotal_unary(items) {
    return items.reduce((sum, item) => sum + (+item.price), 0);
}

console.log("\n--- FIXED VERSIONS ---");
console.log(`  parseFloat: $${calculateTotal_fixed(cartItems)}`);    // 60
console.log(`  Number():   $${calculateTotal_number(cartItems)}`);   // 60
console.log(`  Unary +:    $${calculateTotal_unary(cartItems)}`);    // 60


// Fix 4: For money, use integers (cents) to avoid floating point issues
function calculateTotal_cents(items) {
    const totalCents = items.reduce((sum, item) => {
        return sum + Math.round(parseFloat(item.price) * 100);
    }, 0);
    return totalCents / 100;
}

console.log(`  Cents-based: $${calculateTotal_cents(cartItems)}`);  // 60


// Defensive comparison
console.log("\n--- SAFE COMPARISONS ---");

// ❌ Loose equality surprises
console.log(`  "0" == false:  ${("0" == false)}`);    // true (wat?)
console.log(`  "" == false:   ${"" == false}`);       // true
console.log(`  " " == false:  ${" " == false}`);      // false (wat??)

// ✅ Strict equality — always use ===
console.log(`  "0" === false: ${("0" === false)}`);   // false (correct)
console.log(`  "" === false:  ${"" === false}`);      // false (correct)


// ============================================================
// THE LESSON
// ============================================================

/*
KEY TAKEAWAYS:

1. Always use === instead of ==
   == does type coercion, which leads to surprising results.
   === checks type AND value. No surprises.

2. Be explicit about type conversions:
   Number("42")       for string → number
   String(42)         for number → string
   Boolean(value)     for → boolean
   parseInt("42", 10) for string → integer (always pass radix 10)

3. API data is always strings until you convert it:
   JSON.parse gives you strings for string fields.
   URL params, form inputs, localStorage — all strings.

4. For money, use integers (cents):
   $19.99 → store as 1999
   Avoids floating point: 0.1 + 0.2 = 0.30000000000000004

5. Use TypeScript to catch these at compile time:
   function calculateTotal(items: {price: number}[]): number
   If someone passes a string, TypeScript will error.
*/
