import os
from sqlalchemy import create_engine


db_uri = os.environ["DATABASE_URL"]

try:
    engine = create_engine(db_uri)
except Exception as e:
    print("Failed to connect to database.")
    print(f"{e}")
    exit(1)
