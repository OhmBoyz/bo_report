from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1) Importez ici votre Base SQLAlchemy
from app.models import Base  

# 2) Définissez target_metadata à partir de Base
target_metadata = Base.metadata

# -- début du boilerplate Alembic --
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
# -- fin du boilerplate Alembic --

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        render_as_batch=True,    # <- ajoutez ceci
        compare_type=True,       # <- pour que Alembic détecte les changements de type
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # 3) Créez l’engine AVANT d’appeler context.configure
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # 4) Passez la connection ET target_metadata ici
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,    # <- ajoutez ceci
            compare_type=True,       # <- pour que Alembic détecte les changements de type
            compare_server_default=True,  # optionnel
        )

        with context.begin_transaction():
            context.run_migrations()


# 5) Choix de mode offline/online
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
