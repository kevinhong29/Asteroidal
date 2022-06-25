from asteroidal import asteroid as ast
import pytest
import matplotlib.pyplot as plt

def test_known_asteroid():
    """
    Tests initialization of known asteroid, that all attributes
    are correctly initialized and methods do not fail.
    """
    flora = ast.Asteroid(number_mp=8)
    flora_name = ast.Asteroid(denomination='flora')
    flora_id = ast.Asteroid(source_id=-4284967216)
    
    assert flora.num_of_obs == flora_name.num_of_obs
    assert flora.num_of_obs == flora_id.num_of_obs
    assert flora.denomination == 'flora'
    assert flora.number_mp == 8
    assert flora.source_id == -4284967216
    assert flora.num_of_obs == 60
    assert len(flora.observations) == flora.num_of_obs
    assert len(flora.transits) == len(flora.transit_ccds)
    assert flora.orbit_data[0] == pytest.approx(2.2017319)
    assert flora.orbit_data[1] == pytest.approx(0.1560672)
    flora.plot_observations()
    flora.plot_transit(0)
    flora.plot_transit(300)
    flora.plot_all_transits()
    flora.plot_orbits()

def test_non_gaia_asteroid():
    """
    Tests initialization of asteroid not found in gaia.sso_source
    """
    blank = ast.Asteroid(number_mp=3)
    
    assert blank.denomination == ''
    assert blank.number_mp == 0
    assert blank.source_id == 0
    assert blank.num_of_obs == 0
    assert len(blank.observations) == blank.num_of_obs
    assert len(blank.transits) == len(blank.transit_ccds)
    assert blank.orbit_data[0] == pytest.approx(0)
    assert blank.orbit_data[1] == pytest.approx(0)
    blank.plot_observations()
    blank.plot_transit(0)
    blank.plot_transit(300)
    blank.plot_all_transits()
    blank.plot_orbits()


def test_functions():
    """
    Tests functions in module that plot orbits with given ax
    """
    fig, ax = plt.subplots(subplot_kw={'projection':'polar'}, figsize=(10, 10))
    ast.planet_orbit(ax)
    ast.orbit(ax, [3.3, 0.5], color='b', olabel='test', lw=1.3, alp=0.5)

    asteroids = []
    for i in range(8, 30):
        asteroid = ast.Asteroid(number_mp=i)
        if asteroid.number_mp != 0:
            asteroids.append(asteroid)
    ast.plot_multiple_orbits(asteroids, ax)

def test_blank_asteroid_orbits():
    asteroids = []
    for i in range(0,10):
        asteroid = ast.Asteroid()
        asteroids.append(asteroid)
    ast.plot_multiple_orbits(asteroids)