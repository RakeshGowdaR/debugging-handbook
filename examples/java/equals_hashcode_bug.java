import java.util.*;

/**
 * Bug Pattern: equals/hashCode Contract Violation
 * Difficulty: Intermediate
 * Language: Java
 *
 * THE SCENARIO:
 * You put a User object into a HashMap.
 * Later, you look it up with an identical User object — but it's not found.
 * The HashMap "lost" your data.
 */
public class equals_hashcode_bug {

    // ============================================================
    // THE BUGGY CODE
    // ============================================================

    static class UserBuggy {
        String id;
        String name;

        UserBuggy(String id, String name) {
            this.id = id;
            this.name = name;
        }

        // Overrides equals but NOT hashCode — violates the contract!
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof UserBuggy)) return false;
            UserBuggy other = (UserBuggy) o;
            return id.equals(other.id);
        }

        // Missing: hashCode() override!
        // Default hashCode is based on memory address, so two equal objects
        // will have DIFFERENT hash codes → HashMap can't find them.
    }

    // ============================================================
    // THE FIX
    // ============================================================

    static class UserFixed {
        String id;
        String name;

        UserFixed(String id, String name) {
            this.id = id;
            this.name = name;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof UserFixed)) return false;
            UserFixed other = (UserFixed) o;
            return id.equals(other.id);
        }

        @Override
        public int hashCode() {
            return Objects.hash(id);  // Consistent with equals!
        }
    }

    public static void main(String[] args) {
        // BUGGY: HashMap loses the entry
        System.out.println("--- BUGGY VERSION ---");
        Map<UserBuggy, String> buggyMap = new HashMap<>();
        buggyMap.put(new UserBuggy("1", "Alice"), "admin");

        UserBuggy lookup = new UserBuggy("1", "Alice");
        System.out.println("  equals: " + new UserBuggy("1", "Alice").equals(lookup));  // true
        System.out.println("  found:  " + buggyMap.get(lookup));  // null! Lost!
        System.out.println("  WHY: hashCode differs, so HashMap looks in wrong bucket");

        // FIXED: HashMap works correctly
        System.out.println("\n--- FIXED VERSION ---");
        Map<UserFixed, String> fixedMap = new HashMap<>();
        fixedMap.put(new UserFixed("1", "Alice"), "admin");

        UserFixed fixedLookup = new UserFixed("1", "Alice");
        System.out.println("  equals: " + new UserFixed("1", "Alice").equals(fixedLookup));
        System.out.println("  found:  " + fixedMap.get(fixedLookup));  // "admin"
    }
}

/*
KEY TAKEAWAYS:

1. THE CONTRACT: If a.equals(b) then a.hashCode() == b.hashCode()
   If you override equals(), you MUST override hashCode().

2. HashMap/HashSet use hashCode() to find the bucket,
   then equals() to match within the bucket.
   Wrong hashCode → wrong bucket → object "disappears."

3. Use Objects.hash() for easy, correct implementations:
   @Override public int hashCode() { return Objects.hash(field1, field2); }

4. In modern Java, consider using Records (Java 16+):
   record User(String id, String name) {}
   Records auto-generate equals, hashCode, and toString correctly.

5. Mutable fields in equals/hashCode are dangerous:
   If you put an object in a HashMap and then change a field used
   in hashCode, the object becomes unfindable.
*/
