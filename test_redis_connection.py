"""Test Upstash Redis Connection"""
import redis

# Connect to Upstash Redis
redis_url = "rediss://default:AYotAAIncDE1NmMyYTEzZDAxNDY0NDFmYjA3YmQ3NWJiOGRhZGVlZHAxMzUzNzM@faithful-guinea-35373.upstash.io:6379"

print("🔌 Connecting to Upstash Redis...")
r = redis.Redis.from_url(redis_url)

# Test write
print("📝 Testing write operation...")
r.set('test_key', 'Hello from ModalityRAG!')

# Test read
print("📖 Testing read operation...")
value = r.get('test_key')
print(f"✓ Retrieved value: {value.decode()}")

# Test delete
print("🗑️ Testing delete operation...")
r.delete('test_key')

# Verify delete
if r.get('test_key') is None:
    print("✓ Delete successful!")

print("\n" + "="*60)
print("✅ UPSTASH REDIS CONNECTION SUCCESSFUL!")
print("="*60)
print(f"📡 Connected to: faithful-guinea-35373.upstash.io")
print("🚀 Ready for production deployment!")
print("="*60)
