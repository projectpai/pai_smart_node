import pathlib
import yaml
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def connect_engine():
    DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

    BASE_DIR = pathlib.Path(__file__).parent
    config_path = BASE_DIR / 'config.yaml'

    with open(str(config_path), 'rb') as f:
        db_config = yaml.load(f.read())

    conn = create_engine(DSN.format(**db_config['postgres_user']), isolation_level='AUTOCOMMIT').connect()

    return conn


class Ico(Base):
    __tablename__ = 'ico'

    id = Column(Integer, primary_key=True)
    asset = Column(String, unique=True)
    is_approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_issued = Column(Boolean, default=False)
    source_address = Column(String(36), unique=True)
    return_address = Column(String, nullable=False)
    details = Column(String, nullable=True)

    def save_ico(self, **kwargs):
        conn = connect_engine()
        ico = self.__table__
        return conn.execute(
            ico.insert().values(**kwargs)
        )

    def get_all(self):
        ico = self.__table__
        conn = connect_engine()
        result = conn.execute(
            ico.select()
        )
        return [dict(r) for r in result]

    def get_by_id(self, id):
        ico = self.__table__
        conn = connect_engine()
        result = conn.execute(
            ico.select().where(
                ico.c.id == id
            )
        )
        return [dict(r) for r in result]

    def get_by_return_address(self, return_address):
        ico = self.__table__
        conn = connect_engine()
        result = conn.execute(
            ico.select().where(
                ico.c.return_address == return_address
            )
        )
        return [dict(r) for r in result]

    def get_by_source_address(self, source_address):
        ico = self.__table__
        conn = connect_engine()
        result = conn.execute(
            ico.select().where(
                ico.c.source_address == source_address
            )
        )
        return [dict(r) for r in result][0]

    def update_source_address(self, conn, id, address):
        ico = self.__table__
        return conn.execute(
            ico.update().where(
                ico.c.id == id
            ).values(
                asset_source_address=address
            )
        )

    def end_ico(self, conn, id):
        ico = self.__table__
        return conn.execute(
            ico.update().where(
                ico.c.id == id
            ).values(
                is_active=False
            )
        )


class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True)
    txid = Column(String, unique=True, nullable=False)
    asset_address = Column(String, nullable=False)
    contributor_address = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    time_received = Column(String, nullable=False)
    is_paid = Column(Boolean, default=False, nullable=False)
    confirmations = Column(Integer, default=0)
    details = Column(String, nullable=True)

    def save_transaction(self, conn, **kwargs):
        transaction = self.__table__
        return conn.execute(
            transaction.insert().values(**kwargs)
        )

    def get_unpaid(self, source):
        transaction = self.__table__
        conn = connect_engine()
        result = conn.execute(
            transaction.select().where(and_(
                transaction.c.is_paid == False,
                transaction.c.asset_address == source
                )
            )
        )

        return [dict(r) for r in result]

