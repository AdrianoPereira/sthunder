import os
import xarray as xr
import numpy as np
import db_queries as dbq
from sqlalchemy import select, create_engine, Table, func
from db_schema import FlashDatetime, FlashCoordinate
from sqlalchemy.orm import sessionmaker
import geopandas as gpd
from shapely.geometry import Point
from .Database import Database


def job_datetime():
    path_nc = "/glm/G05GT1H"
    filenames = [os.path.join(path_nc, file) for file in os.listdir(path_nc)]

    for filename in filenames:
        nc = xr.load_dataset(filename)
        datetimes = nc['time'].values

        for datetime in datetimes:
            dbq.insert_datetime(str(datetime))


def job_coords():
    path_nc = "/glm/G05GT1H"
    filenames = [os.path.join(path_nc, file) for file in os.listdir(path_nc)]

    slons = set()
    slats = set()

    for filename in filenames:
        nc = xr.load_dataset(filename)
        lons = nc['lon'].values
        lats = nc['lat'].values

        print(filename, len(lons), len(lats))
        for lon in lons:
            for lat in lats:
                slons.add(lon)
                slats.add(lat)

    for lon in slons:
        for lat in slats:
            dbq.insert_coords(coordinates=f"POINT({lon} {lat})")


# def job_flash(filename):
#     nc = xr.load_dataset(filename)
#     times = list(map(str, nc['time'].values))
#     lons = nc['lon'].values
#     lats = nc['lat'].values
#     totals = nc['var'].values
#
#     for i, time in enumerate(times):
#         for j, lat in enumerate(lats):
#             for k, lon in enumerate(lons):
#                 print(f"{i}, {j}, {k}")
#
#                 total = totals[i, j, k]
#                 coords = f"POINT({lon} {lat})"
#
#                 insert_flash(time=time, coords=coords, total=total)

def job_flash(filename):
    nc = xr.load_dataset(filename)
    times = list(map(str, nc['time'].values))
    lons = nc['lon'].values
    lats = nc['lat'].values
    totals = nc['var'].values

    gdf = gpd.read_file("/home/adriano/CAP-395/data/GEO/Vector/"
                        "SouthAmericaPolygon/South_America.shp")
    brazil = gdf.query("COUNTRY == 'Brazil'").iloc[-0, -1]

    blats, blons = [], []
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            coord = Point(lon, lat)
            if brazil.contains(coord):
                blats.append(i)
                blons.append(j)

    for i, time in enumerate(times):
        for j, k in zip(blats, blons):
            print(
                f"{i}, {j}, {k}: {totals[i, j, k]}, POINT({lons[k]} {lats[j]})")

            total = totals[i, j, k]
            coords = f"POINT({lons[k]} {lats[j]})"
            dbq.insert_flash(time=time, coords=coords, total=total)


def job_country():
    gdf = gpd.read_file(
        "../../data/GEO/Vector/SouthAmericaPolygon/South_America.shp").to_crs(
        "EPSG:4326")

    for i, row in gdf.iterrows():
        print(f"Inserting {row['COUNTRY']}")
        name = row['COUNTRY'],
        geom = row['geometry'].wkt

        dbq.insert_country(name, geom)


def job_land_class():
    pass


def job_region():
    gdf = gpd.read_file(
        "/home/adriano/CAP-395/data/GEO/Vector/BrazilRegionsPolygon/regioes_2010.shp").to_crs(
        "EPSG:4326")

    for i, row in gdf.iterrows():
        print(row)
        dbq.insert_region(name=row['nome'], country=3, geom=row['geometry'].wkt)

def job_state():
    gdf = gpd.read_file(
        "/home/adriano/CAP-395/data/GEO/Vector/brazil-uf-shapefile/estados_2010.shp").to_crs(
        "EPSG:4326")

    for i, row in gdf.iterrows():
        print(row)
        dbq.insert_state(name=row['nome'], country=3, uf=row['sigla'], geom=row['geometry'].wkt)


def job_city():
    gdf = gpd.read_file("/home/adriano/CAP-395/data/GEO/Vector/BrazilCitiesPolygon/municipios_2010.shp").to_crs('EPSG:4326')

    for i, row in gdf.iterrows():
        dbq.insert_city(name=row['nome'], uf=row['uf'], population=row['populacao'], gpd=row['pib'], geom=row['geometry'].wkt)


if __name__ == "__main__":
    # job_region()
    # job_country()
    # job_datetime()
    # job_coords()
    # job_state()
    job_city()

    # job_flash("/glm/G05GT1H/GLM_2020_01_hourly_05x05.nc") #1 tab
    # job_flash("/glm/G05GT1H/GLM_2020_03_hourly_05x05.nc") #2 tab
    # job_flash("/glm/G05GT1H/GLM_2020_04_hourly_05x05.nc") #1 tab
    # job_flash("/glm/G05GT1H/GLM_2020_05_hourly_05x05.nc") #2 tab
    # job_flash("/glm/G05GT1H/GLM_2020_06_hourly_05x05.nc") #1 tab
    # job_flash("/glm/G05GT1H/GLM_2020_07_hourly_05x05.nc") #2 tab
    # job_flash("/glm/G05GT1H/GLM_2020_08_hourly_05x05.nc") #1 tab
    # job_flash("/glm/G05GT1H/GLM_2020_09_hourly_05x05.nc") #2 tab
    # job_flash("/glm/G05GT1H/GLM_2020_10_hourly_05x05.nc") #3 tab
    # job_flash("/glm/G05GT1H/GLM_2020_11_hourly_05x05.nc") #1 tab
    # job_flash("/glm/G05GT1H/GLM_2020_12_hourly_05x05.nc") #2 tab

    # filenames = (
    #     "/glm/G05GT1H/GLM_2020_02_hourly_05x05.nc",
    #     "/glm/G05GT1H/GLM_2020_03_hourly_05x05.nc",
    #     "/glm/G05GT1H/GLM_2020_04_hourly_05x05.nc",
    #     "/glm/G05GT1H/GLM_2020_05_hourly_05x05.nc",
    #     "/glm/G05GT1H/GLM_2020_06_hourly_05x05.nc",
    #     "/glm/G05GT1H/GLM_2020_07_hourly_05x05.nc",
    #     "/glm/G05GT1H/GLM_2020_08_hourly_05x05.nc",
    #     "/glm/G05GT1H/GLM_2020_09_hourly_05x05.nc",
    #     "/glm/G05GT1H/GLM_2020_10_hourly_05x05.nc",
    #     "/glm/G05GT1H/GLM_2020_11_hourly_05x05.nc",
    #     "/glm/G05GT1H/GLM_2020_12_hourly_05x05.nc"
    # )
    #
    # for filename in filenames:
    #     job_flash(filename)
