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
    
    def set_sso_source(self, sso_source_results):
        self.source_id = sso_source_results['source_id']
        self.num_of_obs = sso_source_results['num_of_obs']
        self.number_mp = sso_source_results['number_mp']
        self.denomination = sso_source_results['denomination']

    def get_sso_source_from_source_id(self):
        query = """SELECT
                source_id, num_of_obs, number_mp, denomination
                FROM gaiadr2.sso_source
                WHERE source_id={source_id}
                """.format(source_id=self.source_id)

        job = Gaia.launch_job(query)
        results = job.get_results()
        print(results)
        self.set_sso_source(results)
        
    
    def get_sso_source_from_number_mp(self):
        query = """SELECT
                source_id, num_of_obs, number_mp, denomination
                FROM gaiadr2.sso_source
                WHERE number_mp={number_mp}
                """.format(number_mp=self.number_mp)

        job = Gaia.launch_job(query)
        results = job.get_results()
        print(results)
        self.set_sso_source(results)

    def get_sso_source_from_denomination(self):
        query = """SELECT
                source_id, num_of_obs, number_mp, denomination
                FROM gaiadr2.sso_source
                WHERE denomination={denomination}
                """.format(denomination=self.denomination)

        job = Gaia.launch_job(query)
        results = job.get_results()
        print(results)
        self.set_sso_source(results)

    def get_sso_observation_from_number_mp(self):
        query = """SELECT
                source_id, num_of_obs, number_mp, denomination
                FROM gaiadr2.sso_source
                WHERE denomination={denomination}
                """.format(denomination=self.denomination)

        job = Gaia.launch_job(query)
        results = job.get_results()
        print(results)
        self.set_sso_source(results)

test = Asteroid(number_mp=8)
test.get_sso_source_from_number_mp()
print(test.num_of_obs)