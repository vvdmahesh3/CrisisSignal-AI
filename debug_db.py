import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from urllib.parse import quote

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
_db_path = os.path.join(INSTANCE_DIR, "crisissignal_dev.db")

uri1 = "sqlite:///" + quote(_db_path.replace("\\", "/"), safe=":/")
uri2 = "sqlite:///" + _db_path.replace("\\", "/")

print(f"URI (encoded): {uri1}")
print(f"URI (raw):     {uri2}")

# Test with SQLAlchemy
from sqlalchemy import create_engine, text

for label, uri in [("encoded", uri1), ("raw", uri2)]:
    try:
        engine = create_engine(uri)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"  {label}: SUCCESS")
    except Exception as e:
        print(f"  {label}: FAILED - {e}")

# Test with absolute path using pathlib
from pathlib import Path
db_file = Path(INSTANCE_DIR) / "crisissignal_dev.db"
uri3 = f"sqlite:///{db_file.as_posix()}"
print(f"\nURI (pathlib):  {uri3}")
try:
    engine = create_engine(uri3)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print(f"  pathlib: SUCCESS")
except Exception as e:
    print(f"  pathlib: FAILED - {e}")

# Test with raw connection creator
import sqlite3
uri4 = "sqlite://"
print(f"\nURI (creator):  {uri4} + custom creator")
try:
    engine = create_engine(uri4, creator=lambda: sqlite3.connect(_db_path))
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print(f"  creator: SUCCESS")
except Exception as e:
    print(f"  creator: FAILED - {e}")
