from minisom import MiniSom
import numpy as np


def create_and_fitting_minisom(data, nrow, ncol, weights_init='random',
               training_method='random', n_it = 500, sigma=1.0, lr=0.5, 
               nf='gaussian', topology='rectangular', ad='euclidean', 
               random_seed=42, **kwargs) -> MiniSom:
    """
    create_som(nrow, ncol, input_len, sigma=1.0, lr=0.5, nf='gaussian',
               topology='rectangular', ad='euclidean', random_seed=42,
               **kwargs)

    Parameters
    ----------
    data : numpy.ndarray
        Data for fit SOM.
    nrow : int
        Number of rows in the SOM map.
    ncol : int
        Number of columns in the SOM map..
    weights_init : str
        Weights initialization method. The default is 'random'. The options 
        avaiable are 'random' and 'pca'.
    training_method: str
        Training SOM method. The default is 'random'. The options 
        avaiable are 'random', 'batch' and 'normal'.
    n_it : int
        Number of iterations for SOM fitting.
    sigma : float, optional
        Parameter sigma in SOM map. The default is 1.0.
    lr : float, optional
        Parameter learning rate in SOM map. The default is 0.5.
    nf : str, optional
        Parameter neighborhood function. The default is 'gaussian'. The options 
        avaiable are 'gaussian', 'mexican_hat', 'bubble' and 'triangle'.
    topology : str, optional
        Parameter topology in SOM map. The default is 'rectangular'. The 
        options avaiable are 'rectangular' and 'hexagonal'.
    ad : str, optional
        Parameter activation distance in SOM map. The default is 'euclidean'.
        The options avaiable are 'euclidean', 'cosine', 'manhattan' and 
        'chebyshev'.
    random_seed : int, optional
        The seed for reproducible experiments. The default is 42. None define a 
        random seed.
    **kwargs : dict
        Optional minisom.MiniSom class argument.

    Returns
    -------
    SOM : minisom.MiniSom.
        The SOM object fitted.

    """
    
    SOM = MiniSom(x=nrow, y=ncol, input_len=data.shape[1], sigma=sigma, 
                  learning_rate=lr, neighborhood_function=nf, 
                  topology=topology, activation_distance=ad, 
                  random_seed=random_seed, **kwargs)

    if weights_init == 'random':
        SOM.random_weights_init(data=data)
    elif weights_init == 'pca':
        SOM.pca_weights_init(data=data)
    else:
        raise ValueError(
            f"weights_init argument value must be 'normal' or 'pca'"
        )
        
    if training_method == 'random':
        SOM.train_random(data=data, num_iteration=n_it)
    elif training_method == 'batch':
        SOM.train_batch(data=data, num_iteration=n_it)
    elif training_method == 'normal':
        SOM.train(data=data, num_iteration=n_it)
    else:
        raise ValueError(
            f"training_method argument value must be 'random', 'batch' or " \
                "'normal'"
        )
        
    return SOM


def get_color_and_alpha_maps(SOM, data, thr_v=0.05, thr_p=0.05, 
                             normalize_alpha=True, **kwags) -> tuple:
    """
    get_color_and_alpha_maps(SOM, data, thr_v=0.05, thr_p=0.05, 
                             normalize_alpha=True, **kwags)

    Parameters
    ----------
    SOM : minisom.MiniSom
        A MiniSom object fitted.
    data : numpy.ndarray
        Data used to fit MiniSom object.
    normalize_alpha : bool, optional
        If alpha values must be normalized. The default is True.
    **kwags : TYPE
        DESCRIPTION.

    Returns
    -------
    tuple
        color_map : numpy.ndarray
            Matrix with neurons color map.
        alpha_map : numpy.ndarray
            Matrix with neurons alpha color map.

    """
    
    weights = SOM._weights
    
    color_map = np.full((*SOM._weights.shape[:-1],), 'white')
    alpha_map = np.full((*SOM._weights.shape[:-1],), 0.)
    
    for i in np.arange(weights.shape[0]):
        for j in np.arange(weights.shape[1]):
            w = weights[i, j, :]
            act = len(w[w>thr_v])
            ina = len(w[w<=thr_v])
            
            if act/(act+ina) >= thr_p:
                color_map[i][j] = 'red'
                alpha_map[i][j] = act/(act+ina)
            else:
                color_map[i][j] = 'blue'
                alpha_map[i][j] = act/(act+ina)
                
    if normalize_alpha:
        xb, yb = np.where(color_map == 'blue')
        xr, yr = np.where(color_map == 'red')
    
        alpha_map[xb, yb] = alpha_map[xb, yb]/alpha_map[xb, yb].max()
        alpha_map[xr, yr] = alpha_map[xr, yr]/alpha_map[xr, yr].max()
    
    return color_map, alpha_map