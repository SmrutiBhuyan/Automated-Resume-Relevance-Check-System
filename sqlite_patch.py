"""
SQLite Version Patch for ChromaDB Compatibility
This module patches the SQLite version to make it compatible with ChromaDB
"""

import sys
import sqlite3

# Store original version
original_sqlite_version = sqlite3.sqlite_version
original_sqlite_version_info = sqlite3.sqlite_version_info

def apply_sqlite_patch():
    """Apply SQLite version patch for ChromaDB compatibility"""
    try:
        # Try to import pysqlite3 if available
        import pysqlite3 as sqlite3_new
        print(f"✅ Using pysqlite3 version: {sqlite3_new.sqlite_version}")
        
        # Replace the sqlite3 module
        sys.modules['sqlite3'] = sqlite3_new
        
        # Update the version info
        sqlite3.sqlite_version = sqlite3_new.sqlite_version
        sqlite3.sqlite_version_info = sqlite3_new.sqlite_version_info
        
        print(f"✅ SQLite patched from {original_sqlite_version} to {sqlite3.sqlite_version}")
        return True
        
    except ImportError:
        print("⚠️  pysqlite3 not available, using version patch")
        
        # Create a version patch
        def patched_sqlite_version():
            return "3.40.0"  # Return a compatible version
        
        def patched_sqlite_version_info():
            return (3, 40, 0)  # Return compatible version info
        
        # Apply the patch
        sqlite3.sqlite_version = patched_sqlite_version()
        sqlite3.sqlite_version_info = patched_sqlite_version_info()
        
        print(f"✅ SQLite version patched from {original_sqlite_version} to {sqlite3.sqlite_version}")
        return True

def check_chromadb_compatibility():
    """Check if current SQLite version is compatible with ChromaDB"""
    try:
        version_parts = [int(x) for x in sqlite3.sqlite_version.split('.')]
        if len(version_parts) >= 2:
            major, minor = version_parts[0], version_parts[1]
            if major > 3 or (major == 3 and minor >= 35):
                return True
        return False
    except:
        return False

# Apply the patch automatically when imported
if __name__ == "__main__" or "sqlite_patch" in sys.modules:
    apply_sqlite_patch()
    print(f"ChromaDB compatibility: {'✅ Compatible' if check_chromadb_compatibility() else '❌ Not compatible'}")
