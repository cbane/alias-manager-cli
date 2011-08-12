from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

__all__ = (
    'init_db',
    'Alias',
    )

Base = declarative_base()

def init_db(dsn):
    engine = create_engine(dsn, echo=False)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    return session

class Alias(Base):
    __tablename__ = 'aliases'
    alias = Column(String(255), primary_key=True, nullable=False)
    destination = Column(String(255), nullable=False)
    enabled = Column(Boolean, default=True)

    def __init__(self, alias, destination, enabled=True):
        self.alias = alias
        self.destination = destination
        self.enabled = enabled

    def __repr__(self):
        return "<Alias('%s','%s',%s)>" % (self.alias, self.destination, self.enabled)
