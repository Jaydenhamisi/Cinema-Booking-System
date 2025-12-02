from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Alembic Config object
config = context.config

# Logging configuration
if config.config_file_name:
    fileConfig(config.config_file_name)

# Import Base BEFORE importing any models
from app.core.database import Base

# IMPORT ALL MODEL MODULES (NOT classes)
# This ensures Base.metadata contains everything.
import app.contexts.screen.models
import app.contexts.movie.models
import app.contexts.showtime.models
import app.contexts.seat_availability.models
import app.contexts.reservation.models
import app.contexts.order.models
import app.contexts.pricing.models
import app.contexts.payment.models
import app.contexts.refund.models
import app.contexts.audit.models
import app.contexts.auth.models
import app.contexts.user.models

# target metadata for Alembic
target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    from app.core.config import settings
    from sqlalchemy import create_engine

    connectable = create_engine(settings.DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()



if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
