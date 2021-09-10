"""
Self-Organizing Map Visualization (:mod: `sthunder.visualization`)

This module provides functions to SOM visualization.
"""

import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
from sthunder import constants as const


def plot_weights(SOM, data, dim=0, **kwargs):    
    """
    plot_weights(SOM, data, dim=0, **kwargs)
    
    Create plot neurons weights.
    
    From MiniSom object and a give data, this function generate a plot of 
    neurons weight fitted.

    Parameters
    ----------
    SOM : minisom.MiniSom
        A MiniSom object fitted.
    data : numpy.ndarray
        Data used to fit MiniSom object.
    dim : int, optional
        Index of feature to visualization. The default is 0.
    **kwargs : dict, optional.
        Additional keyword arguments passed to visualization.
            `dpi` : int 
                Dots per inch for plot. The default is 100.
            `width` : int
                Weight in inch for monitor resolution. The default is 956.
            `height` : int
                Height in inch for monitor resolution. The default is 844.8.
            `facecolor` : string
                Backgroud plot color.The default is white.
            
    Returns
    -------
    None.
    
    Examples
    --------
    >>> from sthunder import visualization as viz
    >>> viz.plot_weights(SOM, data, 1)

    """
    dpi = kwargs.get('dpi', 100)
    width = kwargs.get('width', np.round(1366 * 70 / 100))
    height = kwargs.get('height', 768*1.1)
    facecolor = kwargs.get('facecolor', 'white')
    cmap = kwargs.get('cmap', 'coolwarm')
    
    fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), dpi=dpi, 
                           facecolor=facecolor)
    
    ax.set_title(f"{const.TITLE_SINGLE_WEIGHTS_EN} (DIM {dim})", 
                 fontdict=const.STYLE_TITLE)
    weights = SOM._weights
    act_res = SOM.activation_response(data)
    
    img = ax.pcolor(weights[:, :, dim].T, cmap=cmap)
    plt.colorbar(img)
    plt.xticks(np.arange(weights.shape[0]+1))
    plt.yticks(np.arange(weights.shape[1]+1))
    plt.tight_layout()
    
    plt.savefig(
        f"{const.DIR_IMG_CITIES}/weights/weight_dim{str(dim).zfill(5)}.png", 
                transparent=False, bbox_inches='tight', pad_inches=0.1)
    
    return None
    
    
def plot_single_hourly_density_city_map(SOM, df, norm, color_map, alpha_map, 
                                        **kwargs):
    """
    plot_single_density_city_map(SOM, df, norm, color_map, alpha_map, 
                                 **kwargs)
    
    Create plot single hourly density city map.
    
    Create a hourly density activities and inactivities flashes map.

    Parameters
    ----------
    SOM : minisom.MiniSom
        A MiniSom object fitted.
    df : pandas.core.frame.DataFrame
        Pandas DataFrame with structured data having datetimes as index and 
        cities as columns.
    norm : sklearn.preprocessing._data.MinMaxScaler
        Data scaler normalizer.
    color_map : numpy.ndarray
        Matrix with SOM color maps.
    alpha_map: numpy.ndarray
        Matrix with SOM alpha color maps.
    **kwargs : dict, optional.
        Additional keyword arguments passed to visualization.
            `dpi` : int 
                Dots per inch for plot. The default is 100.
            `width` : int
                Weight in inch for monitor resolution. The default is 956.
            `height` : int
                Height in inch for monitor resolution. The default is 844.8.
            `facecolor` : string
                Backgroud plot color.The default is white.
            
    Returns
    -------
    None.
    
    Examples
    --------
    >>> from sthunder import visualization as viz
    >>> viz.plot_single_hourly_density_city_map(SOM, df, norm, color_map, 
                                                alpha_map)

    """
    ngdf = gpd.read_file(
        const.SHP_BRAZIL_CITIES
    ).set_index('nome').loc[df.columns][['geometry']]
    
    c, a = [], []
    for i, (city, row) in enumerate(ngdf.iterrows()):
        winner = SOM.winner(norm.transform(df[[city]].values.T)[0])
        
        c.append(color_map[winner[0]][winner[1]])
        a.append(alpha_map[winner[0]][winner[1]])
        
    ngdf['color'] = c
    ngdf['alpha'] = a
    
    
    dpi = kwargs.get('dpi', 100)
    width = kwargs.get('width', np.round(1366 * 70 / 100))
    height = kwargs.get('height', 768*1.1)
    facecolor = kwargs.get('facecolor', 'white')

    fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), 
                           dpi=dpi, facecolor=facecolor)

    ax.set_title(const.TITLE_SINGLE_DENSITY_CITY_MAP, 
                 fontdict=const.STYLE_TITLE)
    ax.grid(ls='--', alpha=0.5)
    ax.set_xlabel("Longitude [°]")
    ax.set_ylabel("Latitude [°]")

    ngdf[ngdf['color'] == 'red'].plot(cmap='Reds', ec='k', lw=0.1, 
                                      column='alpha', ax=ax)
    ngdf[ngdf['color'] == 'blue'].plot(cmap='Blues', ec='k', lw=0.1, 
                                       column='alpha', ax=ax)

    plt.savefig(f"{const.DIR_IMG_CITIES}/single_density_city_map.png", 
                transparent=False, bbox_inches='tight', pad_inches=0.1)
    
    return None


def plot_neurons_map(color_map, alpha_map, **kwargs):
    dpi = kwargs.get('dpi', 100)
    width = kwargs.get('width', np.round(1366 * 70 / 100))
    height = kwargs.get('height', 768*1.1)
    facecolor = kwargs.get('facecolor', 'white')

    fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), 
                           dpi=dpi, facecolor=facecolor)
    
    for i in range(color_map.shape[0]):
        for j in range(color_map.shape[1]):
            ax.plot([i+.5], [j+.5], color=color_map[i][j],
                      marker='o', markersize=33, alpha=alpha_map[i][j])
    
    ax.set_xlim([0, color_map.shape[0]])
    ax.set_ylim([0, color_map.shape[1]])
        
    