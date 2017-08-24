from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    asc, desc,
    func
)

from sqlalchemy.dialects.mysql import *
from sqlalchemy.types import *

from sqlalchemy.ext.automap import automap_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
)

from sqlalchemy.schema import (
    UniqueConstraint,
    Index,
    MetaData
)

from sqlalchemy.exc import DBAPIError

import transaction

_sm = sessionmaker(expire_on_commit=False)

def get_session():
    return scoped_session(_sm)

Base = automap_base()

# Decorator - binds a session to the lifetime of a member function of a class
def bind_session( wrapfunc ):
    def inner( self, *args, **kwargs ):
        self.sql = get_session()
        res = wrapfunc( self, *args, **kwargs )
        self.sql.close()
        return res
    return inner

from contextlib import contextmanager

@contextmanager
def session():
    """Provide a transactional scope around a series of operations."""
    sql = get_session()
    try:
        yield sql
        sql.commit()
    except:
        sql.rollback()
        raise
    finally:
        sql.close()

config_defaults = {
    'papercup': {
        'db': None
    }
}

def post_init():
    global c
    from papercup import config
    mysqlconf = config.get('papercup', 'db')
    if mysqlconf:
        from sqlalchemy import create_engine
        engine = create_engine(mysqlconf, pool_recycle=0)
        Base.prepare(engine, reflect=True)
        _sm.configure(bind=engine)
        c = Base.classes
        
