import asyncio
import os

from alembic import context
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from storage_client.models import Base

target_metadata = Base.metadata

load_dotenv()

context.config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))


def run_migrations_online():
    asyncio.run(run_async_migrations())


async def run_async_migrations():
    connectable = async_engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


run_migrations_online()
