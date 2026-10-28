import os
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "jachai.db"
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def auto_migrate_schema(target_engine):
    """
    Safely applies missing columns to existing SQLite/PostgreSQL tables on startup
    to prevent 'no such column' OperationalErrors when deploying schema updates on Render.
    """
    try:
        insp = inspect(target_engine)
        tables = insp.get_table_names()
        with target_engine.connect() as conn:
            # 1. products table
            if "products" in tables:
                cols = {c["name"] for c in insp.get_columns("products")}
                if "is_discontinued" not in cols:
                    conn.execute(text("ALTER TABLE products ADD COLUMN is_discontinued BOOLEAN DEFAULT 0"))
                if "discontinued_note_en" not in cols:
                    conn.execute(text("ALTER TABLE products ADD COLUMN discontinued_note_en VARCHAR(500) NULL"))
                if "discontinued_note_bn" not in cols:
                    conn.execute(text("ALTER TABLE products ADD COLUMN discontinued_note_bn VARCHAR(500) NULL"))
                if "homepage_slot_order" not in cols:
                    conn.execute(text("ALTER TABLE products ADD COLUMN homepage_slot_order INTEGER DEFAULT 0"))

            # 2. store_offers table
            if "store_offers" in tables:
                o_cols = {c["name"] for c in insp.get_columns("store_offers")}
                if "is_sponsored" not in o_cols:
                    conn.execute(text("ALTER TABLE store_offers ADD COLUMN is_sponsored BOOLEAN DEFAULT 0"))
                if "discount_tag" not in o_cols:
                    conn.execute(text("ALTER TABLE store_offers ADD COLUMN discount_tag VARCHAR(50) NULL"))
                if "discount_pct" not in o_cols:
                    conn.execute(text("ALTER TABLE store_offers ADD COLUMN discount_pct INTEGER NULL"))
                if "risk_level" not in o_cols:
                    conn.execute(text("ALTER TABLE store_offers ADD COLUMN risk_level VARCHAR(50) DEFAULT 'low'"))
                if "trust_score" not in o_cols:
                    conn.execute(text("ALTER TABLE store_offers ADD COLUMN trust_score INTEGER DEFAULT 95"))
                if "trust_badge" not in o_cols:
                    conn.execute(text("ALTER TABLE store_offers ADD COLUMN trust_badge VARCHAR(100) NULL"))
                if "spider_status" not in o_cols:
                    conn.execute(text("ALTER TABLE store_offers ADD COLUMN spider_status VARCHAR(50) DEFAULT 'healthy'"))
                if "last_synced_at" not in o_cols:
                    conn.execute(text("ALTER TABLE store_offers ADD COLUMN last_synced_at VARCHAR(100) NULL"))

            conn.commit()
            print("[Database Migration] Auto-migration successfully verified table columns.")
    except Exception as e:
        print(f"[Database Migration Notice] Auto-migration check: {e}")


# Run migration immediately on module load
try:
    auto_migrate_schema(engine)
except Exception:
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
