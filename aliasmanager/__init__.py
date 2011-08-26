from __future__ import print_function

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

__all__ = (
    'init_db',
    'Alias',
    )

Base = declarative_base()

def init_db(config, echo=False):
    url = URL(drivername=config['driver'],
              username=config['user'],
              password=config['password'],
              host=config['host'],
              port=config['port'],
              database=config['dbname'])
    if 'table' in config and config['table']:
        change_table_name(Base.metadata, Alias, config['table'])
    engine = create_engine(url, echo=echo)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    return session

def change_table_name(metadata, cls, name):
    old_name = cls.__table__.name
    schema = cls.__table__.schema

    if name == old_name:
        return

    cls.__table__.name = name
    if schema:
        cls.__table__.fullname = '%s.%s' % (schema, name)
    else:
        cls.__table__.fullname = name
    metadata._remove_table(old_name, schema)
    metadata._add_table(name, schema, cls.__table__)

class Alias(Base):
    __tablename__ = 'aliases'
    __table_args__ = {'mysql_engine':'InnoDB'}
    alias = Column(String(255), primary_key=True, nullable=False)
    destination = Column(String(255), nullable=False)
    enabled = Column(Boolean, default=True)

    def __init__(self, alias, destination, enabled=True):
        self.alias = alias
        self.destination = destination
        self.enabled = enabled

    def __repr__(self):
        return "<Alias('%s','%s',%s)>" % (self.alias, self.destination, self.enabled)
