"""Database engine + session.

Backed by the hosted Supabase Postgres instance (PostGIS enabled). The backend
connects directly with SQLAlchemy using the service-level Postgres credentials,
so it bypasses row level security by design; RLS stays enabled on the table to
keep the public PostgREST API closed.
"""

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def _build_engine():
    """Create the Supabase Postgres engine and report PostGIS availability."""
    if not settings.database_url.startswith("postgres"):
        raise RuntimeError(
            "DATABASE_URL must point at the Supabase Postgres instance. "
            "Copy the connection string from Project Settings > Database."
        )

    engine = create_engine(
        settings.database_url,
        # pre_ping validates a pooled connection before use, and recycle keeps
        # connections young enough that Supabase's pooler does not close them
        # mid-request.
        pool_pre_ping=True,
        pool_recycle=180,
        pool_size=5,
        max_overflow=5,
        future=True,
        connect_args={
            "connect_timeout": 10,
            "sslmode": "require",
            # PostGIS lives in the `extensions` schema on Supabase, so the
            # geography type only resolves when it is on the search path.
            "options": "-csearch_path=public,extensions",
        },
    )

    with engine.connect() as conn:
        has_postgis = bool(
            conn.execute(
                text("SELECT count(*) FROM pg_extension WHERE extname = 'postgis'")
            ).scalar()
        )
    if not has_postgis:
        logger.warning("PostGIS not enabled; storing plain lat/lon only.")
    return engine, has_postgis


engine, POSTGIS_ENABLED = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Verify the schema managed by Supabase migrations is reachable.

    Tables are owned by the migrations in `supabase/migrations/`, so this does
    not create anything; it just fails loudly if the app cannot see them.
    """
    from app.models import detection  # noqa: F401  (register metadata)

    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT to_regclass('public.detection_reports') IS NOT NULL")
        ).scalar()
    if not exists:
        raise RuntimeError(
            "Table public.detection_reports is missing. Apply the Supabase "
            "migrations before starting the API."
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
