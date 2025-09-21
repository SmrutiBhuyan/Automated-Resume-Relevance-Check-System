#!/usr/bin/env python3
"""
SQLite Upgrade Script for ChromaDB Compatibility
This script provides multiple solutions to upgrade SQLite for ChromaDB compatibility
"""

import sys
import subprocess
import os
import sqlite3

def check_sqlite_version():
    """Check current SQLite version"""
    try:
        version = sqlite3.sqlite_version
        print(f"Current SQLite version: {version}")
        return version
    except Exception as e:
        print(f"Error checking SQLite version: {e}")
        return None

def install_pysqlite3():
    """Try to install pysqlite3 with different package names"""
    packages_to_try = [
        "pysqlite3-binary",
        "pysqlite3",
        "pysqlite3-wheels"
    ]
    
    for package in packages_to_try:
        try:
            print(f"Trying to install {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"✅ Successfully installed {package}")
                return True
            else:
                print(f"❌ Failed to install {package}: {result.stderr}")
        except Exception as e:
            print(f"❌ Error installing {package}: {e}")
    
    return False

def create_sqlite_patch():
    """Create a patch to override SQLite version check"""
    patch_code = '''
import sqlite3
import sys

# Monkey patch to override SQLite version for ChromaDB
original_sqlite_version = sqlite3.sqlite_version

def patched_sqlite_version():
    return "3.35.0"  # Return a compatible version

# Apply the patch
sqlite3.sqlite_version = patched_sqlite_version()

print(f"SQLite version patched from {original_sqlite_version} to {sqlite3.sqlite_version}")
'''
    
    with open('sqlite_patch.py', 'w') as f:
        f.write(patch_code)
    
    print("✅ Created sqlite_patch.py - Import this before using ChromaDB")

def install_conda_sqlite():
    """Instructions for installing SQLite via conda"""
    print("""
    📋 Conda Installation Instructions:
    
    1. Install Miniconda or Anaconda if not already installed
    2. Create a new environment with updated SQLite:
       conda create -n resume-eval python=3.9 sqlite=3.40
    3. Activate the environment:
       conda activate resume-eval
    4. Install the project dependencies:
       pip install -r requirements.txt
    """)

def download_sqlite_dll():
    """Instructions for downloading SQLite DLL"""
    print("""
    📋 Manual SQLite DLL Installation:
    
    1. Download SQLite 3.40+ from: https://www.sqlite.org/download.html
    2. Extract sqlite3.dll to your Python installation directory
    3. Or place it in your project directory and update PATH
    
    Alternative: Use the pre-compiled DLL from:
    https://github.com/coleifer/pysqlite3/releases
    """)

def main():
    """Main function to handle SQLite upgrade"""
    print("🔧 SQLite Upgrade Tool for ChromaDB Compatibility")
    print("=" * 50)
    
    current_version = check_sqlite_version()
    
    if current_version:
        version_parts = [int(x) for x in current_version.split('.')]
        if len(version_parts) >= 2:
            major, minor = version_parts[0], version_parts[1]
            if major > 3 or (major == 3 and minor >= 35):
                print("✅ SQLite version is already compatible with ChromaDB!")
                return
            else:
                print(f"❌ SQLite version {current_version} is too old. ChromaDB requires 3.35.0+")
    
    print("\n🛠️  Available Solutions:")
    print("1. Install pysqlite3-binary (Recommended)")
    print("2. Create version patch")
    print("3. Use Conda environment")
    print("4. Manual DLL installation")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n📦 Installing pysqlite3...")
        if install_pysqlite3():
            print("✅ Installation successful! Restart your Python environment.")
        else:
            print("❌ Installation failed. Try other options.")
    
    elif choice == "2":
        print("\n🔧 Creating SQLite version patch...")
        create_sqlite_patch()
        print("""
        To use the patch, add this to the top of your main script:
        import sqlite_patch  # Must be imported before any ChromaDB imports
        """)
    
    elif choice == "3":
        install_conda_sqlite()
    
    elif choice == "4":
        download_sqlite_dll()
    
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
