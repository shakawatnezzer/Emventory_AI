from app.database import engine

try:
    conn = engine.connect()
    print("✅ Successfully connected to PostgreSQL!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
