"""
Database configuration and session management for Email Campaign App.

Supports both SQLite (development) and PostgreSQL (production) databases.
"""

import os
from typing import Generator
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./email_campaigns.db")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,  # Allow multi-threading
            "timeout": 20  # Timeout for database operations
        },
        poolclass=StaticPool,  # Use static pool for SQLite
        echo=ENVIRONMENT == "development"  # Log SQL queries in development
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,  # Recycle connections after 5 minutes
        echo=False  # Don't log SQL queries in production
    )

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Import Base from models (defined there to avoid circular imports)
# Will be imported when models are loaded


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        @app.get("/")
        def read_root(db: Session = Depends(get_db)):
            # Use db session here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.
    
    This function creates all tables defined in the models.
    Should be called during application startup.
    """
    # Import models to ensure they're registered
    import importlib
    try:
        models_module = importlib.import_module('app.models')
        Base = getattr(models_module, 'Base')
        Base.metadata.create_all(bind=engine)
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not import models: {e}")


def drop_tables():
    """
    Drop all database tables.
    
    WARNING: This will delete all data!
    Only use for testing or development reset.
    """
    # Import models to ensure they're registered
    import importlib
    try:
        models_module = importlib.import_module('app.models')
        Base = getattr(models_module, 'Base')
        Base.metadata.drop_all(bind=engine)
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not import models: {e}")


def get_database_info() -> dict:
    """
    Get database connection information.
    
    Returns:
        dict: Database connection details
    """
    return {
        "database_url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL,
        "database_type": "sqlite" if DATABASE_URL.startswith("sqlite") else "postgresql",
        "environment": ENVIRONMENT,
        "echo_queries": engine.echo
    }


def check_database_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            # Try a simple query
            connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


class DatabaseManager:
    """
    Database manager for handling database operations.
    
    Provides utilities for database management, migrations, and health checks.
    """
    
    def __init__(self):
        self.engine = engine
        self.session_local = SessionLocal
        
    def create_all_tables(self):
        """Create all database tables."""
        create_tables()
        
    def drop_all_tables(self):
        """Drop all database tables."""
        drop_tables()
        
    def reset_database(self):
        """Reset database by dropping and recreating all tables."""
        self.drop_all_tables()
        self.create_all_tables()
        
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.session_local()
        
    def health_check(self) -> dict:
        """
        Perform database health check.
        
        Returns:
            dict: Health check results
        """
        try:
            connection_ok = check_database_connection()
            db_info = get_database_info()
            
            return {
                "status": "healthy" if connection_ok else "unhealthy",
                "connection": connection_ok,
                "database_info": db_info
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connection": False,
                "error": str(e)
            }


# Global database manager instance
db_manager = DatabaseManager()