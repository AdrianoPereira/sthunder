import os
from sqlalchemy import create_engine, select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from shapely import wkt as swkt
from shapely import geometry as sgeom
import geopandas as gpd


Base = declarative_base()


class FlashDatetime(Base):
    __tablename__ = 'flash_datetime'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    flash = relationship("FlashSpatioTemporal")


class FlashCoordinate(Base):
    __tablename__ = 'flash_coordinate'
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry('POINT'), unique=True)
    flash = relationship("FlashSpatioTemporal")
    land_class = relationship("LandClass")


class FlashSpatioTemporal(Base):
    __tablename__ = 'flash_spatio_temporal'
    id = Column(Integer, primary_key=True)
    total = Column(Integer)
    time = Column(Integer, ForeignKey('flash_datetime.id'))
    coords = Column(Integer, ForeignKey('flash_coordinate.id'))


class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    geom = Column(Geometry('GEOMETRY'))
    country_state = relationship("State")
    country_biome = relationship("Biome")
    country_watershed = relationship("Watershed")
    country_region = relationship("Region")



class State(Base):
    __tablename__ = 'state'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    country = Column(Integer, ForeignKey('country.id'))
    uf = Column(String(5))
    geom = Column(Geometry('GEOMETRY'))
    state_city = relationship("City")


class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    state = Column(Integer, ForeignKey('state.id'))
    uf = Column(String(5))
    population = Column(Integer)
    gpd = Column(Float)
    geom = Column(Geometry('GEOMETRY'))


class Biome(Base):
    __tablename__ = 'biome'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    country = Column(Integer, ForeignKey('country.id'))
    geom = Column(Geometry('GEOMETRY'))


class Watershed(Base):
    __tablename__ = 'watershed'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    country = Column(Integer, ForeignKey('country.id'))
    geom = Column(Geometry('GEOMETRY'))


class Region(Base):
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    country = Column(Integer, ForeignKey('country.id'))
    geom = Column(Geometry('GEOMETRY'))


class LandClass(Base):
    __tablename__ = 'land_class'
    id = Column(Integer, primary_key=True)
    class_name = Column(String(150))
    collection = Column(String(50))
    date = Column(Integer())
    coords = Column(Integer, ForeignKey('flash_coordinate.id'))


if __name__ == "__main__":
    pass
