import java.util.*;

/**
 * Bug Pattern: ConcurrentModificationException
 * Difficulty: Intermediate
 * Language: Java
 *
 * THE SCENARIO:
 * You're filtering a list of users — removing inactive ones.
 * It works in testing with small lists but crashes in production
 * with larger datasets.
 */
public class concurrent_modification {

    // ============================================================
    // THE BUGGY CODE
    // ============================================================

    static void removeInactive_buggy(List<String> users, Set<String> inactiveIds) {
        // ❌ ConcurrentModificationException — modifying list while iterating
        for (String user : users) {
            if (inactiveIds.contains(user)) {
                users.remove(user);  // CRASHES!
            }
        }
    }

    // ============================================================
    // THE FIXES
    // ============================================================

    // Fix 1: Use Iterator.remove() — the safe way to remove during iteration
    static void removeInactive_iterator(List<String> users, Set<String> inactiveIds) {
        Iterator<String> it = users.iterator();
        while (it.hasNext()) {
            if (inactiveIds.contains(it.next())) {
                it.remove();  // Safe — iterator handles structural modification
            }
        }
    }

    // Fix 2: removeIf (Java 8+) — cleanest approach
    static void removeInactive_removeIf(List<String> users, Set<String> inactiveIds) {
        users.removeIf(inactiveIds::contains);
    }

    // Fix 3: Collect then remove — two-pass approach
    static void removeInactive_twoPass(List<String> users, Set<String> inactiveIds) {
        List<String> toRemove = new ArrayList<>();
        for (String user : users) {
            if (inactiveIds.contains(user)) {
                toRemove.add(user);
            }
        }
        users.removeAll(toRemove);
    }

    // Fix 4: Create a new filtered list (immutable-style)
    static List<String> removeInactive_filter(List<String> users, Set<String> inactiveIds) {
        return users.stream()
                .filter(u -> !inactiveIds.contains(u))
                .collect(java.util.stream.Collectors.toList());
    }

    // ============================================================
    // DEMO
    // ============================================================

    public static void main(String[] args) {
        Set<String> inactive = new HashSet<>(Arrays.asList("user-2", "user-4"));

        // Buggy version
        try {
            List<String> users = new ArrayList<>(Arrays.asList("user-1", "user-2", "user-3", "user-4", "user-5"));
            removeInactive_buggy(users, inactive);
        } catch (ConcurrentModificationException e) {
            System.out.println("BUGGY: ConcurrentModificationException thrown!");
        }

        // Fix 1: Iterator
        List<String> users1 = new ArrayList<>(Arrays.asList("user-1", "user-2", "user-3", "user-4", "user-5"));
        removeInactive_iterator(users1, inactive);
        System.out.println("Fix 1 (Iterator):  " + users1);

        // Fix 2: removeIf
        List<String> users2 = new ArrayList<>(Arrays.asList("user-1", "user-2", "user-3", "user-4", "user-5"));
        removeInactive_removeIf(users2, inactive);
        System.out.println("Fix 2 (removeIf):  " + users2);

        // Fix 3: Two-pass
        List<String> users3 = new ArrayList<>(Arrays.asList("user-1", "user-2", "user-3", "user-4", "user-5"));
        removeInactive_twoPass(users3, inactive);
        System.out.println("Fix 3 (Two-pass):  " + users3);

        // Fix 4: Stream filter
        List<String> users4 = new ArrayList<>(Arrays.asList("user-1", "user-2", "user-3", "user-4", "user-5"));
        List<String> result = removeInactive_filter(users4, inactive);
        System.out.println("Fix 4 (Stream):    " + result);
    }
}

/*
KEY TAKEAWAYS:

1. Never modify a collection while iterating with for-each.
   The for-each loop uses an iterator internally, and structural
   modifications invalidate it.

2. Preferred fix in modern Java: list.removeIf(condition)
   Clean, readable, and safe.

3. This also applies to Maps:
   map.entrySet().removeIf(entry -> entry.getValue() == null);

4. For concurrent access (multiple threads), use ConcurrentHashMap
   or CopyOnWriteArrayList instead of synchronizing manually.
*/
