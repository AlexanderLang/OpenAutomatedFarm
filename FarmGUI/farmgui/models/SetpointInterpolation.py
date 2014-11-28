"""
Created on Feb 15, 2014

@author: alex
"""

from sqlalchemy import Column
from sqlalchemy.types import Float
from sqlalchemy.types import Integer
from sqlalchemy.types import SmallInteger
from sqlalchemy.types import Unicode
from sqlalchemy.orm import relationship

from farmgui.models import Base
from farmgui.models import InterpolationKnot

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
    knots = relationship('InterpolationKnot', backref='interpolation')

    f = None

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
        fig = plt.figure(figsize=(5, 3))
        ax = fig.add_axes([0.15, 0.15, 0.8, 0.8])
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
        while len(x) <= self.order:
            # not enough knots
            x.append(self.end_time * len(x)/5.0)
            y.append(self.end_value)
        x_inter = np.linspace(0, self.end_time, 100)
        if self.order < 4:
            f = interpolate.interp1d(x, y, kind=self.order)
            y_inter = f(x_inter)
        else:
            f = interpolate.splrep(x, y)
            y_inter = interpolate.splev(x_inter, f)

        ax.set_xlim(0, self.end_time)
        ax.set_ylim(y_inter.min()-1, y_inter.max()+1)
        ax.plot(x, y, 'o', x_inter, y_inter, '-')
        fig.savefig(filename)

    def calculate_interpolation(self):
        x = []
        y = []
        x.append(0)
        y.append(self.start_value)
        for knot in self.knots:
            x.append(knot.time)
            y.append(knot.value)
        x.append(self.end_time)
        y.append(self.end_value)
        if self.order < 4:
            self.f = interpolate.interp1d(x, y, kind=self.order)
        else:
            self.f = interpolate.splrep(x, y)

    def get_value_at(self, interpolation_time):
        if self.f is None:
            self.calculate_interpolation()
        if self.order < 4:
            y = self.f([interpolation_time])[0]
        else:
            y = interpolate.splev([interpolation_time], self.f)[0]
        return round(y.item(), 2)


def init_setpoint_interpolations(db_session):
    h = 3600
    m = 60
    new_inter = SetpointInterpolation('Temperature Interpolation (long day)', 1, 20, 86400, 20, '...')
    new_inter.knots.append(InterpolationKnot(new_inter, 6*h, 20))
    new_inter.knots.append(InterpolationKnot(new_inter, 8*h, 25))
    new_inter.knots.append(InterpolationKnot(new_inter, 22*h, 25))
    db_session.add(new_inter)
    new_inter = SetpointInterpolation('Humidity Interpolation (long day)', 1, 70, 86400, 70, '...')
    new_inter.knots.append(InterpolationKnot(new_inter, 6*h, 70))
    new_inter.knots.append(InterpolationKnot(new_inter, 8*h, 50))
    new_inter.knots.append(InterpolationKnot(new_inter, 22*h, 50))
    db_session.add(new_inter)
    new_inter = SetpointInterpolation('Red Light Interpolation (long day)', 1, 0, 86400, 0, '...')
    new_inter.knots.append(InterpolationKnot(new_inter, 3*h, 0))
    new_inter.knots.append(InterpolationKnot(new_inter, 3*h+30*m, 100))
    new_inter.knots.append(InterpolationKnot(new_inter, 20*h+30*m, 100))
    new_inter.knots.append(InterpolationKnot(new_inter, 21*h, 0))
    db_session.add(new_inter)
    new_inter = SetpointInterpolation('Test Interpolation', 1, 0, 86400, 0, '...')
    new_inter.knots.append(InterpolationKnot(new_inter, 4*h, 100))
    new_inter.knots.append(InterpolationKnot(new_inter, 8*h, 0))
    new_inter.knots.append(InterpolationKnot(new_inter, 12*h, 100))
    new_inter.knots.append(InterpolationKnot(new_inter, 16*h, 0))
    new_inter.knots.append(InterpolationKnot(new_inter, 20*h, 100))
    db_session.add(new_inter)
