"""
Test Redis Cloud Connection
"""

import os
from dotenv import load_dotenv
import redis

def test_redis_connection():
    """Test connection to Redis Cloud"""
    load_dotenv()
    
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    try:
        print(f"🔄 Testing Redis connection to: {redis_url}")
        
        # Parse Redis URL
        r = redis.from_url(redis_url)
        
        # Test connection
        response = r.ping()
        print(f"✅ Redis connection successful! Response: {response}")
        
        # Test basic operations
        r.set('test_key', 'Hello Redis Cloud!')
        value = r.get('test_key')
        print(f"✅ Test write/read successful: {value.decode()}")
        
        # Clean up
        r.delete('test_key')
        print("✅ Test cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your Redis Cloud connection string")
        print("2. Ensure your database is active")
        print("3. Verify your password is correct")
        print("4. Check if your IP is whitelisted (if required)")
        return False

if __name__ == "__main__":
    print("🚀 Testing Redis Cloud Connection")
    print("=" * 40)
    
    success = test_redis_connection()
    
    if success:
        print("\n🎉 Redis is ready! You can now start the system.")
    else:
        print("\n❌ Please fix the Redis connection before starting the system.")
