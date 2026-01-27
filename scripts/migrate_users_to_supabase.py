"""
Migration Script: JSON Users to Supabase
Run once to migrate existing users from _secret_auth_.json to Supabase users table

Usage:
    python scripts/migrate_users_to_supabase.py
"""

import json
import os
import sys
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SECRET_KEY = os.getenv('SUPABASE_SECRET_KEY')


def migrate_users():
    """Migrate users from JSON file to Supabase"""

    print("=" * 50)
    print("User Migration: JSON to Supabase")
    print("=" * 50)

    # Check Supabase credentials
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        print("ERROR: SUPABASE_URL and SUPABASE_SECRET_KEY must be set in .env")
        return

    # Read existing users
    json_file = '_secret_auth_.json'
    if not os.path.exists(json_file):
        print(f"No {json_file} found. Nothing to migrate.")
        return

    with open(json_file, 'r') as f:
        users = json.load(f)

    if not users:
        print("No users found in JSON file.")
        return

    print(f"Found {len(users)} users to migrate")

    # Connect to Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

    migrated = 0
    skipped = 0
    errors = 0

    for idx, user in enumerate(users):
        try:
            # Check if user already exists by email
            existing_email = supabase.table('users').select('user_id').eq('email', user['email']).execute()
            if existing_email.data:
                print(f"  SKIP: {user['username']} - email already exists")
                skipped += 1
                continue

            # Check if user already exists by username
            existing_username = supabase.table('users').select('user_id').eq('username', user['username']).execute()
            if existing_username.data:
                print(f"  SKIP: {user['username']} - username already exists")
                skipped += 1
                continue

            # First user becomes admin
            is_admin = migrated == 0

            # Insert user
            supabase.table('users').insert({
                'username': user['username'],
                'name': user['name'],
                'email': user['email'],
                'password_hash': user['password'],  # Already Argon2 hashed
                'is_admin': is_admin,
                'is_active': True,
                'created_at': datetime.now(timezone.utc).isoformat()
            }).execute()

            role = "ADMIN" if is_admin else "user"
            print(f"  OK: {user['username']} ({user['email']}) - {role}")
            migrated += 1

        except Exception as e:
            print(f"  ERROR: {user['username']} - {str(e)}")
            errors += 1

    print("\n" + "=" * 50)
    print(f"Migration Complete")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped:  {skipped}")
    print(f"  Errors:   {errors}")
    print("=" * 50)

    # Backup the JSON file
    if migrated > 0:
        backup_name = '_secret_auth_.json.backup'
        try:
            os.rename(json_file, backup_name)
            print(f"\nOriginal JSON file renamed to: {backup_name}")
        except Exception as e:
            print(f"\nWarning: Could not rename JSON file: {e}")

    print("\nNext steps:")
    print("1. Verify users in Supabase dashboard")
    print("2. Test login with an existing user")
    print("3. The first migrated user is now an admin")


if __name__ == '__main__':
    migrate_users()
