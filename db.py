# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, create_engine, Integer, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

DB_FILE_PATH = './test.db'

Base = declarative_base()
session = None


# https://segmentfault.com/a/1190000004618621
# https://blog.csdn.net/u010745324/article/details/53047107
class AgentServer(Base):
    __tablename__ = 'AgentServerDB'
    id = Column(Integer, primary_key=True, autoincrement=True)
    IP_PORT = Column(String(22))
    ADDR = Column(String(15))
    IS_ANONYMOUS = Column(String(15))
    SURE_TIME = Column(String(20))
    HTTP = Column(Boolean(), nullable=False)
    HTTPS = Column(Boolean(), nullable=False)
    SOURCES = Column(Integer, ForeignKey('AgentServerSourceDB.SOURCES'))

    def __str__(self):
        return str(self.id) + '  ' + self.IP_PORT


class AgentServerSource(Base):
    __tablename__ = 'AgentServerSourceDB'
    id = Column(Integer, primary_key=True, autoincrement=True)
    aid = relationship('AgentServer', backref='ITS_IP_PORT')
    SOURCES = Column(String(30))
    URL = Column(String(50))

    def __str__(self):
        return str(self.SOURCES)


class DBSession(object):
    engine = None

    def __init__(self):
        if not self.engine:
            self.engine = create_engine('sqlite:///' + DB_FILE_PATH, connect_args={'check_same_thread': False})
        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()

    def close(self):
        self.session.close()


def updata_databases():
    engine = create_engine('sqlite:///' + DB_FILE_PATH, connect_args={'check_same_thread': False})
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.commit()
    session.close()


if __name__ == "__main__":
    updata_databases()










