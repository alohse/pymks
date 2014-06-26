from pymks import MKSRegressionModel
from pymks import ElasticFESimulation
import numpy as np
from sklearn import metrics
mse = metrics.mean_squared_error
from pymks.datasets import make_elasticFEstrain_delta
from pymks.datasets import make_elasticFEstrain_random

def test_ElasticFESimulation_2D():
    nx = 5
    ii = (nx - 1) / 2
    X = np.zeros((1, nx, nx), dtype=int)
    X[0, ii, ii] = 1
    model = ElasticFESimulation(elastic_modulus=(1., 10.), poissons_ratio=(0.3, 0.3))
    strains = model.get_response(X, slice(None))
    solution = (1.518e-1, -1.672e-2, 0.)
    assert np.allclose(strains[0, ii, ii], solution, rtol=1e-3)

def test_ElasticFESimulation_3D():
    nx = 4
    ii = (nx - 1) / 2
    X = np.zeros((1, nx, nx, nx), dtype=int)
    X[0, :, ii] = 1
    model = ElasticFESimulation(elastic_modulus=(1., 10.), poissons_ratio=(0., 0.))
    strains = model.get_response(X, slice(None))
    solution = [1., 0., 0., 0., 0., 0.]
    assert np.allclose([np.mean(strains[0,...,i]) for i in range(6)], solution)

def get_delta_data(nx, ny):

    return make_elasticFEstrain_delta(elastic_modulus=(1, 1.1), 
                                      poissons_ratio=(0.3, 0.3), 
                                      size=(nx, ny),
                                      strain_index=slice(None))

def get_random_data(nx, ny):
    np.random.seed(8)
    return make_elasticFEstrain_random(elastic_modulus=(1., 1.1),
                                poissons_ratio=(0.3, 0.3), n_samples=1,
                                size=(nx, ny), strain_index=slice(None))

def rollzip(*args):
    return zip(*tuple(np.rollaxis(x, -1) for x in args))

def test_MKSelastic_delta():
    nx, ny = 21, 21
    X, y_prop = get_delta_data(nx, ny)
    
    for y_test in np.rollaxis(y_prop, -1):
        model = MKSRegressionModel(Nbin=2)
        model.fit(X, y_test)
        y_pred = model.predict(X)
        assert np.allclose(y_pred, y_test, rtol=1e-3, atol=1e-3)

def test_MKSelastic_random():
    nx, ny = 21, 21
    i = 3
    X_delta, strains_delta = get_delta_data(nx, ny)
    X_test, strains_test = get_random_data(nx, ny)

    for y_delta, y_test in rollzip(strains_delta, strains_test):
        model = MKSRegressionModel(Nbin=2)
        model.fit(X_delta, y_delta)
        y_pred = model.predict(X_test)
        assert np.allclose(y_pred[0, i:-i], y_test[0, i:-i], rtol=1e-2, atol=6.1e-3)

def test_resize_pred():
    nx, ny = 21, 21
    i = 3
    resize = 3
    X_delta, strains_delta = get_delta_data(nx, ny)
    X_test, strains_test = get_random_data(nx, ny)
    X_big_test, strains_big_test = get_random_data(resize * nx, resize * ny)

    for y_delta, y_test, y_big_test in rollzip(strains_delta, strains_test, strains_big_test):
        model = MKSRegressionModel(Nbin=2)
        model.fit(X_delta, y_delta)
        y_pred = model.predict(X_test)
        assert np.allclose(y_pred[0, i:-i], y_test[0, i:-i], rtol=1e-2, atol=6.1e-3)
        model.resize_coeff((resize * nx, resize * ny))
        y_big_pred = model.predict(X_big_test)
        assert np.allclose(y_big_pred[0, resize * i:-i * resize], y_big_test[0, resize * i:-i * resize],  rtol=1e-2, atol=6.1e-2)
        
def test_resize_coeff():
    nx, ny = 21, 21
    resize = 3
    X_delta, strains_delta = get_delta_data(nx, ny)
    X_big_delta, strains_big_delta =  get_delta_data(resize * nx, resize * ny)
   
    
    for y_delta, y_big_delta in rollzip(strains_delta, strains_big_delta):
         model = MKSRegressionModel(Nbin=2)
         big_model = MKSRegressionModel(Nbin=2)
         model.fit(X_delta, y_delta)
         big_model.fit(X_big_delta, y_big_delta)
         model.resize_coeff((resize * nx, resize * ny))
         assert np.allclose(model.coeff, big_model.coeff, rtol=1e-2, atol=2.1e-3)
    

if __name__ == '__main__':
    test_MKSelastic_random()