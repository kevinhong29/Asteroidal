import numpy as np
import matplotlib.pyplot as plt
from astroquery.gaia import Gaia
import astropy.units as u
from astropy.coordinates import SkyCoord

class Asteroid(object):
    def __init__(self, source_id=0, number_mp=0, denomination=''):
        self.source_id = source_id
        self.number_mp = number_mp
        self.denomination = denomination
        self.num_of_obs = 0
        self.epoch = np.array([])
        self.ra = np.array([])
        self.dec = np.array([])
    
    def get_sso_source_from_source_id(self):
        pass

# Gets table from Gaia.sso_source using either source_id, number_mp, or denomination as type and respective input as text
def get_sso_source(text, type):
    query = """SELECT
    source_id, num_of_obs, number_mp, denomination
    FROM gaiadr2.sso_source
    WHERE {mpc_type}={mpc_name}
    """.format(mpc_type = type, mpc_name='\'' + text + '\'')
    job = Gaia.launch_job(query)
    r = job.get_results()
    print(r)

get_sso_source('8','number_mp')
