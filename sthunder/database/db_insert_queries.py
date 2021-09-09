import sys; sys.path.insert(0, "/home/adriano/sthunder")
import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from wlts import WLTS
from sthunder.database import db_schema as dbs
from sthunder.database import db_connection


@db_connection
def insert_datetime(session, datetime):
    flash_time = dbs.FlashDatetime(datetime=datetime)
    session.add(flash_time)
    session.commit()


@db_connection
def insert_coords(session, coordinates):
    flash_coords = dbs.FlashCoordinate(geom=coordinates)
    session.add(flash_coords)
    session.commit()


@db_connection
def insert_flash(session, time, coords, total):
    dtc = session.execute(
        select(
            dbs.FlashDatetime.id
        ).where(
            dbs.FlashDatetime.datetime == time
        )
    ).first()[0]
    gc = session.execute(
        select(
            dbs.FlashCoordinate.id
        ).where(
            dbs.FlashCoordinate.geom == coords
        )
    ).first()[0]

    flash_coords = dbs.FlashSpatioTemporal(time=dtc, coords=gc, total=total)
    session.add(flash_coords)
    session.commit()


@db_connection
def insert_country(session, name, geom):
    country = dbs.Country(name=name, geom=geom)
    session.add(country)
    session.commit()


@db_connection
def insert_region(session, name, country, geom):
    region = dbs.Region(name=name, country=country, geom=geom)
    session.add(region)
    session.commit()


@db_connection
def insert_state(session, name, country, uf, geom):
    state = dbs.State(name=name, country=country, uf=uf, geom=geom)
    session.add(state)
    session.commit()


@db_connection
def insert_city(session, name, uf, population, gpd, geom):
    state = session.query(State.id, State.name).filter(State.uf == uf).first()
    city = City(name=name, state=state[0], uf=uf, population=population,
                gpd=gpd, geom=geom)
    session.add(city)
    session.commit()


@db_connection
def insert_land_class(session, class_name, collection, date, coords):
    land_class = dbs.LandClass(class_name=class_name, collection=collection,
                               date=date, coords=coords)
    session.add(land_class)
    session.commit()


@db_connection
def select_datetime_interval(session):
    query = session.execute(
        select(
            dbs.FlashDatetime.id, dbs.FlashDatetime.datetime
        ).where(
            dbs.FlashDatetime.datetime >= '2020-01-01 10:00',
            dbs.FlashDatetime.datetime <= '2020-01-01 11:00'
        )
    ).all()

    print(query)


@db_connection
def select_countries(session):
    query = session.execute(
        select(
            dbs.FlashSpatioTemporal.id
        ).join(FlashDatetime)
    ).all()

    print(query)


if __name__ == "__main__":
    select_countries()
