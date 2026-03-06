"""
Bug Pattern: Null Reference / NoneType Error
Difficulty: Beginner
Language: Python

THE SCENARIO:
You're building a user profile page. The API returns user data,
but sometimes fields are missing. Your code crashes in production
for some users but works fine in testing.
"""

# ============================================================
# THE BUGGY CODE
# ============================================================

def format_user_profile(user_data):
    """Format user data for display on profile page."""
    name = user_data["name"].title()
    email = user_data["email"].lower()
    city = user_data["address"]["city"]
    bio = user_data["bio"].strip()[:140]
    
    return {
        "display_name": name,
        "email": email,
        "location": city,
        "short_bio": bio,
    }


# This works fine in testing:
test_user = {
    "name": "john doe",
    "email": "JOHN@EXAMPLE.COM",
    "address": {"city": "New York", "zip": "10001"},
    "bio": "  Software engineer who loves debugging.  ",
}
print("Test user:", format_user_profile(test_user))


# But these REAL users crash the app:
real_users = [
    # User who signed up via OAuth (no bio filled in)
    {"name": "jane smith", "email": "jane@test.com", "address": {"city": "London"}, "bio": None},
    
    # User from legacy migration (address was a flat string)
    {"name": "bob wilson", "email": "bob@test.com", "address": "123 Main St", "bio": "Hi!"},
    
    # User who deleted their account info
    {"name": None, "email": "ghost@test.com", "address": None, "bio": ""},
]

print("\n--- Watch it crash ---")
for i, user in enumerate(real_users):
    try:
        print(f"User {i}: {format_user_profile(user)}")
    except (TypeError, KeyError, AttributeError) as e:
        print(f"User {i} CRASHED: {type(e).__name__}: {e}")


# ============================================================
# THE FIX
# ============================================================

def format_user_profile_fixed(user_data):
    """Format user data for display — handles missing/null fields gracefully."""
    if not user_data:
        return {"display_name": "Unknown", "email": "", "location": "Unknown", "short_bio": ""}
    
    # Safe access with defaults
    name = (user_data.get("name") or "Anonymous").title()
    email = (user_data.get("email") or "").lower()
    
    # Nested access — check type before diving in
    address = user_data.get("address")
    if isinstance(address, dict):
        city = address.get("city", "Unknown")
    else:
        city = "Unknown"
    
    bio = (user_data.get("bio") or "").strip()[:140]
    
    return {
        "display_name": name,
        "email": email,
        "location": city,
        "short_bio": bio,
    }


print("\n--- Fixed version ---")
for i, user in enumerate(real_users):
    print(f"User {i}: {format_user_profile_fixed(user)}")


# ============================================================
# THE LESSON
# ============================================================
"""
KEY TAKEAWAYS:

1. Never chain attribute access without null checks
   user["address"]["city"]  ← if "address" is None, this crashes

2. Your test data is NOT representative of production data
   Test with: None values, missing keys, wrong types, empty strings

3. Use .get() with defaults instead of direct key access
   user.get("name", "Anonymous")  instead of  user["name"]

4. "or" trick for None-to-default:
   (user.get("name") or "Anonymous")
   This handles both missing key AND None value

5. Check types before assuming structure:
   isinstance(address, dict) before address["city"]
"""
