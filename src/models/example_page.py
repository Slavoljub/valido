from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime

try:
    from src.models.unified_models import db  # Re-use existing db instance if available
except ImportError:
    from flask_sqlalchemy import SQLAlchemy  # Fallback for isolated unit tests
    db = SQLAlchemy()  # type: ignore

class ExamplePage(db.Model):  # type: ignore
    """Demo table representing example pages used in MVVM samples"""

    __tablename__ = 'example_pages'

    id = Column(Integer, primary_key=True)
    slug = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ExamplePage {self.slug}>"

    # ------------------------------------------------------------------
    # Seed helper – only for demo purposes so pages exist without manual DB work
    # ------------------------------------------------------------------
    @classmethod
    def seed_demo(cls) -> None:
        """Insert a few demo rows if table is empty (creates table lazily)."""
        try:
            # Create table if it doesn't exist (no migrations in demo environment)
            with db.engine.begin() as conn:  # type: ignore
                if not db.inspect(conn).has_table(cls.__tablename__):  # type: ignore
                    db.create_all()  # type: ignore

            if cls.query.count() == 0:  # type: ignore
                demo_pages = [
                    cls(slug='base-layout', title='Base Layout Example', description='Demonstrates the base layout.'),
                    cls(slug='compact-layout', title='Compact Layout Example', description='Compact sidebar demo.'),
                    cls(slug='dashboard-layout', title='Dashboard Layout Example', description='Dashboard blocks demo.'),
                ]
                db.session.bulk_save_objects(demo_pages)  # type: ignore
                db.session.commit()  # type: ignore
        except Exception as e:
            # Log the error but don't crash the application
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not seed example pages: {e}")
            # Rollback any partial changes
            try:
                db.session.rollback()  # type: ignore
            except:
                pass
