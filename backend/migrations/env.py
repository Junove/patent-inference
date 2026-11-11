from alembic import context

from app.db import Base, engine
import app.models  # noqa: F401  (registers tables on Base.metadata)

with engine.connect() as conn:
    context.configure(connection=conn, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
