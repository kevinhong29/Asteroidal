import numpy as np
import matplotlib.pyplot as plt
from astroquery.gaia import Gaia
import astropy.units as u
import astropy.table
from astropy.coordinates import SkyCoord
import pandas as pd

class Asteroid(object):
    """
    An asteroid in Gaia.sso_source database with observations

    Args:
        source_id (long): Unique source identifier from gaia_source
        number_mp (long): Minor Planet number attributed by MPC
        denomination (string): Name of asteroid in MPC database

    Attributes:
        source_id (long): Unique source identifier from gaia_source
        number_mp (long): Minor Planet number attributed by MPC
        denomination (string): Name of asteroid in MPC database
        num_of_obs (int): Number of observations for the asteroid 
            that appear in sso_observation
        observations (dataframe): Dataframe of observations from sso_observation. 
            Includes source_id, number_mp, epoch, ra, dec.
    """
    def __init__(self, source_id=0, number_mp=0, denomination=''):
        self.source_id = source_id
        self.num_of_obs = 0
        self.number_mp = number_mp
        self.denomination = denomination
        self.source = astropy.table.Table()
        self.observations = astropy.table.Table()
    
    def set_sso_source(self, sso_source_results):
        """
        Sets attributes of Asteroid object from results of Gaia query in sso_source

        Args:
            sso_source_results (Table): Table of results from query job for gaia.sso_source.
                Includes source_id, num_of_obs, number_mp, denomination.
        
        Returns:
            Table: Table of results from query job including source_id, num_of_obs, number_mp, denomination
        """
        self.source_id = sso_source_results['source_id']
        self.num_of_obs = sso_source_results['num_of_obs']
        self.number_mp = sso_source_results['number_mp']
        self.denomination = sso_source_results['denomination']
        self.source = sso_source_results
        
        return self.source

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
                source_id, number_mp, epoch, ra, dec
                FROM gaiadr2.sso_observation
                WHERE number_mp={number_mp}
                """.format(number_mp=self.number_mp)

        job = Gaia.launch_job(query)
        results = job.get_results()
        print(results)
        self.set_sso_source(results)

test = Asteroid(number_mp=8)
test.get_sso_source_from_number_mp()
print(test.num_of_obs)