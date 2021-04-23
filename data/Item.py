import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase


class Item(SqlAlchemyBase):
    __tablename__ = "product"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    isActive = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

