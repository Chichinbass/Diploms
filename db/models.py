from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    route_name = Column(String, nullable=True)     
    city_from = Column(String, nullable=False)
    city_to = Column(String, nullable=False)
