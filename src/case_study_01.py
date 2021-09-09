# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
from dask import dataframe as dd
from minisom import MiniSom
from sklearn.preprocessing import MinMaxScaler
import SimpSOM as sps
import geopandas as gpd
from sthunder import constants as const



def plot_weights(som, data):
    weights = som.get_weights()
    act_res = som.activation_response(data)
    
    plt.pcolor(weights[:, :, 0].T, cmap='coolwarm')
    plt.xticks(np.arange(weights.shape[0]+1))
    plt.yticks(np.arange(weights.shape[0]+1))
    plt.tight_layout()
    
    
def plot_neurons(som, data):
    weights = som.get_weights()
    
    Z = np.full((*som._weights.shape[:-1],), '')
    thr = 0.05
    plt.figure(figsize=(10, 10))
    color = np.full((*som._weights.shape[:-1],), 'white')
    alpha = np.full((*som._weights.shape[:-1],), 0.)
    
    for i in np.arange(weights.shape[0]):
        for j in np.arange(weights.shape[1]):
            # argmax= np.argmax(weights[i, j, :])
            w = weights[i, j, :]
            act = len(w[w>thr])
            ina = len(w[w<=thr])
            
            # print(act, ina)
            if act/(act+ina) >= thr:
                # Z[i][j] = 'red'
                color[i][j] = 'red'
                alpha[i][j] = act/(act+ina)
                plt.plot([j+.5], [i+.5], 'o', color="red",
                          marker='o', markersize=33, alpha=act/(act+ina))
            else:
                # Z[i][j] = 'blue'
                color[i][j] = 'blue'
                alpha[i][j] = act/(act+ina)
                plt.plot([j+.5], [i+.5], 'o', color="blue",
                          marker='o', markersize=33, alpha=ina/(act+ina))
    
    # plt.imshow(Z)
    plt.xlim([0, weights.shape[0]])
    plt.ylim([0, weights.shape[1]])
    
    return color, alpha


def plot_single_density_city_map(df, color, alpha):
    ngdf = gpd.read_file(
        const.SHP_BRAZIL_CITIES
    ).set_index('nome').loc[df.columns][['geometry']]
    
    c, a = [], []
    for i, (city, row) in enumerate(ngdf.iterrows()):
        winner = som.winner(norm.transform(df[[city]].values.T)[0])
        
        c.append(color[winner[0]][winner[1]])
        a.append(alpha[winner[0]][winner[1]])
        
    ngdf['color'] = c
    ngdf['alpha'] = a
        
    
    
    fig, ax = plt.subplots(figsize=(10, 10))

    ax.grid(ls='--', alpha=0.5)
    ax.set_xlabel("Longitude [°]")
    ax.set_xlabel("Latitude [°]")

    ngdf[ngdf['color'] == 'red'].plot(cmap='Reds_r', column='alpha', ax=ax)
    ngdf[ngdf['color'] == 'blue'].plot(cmap='Blues_r', column='alpha', ax=ax)
    
    plt.savefig(f"{const.DIR_IMG_CITIES}/single_density_city_map.png")
    
    
    


df = dd.read_csv(
    "/glm/city_state.csv"
).groupby(
    ['city', 'datetime']
).aggregate(
    {'total': 'sum'}
).reset_index().compute().pivot(
     columns='city', index='datetime', values='total'
).reset_index()
    

df['datetime'] = dd.to_datetime(df['datetime'])
df = df.set_index('datetime')

norm = MinMaxScaler(feature_range=(0, 1))
data = norm.fit_transform(df.values.T)

nr, nc = 13, 13
sigma = 3
lr = 0.5
neigh_func = 'triangle'
topology = 'rectangular'


som = MiniSom(
    x=nr, y=nc, input_len=data.shape[1], sigma=sigma, 
    learning_rate=lr, neighborhood_function=neigh_func,
    topology=topology,
    random_seed=42
)

som.random_weights_init(data)
som.train_random(data=data, num_iteration=500)


color, alpha = plot_neurons(som, data)
plot_single_density_city_map(df, color, alpha)


dpi = 100
width = np.round(1366 * 70 / 100)
height = 768*1.1

fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), dpi=dpi, facecolor='w')

ax.set_title(const.TITLE_SINGLE_DENSITY_CITY_MAP, fontdict=const.STYLE_TITLE)
ax.grid(ls='--', alpha=0.5)
ax.set_xlabel("Longitude [°]")
ax.set_ylabel("Latitude [°]")

ngdf[ngdf['color'] == 'red'].plot(cmap='Reds_r', column='alpha', ax=ax)
ngdf[ngdf['color'] == 'blue'].plot(cmap='Blues_r', column='alpha', ax=ax)

plt.savefig(f"{const.DIR_IMG_CITIES}/single_density_city_map.png", 
            transparent=False, bbox_inches='tight', pad_inches=0.1)