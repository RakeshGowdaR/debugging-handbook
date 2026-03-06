"""
Bug Pattern: Silent Exception Swallowing
Difficulty: Beginner
Language: Python

THE SCENARIO:
Users report that sometimes their profile photo doesn't update.
No errors in the logs. The upload endpoint returns 200 OK.
But the old photo remains. The bug is invisible.
"""

import os

# ============================================================
# THE BUGGY CODE
# ============================================================

class ProfileService:
    def __init__(self):
        self.profiles = {
            "user-1": {"name": "Alice", "photo": "default.jpg"},
        }
    
    def update_photo(self, user_id, photo_data):
        """Upload a new profile photo."""
        try:
            # Validate the image
            validated = self._validate_image(photo_data)
            
            # Resize for storage
            resized = self._resize_image(validated)
            
            # Upload to storage
            url = self._upload_to_storage(user_id, resized)
            
            # Update the database
            self.profiles[user_id]["photo"] = url
            
            return {"success": True, "url": url}
        
        except:
            # ❌ THE BUG: bare except swallows ALL errors silently
            pass
        
        return {"success": True}  # ❌ Always returns success!
    
    def _validate_image(self, photo_data):
        if not photo_data:
            raise ValueError("No image data provided")
        if len(photo_data) > 5_000_000:
            raise ValueError("Image too large (max 5MB)")
        return photo_data
    
    def _resize_image(self, image_data):
        # Simulate a bug: fails on certain image formats
        if b"WEBP" in image_data:
            raise NotImplementedError("WebP format not supported yet")
        return image_data
    
    def _upload_to_storage(self, user_id, image_data):
        # Simulate storage
        return f"https://cdn.example.com/photos/{user_id}.jpg"


# Demonstration
service = ProfileService()

print("--- BUGGY VERSION ---")

# Works fine with regular images
result = service.update_photo("user-1", b"JPEG image data here")
print(f"  JPEG upload: {result}")
print(f"  Photo URL: {service.profiles['user-1']['photo']}")

# Silently fails with WebP — user sees "success" but photo doesn't change
service.profiles["user-1"]["photo"] = "default.jpg"  # Reset
result = service.update_photo("user-1", b"WEBP image data here")
print(f"\n  WebP upload: {result}")  # Says success!
print(f"  Photo URL: {service.profiles['user-1']['photo']}")  # Still default!
print(f"  BUG: Returned success but photo didn't change. No error logged.")

# Even None input is silently swallowed
result = service.update_photo("user-1", None)
print(f"\n  Null upload: {result}")  # Still says success!


# ============================================================
# THE FIX
# ============================================================

class ProfileServiceFixed:
    def __init__(self):
        self.profiles = {
            "user-1": {"name": "Alice", "photo": "default.jpg"},
        }
    
    def update_photo(self, user_id, photo_data):
        """Upload a new profile photo — with proper error handling."""
        # Validate input — let validation errors propagate
        validated = self._validate_image(photo_data)
        
        # Resize — catch specific, known error
        try:
            resized = self._resize_image(validated)
        except NotImplementedError as e:
            return {"success": False, "error": str(e)}
        
        # Upload — handle infrastructure errors separately
        try:
            url = self._upload_to_storage(user_id, resized)
        except IOError as e:
            print(f"  [ERROR] Storage upload failed for {user_id}: {e}")
            return {"success": False, "error": "Upload failed, please try again"}
        
        # Update database
        self.profiles[user_id]["photo"] = url
        return {"success": True, "url": url}
    
    def _validate_image(self, photo_data):
        if not photo_data:
            raise ValueError("No image data provided")
        if len(photo_data) > 5_000_000:
            raise ValueError("Image too large (max 5MB)")
        return photo_data
    
    def _resize_image(self, image_data):
        if b"WEBP" in image_data:
            raise NotImplementedError("WebP format not supported yet")
        return image_data
    
    def _upload_to_storage(self, user_id, image_data):
        return f"https://cdn.example.com/photos/{user_id}.jpg"


print("\n--- FIXED VERSION ---")
fixed_service = ProfileServiceFixed()

result = fixed_service.update_photo("user-1", b"JPEG image data here")
print(f"  JPEG upload: {result}")

result = fixed_service.update_photo("user-1", b"WEBP image data here")
print(f"  WebP upload: {result}")  # Properly reports failure

try:
    result = fixed_service.update_photo("user-1", None)
except ValueError as e:
    print(f"  Null upload: Caught ValueError — {e}")  # Properly raises


# ============================================================
# THE LESSON
# ============================================================
"""
KEY TAKEAWAYS:

1. NEVER use bare `except:` or `except Exception:`
   These catch everything, including bugs you need to see.

2. Catch SPECIFIC exceptions you know how to handle:
   except ValueError:       # Input validation
   except ConnectionError:  # Network issue
   except TimeoutError:     # Slow service

3. ALWAYS log or re-raise caught exceptions:
   except SomeError as e:
       logger.error("Failed", error=str(e))
       raise  # or return an error response

4. Return error states, don't silently succeed:
   ❌ except: pass; return {"success": True}
   ✅ except SpecificError: return {"success": False, "error": "..."}

5. The only acceptable bare except is for top-level error handlers
   that log everything and re-raise:
   except Exception as e:
       logger.critical("Unhandled error", exc_info=True)
       raise
"""
