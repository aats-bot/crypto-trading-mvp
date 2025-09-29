import os
from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool

# 1) Carregar .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# 2) Config Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3) URL do banco (preferir a síncrona para Alembic)
db_url = os.getenv("postgresql://postgres:aats.dados@localhost:5432/crypto_trading_mvp") or os.getenv("postgresql+asyncpg://postgres:aats.dados@localhost:5432/crypto_trading_mvp")
if not db_url:
    raise RuntimeError("Defina DATABASE_URL_SYNC ou DATABASE_URL no .env")

config.set_main_option("sqlalchemy.url", db_url)

# 4) Importar seu Base.metadata (AJUSTE ESTE BLOCO)
# Deixe UM dos imports descomentado conforme seu projeto:

# Exemplo típico se você tem "app/models.py" com Base e modelos:
# from app.models import Base

# Ou se você tem "app/db/base.py" que agrega os imports dos modelos:
# from app.db.base import Base

# Ou se está em "src/models/__init__.py":
# from src.models import Base

# >>>>>> AJUSTE AQUI <<<<<<
from app.models import Base  # <-- troque para o caminho correto dos seus modelos

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
