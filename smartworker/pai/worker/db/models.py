from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Ico(Base):
    __tablename__ = 'ico'

    id = Column(Integer, primary_key=True)
    ico_name = Column(String, nullable=False)
    asset = Column(String, unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    is_approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    asset_source_address = Column(String(36))

    def save_ico(self, conn, **kwargs):
        ico = self.__table__
        return conn.execute(
            ico.insert().values(**kwargs)
        )

    def get_all(self, conn,):
        ico = self.__table__
        result = conn.execute(
            ico.select()
        )
        return [dict(r) for r in result]

    def get_by_id(self, conn, id):
        ico = self.__table__
        result = conn.execute(
            ico.select().where(
                ico.c.id == id
            )
        )
        return [dict(r) for r in result]

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
    address = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    is_paid = Column(Boolean, default=False, nullable=False)

    def save_transaction(self, conn, **kwargs):
        transaction = self.__table__
        return conn.execute(
            transaction.insert().values(**kwargs)
        )

    def get_unpaid(self, conn):
        transaction = self.__table__
        result = conn.execute(
            transaction.select().where(
                transaction.c.is_paid == False
            )
        )

        return [dict(r) for r in result]

