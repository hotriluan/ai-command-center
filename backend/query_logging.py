"""
Database Query Logging - Phase 2C
Logs slow queries and tracks performance metrics
"""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("sqlalchemy.engine")

# Slow query threshold (in seconds)
SLOW_QUERY_THRESHOLD = 1.0


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Record query start time"""
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries and track metrics"""
    
    total_time = time.time() - conn.info['query_start_time'].pop()
    
    # Log slow queries (> 1 second)
    if total_time > SLOW_QUERY_THRESHOLD:
        # Truncate statement for readability
        statement_preview = statement.replace('\n', ' ').replace('\r', '')[:200]
        logger.warning(
            f"SLOW QUERY ({total_time:.2f}s): {statement_preview}..."
        )
    
    # Debug logging for all queries (only in development)
    logger.debug(f"Query ({total_time:.3f}s): {statement[:100]}")


def setup_query_logging(engine):
    """
    Setup query logging for the given engine
    
    Args:
        engine: SQLAlchemy engine instance
    """
    # Event listeners are already registered via decorators
    # This function is for explicit setup if needed
    logger.info("Query logging initialized")
    logger.info(f"Slow query threshold: {SLOW_QUERY_THRESHOLD}s")
