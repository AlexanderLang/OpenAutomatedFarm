"""
Created on Feb 15, 2014

@author: alex
"""

from time import mktime
from sqlalchemy import Column
from sqlalchemy.types import Float
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.orm import relationship

from .meta import Base

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate


class SetpointInterpolation(Base):
    """
    classdocs
    """
    __tablename__ = 'SetpointInterpolations'

    _id = Column(SmallInteger, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = Column(Unicode(250))
    order = Column(SmallInteger, nullable=False)
    start_value = Column(Float(), nullable=False)
    end_time = Column(Integer(), nullable=False)
    end_value = Column(Float(), nullable=True)
    description = Column(Unicode(250), nullable=True)
    knots = relationship('InterpolationKnot')

    def __init__(self, name, order, start_value, end_time, end_value, description):
        self.name = name
        self.order = order
        self.start_value = start_value
        self.end_time = end_time
        self.end_value = end_value
        self.description = description

    @property
    def id(self):
        return self._id

    def plot(self, y_axis_name, filename):
        fig = plt.figure(figsize=(8, 5))
        ax = fig.add_axes([0.05, 0.05, 0.8, 0.9])
        ax.set_xlabel('Time')
        ax.set_ylabel(y_axis_name, rotation='horizontal')
        ax.xaxis.grid(color='gray', linestyle='dashed')
        ax.yaxis.grid(color='gray', linestyle='dashed')
        x = []
        y = []
        x.append(0)
        y.append(self.start_value)
        for knot in self.knots:
            x.append(knot.time*self.end_time)
            y.append(knot.value)
        x.append(self.end_time)
        y.append(self.end_value)
        ax.set_xlim(0, self.end_time)
        f = interpolate.interp1d(x, y, kind=self.order)
        x_inter = np.arange(0, self.end_time, self.end_time/200)
        y_inter = f(x_inter)
        ax.set_ylim(y_inter.min(), y_inter.max())
        ax.plot(x, y, 'o', x_inter, y_inter, '-')
        fig.savefig(filename)
