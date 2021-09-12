import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import shapely.geometry as sgeom
from descartes import PolygonPatch
import matplotlib as mpl
from sthunder import constants as const


def load_NCFile(filename):
    nc = xr.load_dataset(filename)
    lon = nc['lon'].data
    lat = nc['lat'].data
    tim = nc['time'].data
    var = nc['var'].data
    
    return lon, lat, tim, var


def filter_coords_country(glons, glats, country_name):
    gdf = gpd.read_file(const.SHP_SOUTH_AMERICA, crs=const.EPSG4326)
    country_geom = gdf[gdf['COUNTRY'] == country_name].iloc[0, -1]
    
    clons, clats, lats_idx, lons_idx = [], [], [], []
    
    for i, lat in enumerate(glats):
        for j, lon in enumerate(glons):
            if country_geom.contains(sgeom.Point(lon, lat)):
                clats.append(lat)
                clons.append(lon)
                lats_idx.append(i)
                lons_idx.append(j)

    clats = np.array(clats)                
    clons = np.array(clons)

    lats_idx = np.array(lats_idx)    
    lons_idx = np.array(lons_idx)
    
    return country_geom, clons, clats, lons_idx, lats_idx


def plot_annual_flash_density(country_geom, glats, glons, lats_idx, lons_idx):
    dpi = 100
    width = np.round(1366 * 100 / 100)
    height = 768*2
    
    vmin, vmax = 0, 93100
    cmap = 'Spectral_r'
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    # levels = np.linspace(vmin, vmax, 10)
    levels = (0, 200, 400, 600, 800, 1000, 2000, 3000, 4000, 5000, 10000, 
              15000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 93100)
    
    fig, ax = plt.subplots(1, 1, figsize=(width/dpi, height/dpi), 
                           facecolor='w', sharex=True, sharey=True)
    
    mat = np.zeros((glats.shape[0], glons.shape[0]))
    
    path = "/glm/G05GT1H/"
    files = sorted([os.path.join(path, file) for file in os.listdir(path)])
    for i, file in enumerate(files):       
        gvars = xr.load_dataset(file)['var'].data
        
        for lat_idx, lon_idx in zip(lats_idx, lons_idx):
            mat[lat_idx][lon_idx] += gvars[:, lat_idx, lon_idx].sum()
    
        mlon, mlat = np.meshgrid(glons[lons_idx.min(): lons_idx.max()], 
                                 glats[lats_idx.min(): lats_idx.max()])
        mat[mat == 0] = np.nan
        
    maxv = 0
    for ii in range(gvars.shape[1]):
        for jj in range(gvars.shape[2]):
            maxv = mat[ii, jj].sum() if mat[ii, jj].sum() > maxv else maxv
    print(file, maxv)
    
    ax.set_title(f"ACUMULADO ANUAL DE FLASHES EM 2020", 
                 fontdict={'size': 16, 'weight': 'bold'})
    img = ax.contourf(mlon, mlat, mat[lats_idx.min():lats_idx.max(), 
                                      lons_idx.min(): lons_idx.max()], 
                 cmap=cmap, levels=levels, norm=norm)
    path = PolygonPatch(country_geom, ec='k', fc='none', lw=2)
    ax.add_patch(path)
    
    ax.grid(ls='--', alpha=0.5)
    
    ax.set_xlabel('Longitude [°]', fontdict={'size': 12})
    ax.set_ylabel('Latitude [°]', fontdict={'size': 12})
        
    cbaxes = fig.add_axes([0.12, 0.03, 0.780, 0.0175])
    cbar = fig.colorbar(
        img, cax=cbaxes, ticks=levels, orientation="horizontal",
        extend='both',
        shrink=0.5
    )
    cbar.set_label(
        r"ACUMULADO DE FLASHES",
        labelpad=-55, fontdict={'size': 14, 'weight': '500'},
    )
    
    plt.savefig(f"{const.DIR_RESULTS}/spatial_density_analysis/" \
                "density_map_anual.png", 
                    transparent=False, bbox_inches='tight', pad_inches=0.1)
        
        
def plot_monthly_flash_density(country_geom, glats, glons, lats_idx, lons_idx):
    dpi = 100
    width = np.round(1366 * 125 / 100)
    height = 768*2.3
    
    vmin, vmax = 0, 40000
    cmap = 'Spectral_r'
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    levels = (0, 10, 50, 100, 200, 400, 600, 800, 1000, 2000, 3000, 4000, 
              5000, 10000, 15000, 20000, 30000, 40000)
    
    fig, ax = plt.subplots(3, 4, figsize=(width/dpi, height/dpi), 
                           facecolor='w', sharex=True, sharey=True)
    fig.suptitle("ACUMULADO MENSAL DE FLASHES EM 2020", size=18, 
                 weight='bold', y=0.92)
    
    path = "/glm/G05GT1H/"
    files = sorted([os.path.join(path, file) for file in os.listdir(path)])
    for i, file in enumerate(files):    
        row = i//4
        col = i%4
        
        mat = np.zeros((glats.shape[0], glons.shape[0]))
        gvars = xr.load_dataset(file)['var'].data
        
        maxv = 0
        for ii in range(gvars.shape[1]):
            for jj in range(gvars.shape[2]):
                maxv = gvars[:, ii, jj].sum() if gvars[:, ii, jj].sum() > maxv else maxv
        print(file, maxv)
        
        for lat_idx, lon_idx in zip(lats_idx, lons_idx):
            mat[lat_idx][lon_idx] += gvars[:, lat_idx, lon_idx].sum()
    
        mlon, mlat = np.meshgrid(glons[lons_idx.min(): lons_idx.max()], 
                                 glats[lats_idx.min(): lats_idx.max()])
        mat[mat == 0] = np.nan
        
        ax[row][col].set_title(f"{const.MONTHS_LABELS[i+1].upper()}",
                               fontdict={'size': 14, 'weight': '500'})
        img = ax[row][col].contourf(mlon, mlat, 
                                    mat[lats_idx.min():lats_idx.max(), 
                                        lons_idx.min(): lons_idx.max()], 
                     cmap=cmap, levels=levels, norm=norm)
        path = PolygonPatch(country_geom, ec='k', fc='none', lw=2)
        ax[row][col].add_patch(path)
        
        ax[row][col].grid(ls='--', alpha=0.5)
        if row == 2:
            ax[row][col].set_xlabel('Longitude [°]', fontdict={'size': 12})
        if col == 0:
            ax[row][col].set_ylabel('Latitude [°]', fontdict={'size': 12})
        
        
    plt.subplots_adjust(left=0, bottom=None, right=1, top=None,
                            hspace=0.12, wspace=0.04)
    cbaxes = fig.add_axes([0, 0.04, 1, 0.0175])
    cbar = fig.colorbar(
        img, cax=cbaxes, ticks=levels, orientation="horizontal",
        extend='both',
        shrink=0.5
    )
    cbar.set_label(
        r"ACUMULADO DE FLASHES",
        labelpad=-55, fontdict={'size': 14, 'weight': '500'},
    )
    
    plt.savefig(f"{const.DIR_RESULTS}/spatial_density_analysis/" \
                "density_map_month.png", 
                    transparent=False, bbox_inches='tight', pad_inches=0.1)


def plot_seasonal_flash_density(country_geom, glats, glons, lats_idx, 
                                lons_idx):
    def get_station_flashes(station_keys):
        mat = np.zeros((glats.shape[0], glons.shape[0]))
        for month, days in station_keys.items():
            filename = f"/glm/G05GT1H/GLM_2020_{str(month).zfill(2)}_hourly_05x05.nc"
            gvars = xr.load_dataset(
                filename
            )['var'].data[days[0]*24:days[1]*24+1, :, :]

            maxv = 0
            for ii in range(gvars.shape[1]):
                for jj in range(gvars.shape[2]):
                    maxv = gvars[:, ii, jj].sum() if gvars[:, ii, jj].sum() > maxv else maxv

            for lat_idx, lon_idx in zip(lats_idx, lons_idx):
                mat[lat_idx][lon_idx] += gvars[:, lat_idx, lon_idx].sum()
        
        return mat
    
    
    autumn_keys = {3: (20, 31), 4: (0, 30), 5: (0, 31), 6: (0, 20)}
    winter_keys = {6: (20, 30), 7: (0, 31), 8: (0, 31), 9: (0, 22)}
    spring_keys = {9: (22, 30), 10: (0, 31), 11: (0, 30), 12: (0, 21)}
    summer_keys = {12: (21, 31), 1: (0, 31), 2: (0, 29), 3: (0, 20)}
    
    autumn = np.zeros((glats.shape[0], glons.shape[0]))
    winter = np.zeros((glats.shape[0], glons.shape[0]))
    spring = np.zeros((glats.shape[0], glons.shape[0]))
    summer = np.zeros((glats.shape[0], glons.shape[0]))
    
    station_keys = [autumn_keys, winter_keys, spring_keys, summer_keys]
    stations = [get_station_flashes(sk) for sk in station_keys]
    
    mlon, mlat = np.meshgrid(glons[lons_idx.min(): lons_idx.max()], 
                             glats[lats_idx.min(): lats_idx.max()])
    
    dpi = 100
    width = np.round(1366 * 90 / 100)
    height = 768*2.2
    
    vmin, vmax = 0, 66000
    cmap = 'Spectral_r'
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    levels = (0, 200, 400, 600, 800, 1000, 2000, 3000, 4000, 
              5000, 10000, 15000, 20000, 30000, 40000, 50000, 66000)
    
    fig, ax = plt.subplots(2, 2, figsize=(width/dpi, height/dpi), 
                           facecolor='w', sharex=True, sharey=True)
    
    fig.suptitle("ACUMULADO SAZONAL DE FLASHES EM 2020", size=18, 
                 weight='bold', y=0.93)
    for i, station in enumerate(stations):   
        print(const.SEASONAL_LABELS[i+1], station.max())
        row = i//2
        col = i%2
        
        station[station == 0] = np.nan
        ax[row][col].set_title(f"{const.SEASONAL_LABELS[i+1].upper()}", 
                               fontdict={'size': 14, 'weight': '500'})
        img = ax[row][col].contourf(mlon, mlat, 
                                    station[lats_idx.min():lats_idx.max(), 
                                            lons_idx.min(): lons_idx.max()],
                                    cmap=cmap, levels=levels, norm=norm)
        path = PolygonPatch(country_geom, ec='k', fc='none', lw=2)
        ax[row][col].add_patch(path)
        
        ax[row][col].grid(ls='--', alpha=0.5)
        if row == 2:
            ax[row][col].set_xlabel('Longitude [°]', fontdict={'size': 12})
        if col == 0:
            ax[row][col].set_ylabel('Latitude [°]', fontdict={'size': 12})
        
        
    plt.subplots_adjust(left=0, bottom=None, right=1, top=None,
                            hspace=0.09, wspace=0.04)
    cbaxes = fig.add_axes([0, 0.04, 1, 0.0175])
    cbar = fig.colorbar(
        img, cax=cbaxes, ticks=levels, orientation="horizontal",
        extend='both',
        shrink=0.5
    )
    cbar.set_label(
        r"ACUMULADO DE FLASHES",
        labelpad=-55, fontdict={'size': 14, 'weight': '500'},
    )
    
    
    plt.savefig(f"{const.DIR_RESULTS}/spatial_density_analysis/" \
                "density_map_seasonal.png", 
                    transparent=False, bbox_inches='tight', pad_inches=0.1)

    


if __name__ == "__main__":
    nc_file = '/glm/G05GT1H/GLM_2020_01_hourly_05x05.nc'
    glons, glats, gtimes, gvars = load_NCFile(nc_file)
    
    country_geom, clons, clats, lons_idx, lats_idx = filter_coords_country(
            glons, glats, 'Brazil'
    )
    
    # plot_annual_flash_density(country_geom, glats, glons, lats_idx, lons_idx)
    # plot_monthly_flash_density(country_geom, glats, glons, lats_idx, lons_idx)
    plot_seasonal_flash_density(country_geom, glats, glons, lats_idx, lons_idx)