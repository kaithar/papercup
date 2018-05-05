from __future__ import with_statement
from alembic import context
from papercup.drivers import sqlalchemy as db

if context.is_offline_mode():
    print('Offline mode not supported')
else:
  with db.engine.begin() as connection:
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()
