"""
Database initialization — loads CSV data into SQLite on startup.
Uses SQLAlchemy for safe parameterized queries.
"""
import logging
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from app.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def load_csv_to_db(csv_name: str, table_name: str) -> int:
    """Load a CSV file into a SQLite table. Returns row count."""
    csv_path = Path(settings.CSV_DIR) / csv_name
    if not csv_path.exists():
        logger.warning(f"CSV not found: {csv_path}")
        return 0
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    logger.info(f"Loaded {len(df)} rows into table '{table_name}'")
    return len(df)


def init_db():
    """Initialize the database by loading all CSV sources."""
    logger.info("Initializing database from CSV sources...")
    tables = {
        "movies.csv": "movies",
        "viewers.csv": "viewers",
        "watch_activity.csv": "watch_activity",
        "reviews.csv": "reviews",
        "marketing_spend.csv": "marketing_spend",
        "regional_performance.csv": "regional_performance",
    }
    for csv_file, table in tables.items():
        try:
            count = load_csv_to_db(csv_file, table)
            logger.info(f"  ✓ {table}: {count} rows")
        except Exception as e:
            logger.error(f"  ✗ Failed to load {csv_file}: {e}")
    logger.info("Database initialization complete.")


def get_table_names() -> list[str]:
    inspector = inspect(engine)
    return inspector.get_table_names()


def execute_safe_query(query: str, params: dict = None) -> list[dict]:
    """
    Execute a read-only SQL query safely.
    Only SELECT statements are allowed — enforced here.
    """
    stripped = query.strip().upper()
    if not stripped.startswith("SELECT"):
        raise ValueError("Only SELECT queries are permitted.")

    # Block dangerous keywords
    blocked = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "EXEC", "PRAGMA"]
    for kw in blocked:
        if kw in stripped:
            raise ValueError(f"Query contains blocked keyword: {kw}")

    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchmany(500)]
    return rows
