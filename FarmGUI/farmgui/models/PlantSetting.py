"""
Created on Nov 17, 2013

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import BigInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship

from .meta import Base


class PlantSetting(Base):
    """
    classdocs
    """
    __tablename__ = 'PlantSettings'

    _id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    plant = Column(Unicode(250), nullable=False)
    variety = Column(Unicode(250), nullable=False)
    method = Column(Unicode(250), nullable=False)
    description = Column(Text, nullable=True)
    stages = relationship("Stage", backref="plantSetting")

    def __init__(self, plant, variety, method, description=None):
        """
        Constructor
        """
        self.plant = plant
        self.variety = variety
        self.method = method
        self.description = description

    @property
    def id(self):
        return self._id


def init_plant_settings(db_session):
    db_session.add(PlantSetting('tomato', 'unkown', 'hydroponic', 'tomato test settings'))

