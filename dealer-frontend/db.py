# frontend/db.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        database=os.environ.get("DB_NAME", "dealer_dashboard"),
        user=os.environ.get("DB_USER", "dealer_user"),
        password=os.environ.get("DB_PASSWORD", "strongpassword")
    )
