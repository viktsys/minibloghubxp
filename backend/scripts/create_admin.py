#!/usr/bin/env python3
"""
Script to create an admin user for the Mini Blog Hub XP application.
"""

import sys
import os
from getpass import getpass

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def create_admin():
    """Create an admin user interactively"""
    print("=== Mini Blog Hub XP - Create Admin User ===\n")
    
    # Get user input
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    full_name = input("Full name (optional): ").strip() or None
    password = getpass("Password: ")
    confirm_password = getpass("Confirm password: ")
    
    # Validate input
    if not username or not email or not password:
        print("Error: Username, email, and password are required!")
        return False
    
    if password != confirm_password:
        print("Error: Passwords don't match!")
        return False
    
    # Create user in database
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print("Error: User with this username or email already exists!")
            return False
        
        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            is_superuser=True,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"\nSuccess! Admin user '{username}' created successfully!")
        print(f"User ID: {admin_user.id}")
        return True
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = create_admin()
    sys.exit(0 if success else 1)
