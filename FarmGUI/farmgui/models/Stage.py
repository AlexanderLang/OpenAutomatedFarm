"""
Created on Nov 17, 2013

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import BigInteger
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.types import Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .meta import Base
from .PlantSetting import PlantSetting


class Stage(Base):
    """
    classdocs
    """
    __tablename__ = 'Stages'

    _id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    plantSettingId = Column(BigInteger, ForeignKey('PlantSettings._id'), nullable=False)
    number = Column(SmallInteger, nullable=False)
    duration = Column(SmallInteger, nullable=False)
    name = Column(Unicode(250), nullable=True)
    description = Column(Text, nullable=True)
    configurations = relationship("StageConfiguration", backref="stage")

    def __init__(self, plant_setting, number, duration, name, description):
        """
        Constructor
        """
        self.plantSetting = plant_setting
        self.number = number
        self.duration = duration
        self.name = name
        self.description = description

    @property
    def id(self):
        return self._id


def init_stages(db_session):
    plant_setting = db_session.query(PlantSetting).filter(PlantSetting.plant == 'tomato').first()
    db_session.add(Stage(plant_setting, 1, 15, 'groth', 'plant must get bigger :)'))
    db_session.add(Stage(plant_setting, 2, 45, 'stage name', 'some description'))

