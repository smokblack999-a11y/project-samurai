from logging.config import fileConfig
from sqlalchemy import engine_from_config,pool
from alembic import context
from app.models import Base
from app.config import settings
config=context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata=Base.metadata
def run_migrations_offline():
    context.configure(url=settings.DATABASE_URL.replace('+asyncpg',''),target_metadata=target_metadata,literal_binds=True,compare_type=True)
    with context.begin_transaction(): context.run_migrations()
def run_migrations_online():
    cfg=config.get_section(config.config_ini_section,{})
    cfg['sqlalchemy.url']=settings.DATABASE_URL.replace('+asyncpg','')
    connectable=engine_from_config(cfg,prefix='sqlalchemy.',poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection,target_metadata=target_metadata,compare_type=True)
        with context.begin_transaction(): context.run_migrations()
if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()
