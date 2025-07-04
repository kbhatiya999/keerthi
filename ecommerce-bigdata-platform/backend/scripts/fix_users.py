#!/usr/bin/env python3
"""
Script to fix existing users in the database by adding missing fields.
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import users_collection, init_database

load_dotenv()

async def fix_users():
    """Fix existing users by adding missing fields."""
    print("Connecting to database...")
    await init_database()
    
    print("Finding users without is_active field...")
    # Find users that don't have is_active field
    users_without_is_active = []
    async for user in users_collection.find({"is_active": {"$exists": False}}):
        users_without_is_active.append(user)
    
    if not users_without_is_active:
        print("All users already have is_active field.")
        return
    
    print(f"Found {len(users_without_is_active)} users without is_active field.")
    
    # Update users to add is_active field
    for user in users_without_is_active:
        user_id = user["_id"]
        print(f"Updating user {user_id}...")
        
        update_data = {
            "is_active": True,
            "updated_at": datetime.utcnow()
        }
        
        # Also add created_at if missing
        if "created_at" not in user:
            update_data["created_at"] = datetime.utcnow()
        
        result = await users_collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            print(f"✓ Updated user {user_id}")
        else:
            print(f"✗ Failed to update user {user_id}")
    
    print("User fix completed!")

if __name__ == "__main__":
    asyncio.run(fix_users()) 