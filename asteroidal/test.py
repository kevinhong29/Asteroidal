#import asteroid as ast
#from pprint import pprint
# test = ast.Asteroid(number_mp=8)
# test.query_mpc()
# test.plot_orbits()

#%%
import matplotlib.pyplot as plt
import numpy as np
import asteroid as ast
#%%
flora = ast.Asteroid(number_mp=8)
print(flora.source_id)
# %%
# flora = ast.Asteroid(number_mp=8)
# flora.query_mpc()
# flora.plot_orbits()
# print(flora.orbit_data)
# %%
# test = ast.Asteroid(number_mp=43)
# test.query_mpc()
# test.plot_orbits()
#print(test.orbit_data)
# %%
# asteroids = np.array([flora, test])
# ast.plot_multiple_orbits(asteroids)
# %%
ast_list = []
for num in range(0,50):
    asteroid = ast.Asteroid(number_mp=num)
    if asteroid.number_mp != 0:
        ast_list.append(asteroid)
asteroids = np.array(ast_list)
ast.plot_multiple_orbits(asteroids)
# %%
for asteroid in asteroids:
    asteroid.plot_all_transits()
# %%
