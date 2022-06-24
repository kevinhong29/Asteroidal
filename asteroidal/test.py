#%%
import numpy as np
import asteroid as ast
# %%
flora = ast.Asteroid(number_mp=8)
print(flora.observations)
flora.plot_transit(0)
flora.plot_all_transits()
