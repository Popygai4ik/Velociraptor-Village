import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

class Adr(SqlAlchemyBase):
    __tablename__ = 'adress'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    adress = sqlalchemy.Column(sqlalchemy.String, nullable=True)