import matplotlib
from matplotlib import projections
import numpy as np
import matplotlib.pyplot as plt
from astroquery.gaia import Gaia
import astropy.units as u
import astropy.table
from astropy.coordinates import SkyCoord
import pandas as pd
from mpl_toolkits import mplot3d

class Asteroid(object):
    """
    An asteroid in Gaia.sso_source database with observations.

    Args:
        source_id (long): Unique source identifier from gaia_source.
        number_mp (long): Minor Planet number attributed by MPC.
        denomination (string): Name of asteroid in MPC database.

    Attributes:
        source_id (long): Unique source identifier from gaia_source.
        number_mp (long): Minor Planet number attributed by MPC.
        denomination (string): Name of asteroid in MPC database.
        num_of_obs (int): Number of observations for the asteroid 
            that appear in sso_observation.
        observations (table): Table of observations from sso_observation. 
            Includes source_id, observation_id, number_mp, epoch, 
            ra, dec, x_gaia, y_gaia, z_gaia.
        transits (array): Array of individual transits from observation.
        transit_ccds (array): Array of lists of ccd detectors activated 
            for an observation for each transit. 
    """
    def __init__(self, source_id=0, number_mp=0, denomination=''):
        self.source_id = source_id
        self.num_of_obs = 0
        self.number_mp = number_mp
        self.denomination = denomination
        self.source = astropy.table.Table()
        self.observations = astropy.table.Table()
        self.transits = np.array([])
        self.transit_ccds = np.array([])
    
    def set_sso_source(self, sso_source_results):
        """
        Sets attributes of Asteroid object from results of Gaia query in sso_source

        Args:
            sso_source_results (Table): Table of results from query job for gaia.sso_source.
                Includes source_id, num_of_obs, number_mp, denomination.
        
        Returns:
            Table: Table of results from query job including source_id, num_of_obs, number_mp, denomination
        """
        self.source_id = sso_source_results['source_id'][0]
        self.num_of_obs = sso_source_results['num_of_obs'][0]
        self.number_mp = sso_source_results['number_mp'][0]
        self.denomination = sso_source_results['denomination'][0]
        self.source = sso_source_results
        
        return self.source

    def query_sso_source_from_source_id(self):
        query = """SELECT
                source_id, num_of_obs, number_mp, denomination
                FROM gaiadr2.sso_source
                WHERE source_id={source_id}
                """.format(source_id=self.source_id)

        job = Gaia.launch_job(query)
        results = job.get_results()
        print(results)
        self.set_sso_source(results)
        
    
    def query_sso_source_from_number_mp(self):
        query = """SELECT
                source_id, num_of_obs, number_mp, denomination
                FROM gaiadr2.sso_source
                WHERE number_mp={number_mp}
                """.format(number_mp=self.number_mp)

        job = Gaia.launch_job(query)
        results = job.get_results()
        print(results)
        self.set_sso_source(results)

    def query_sso_source_from_denomination(self):
        query = """SELECT
                source_id, num_of_obs, number_mp, denomination
                FROM gaiadr2.sso_source
                WHERE denomination={denomination}
                """.format(denomination=self.denomination)

        job = Gaia.launch_job(query)
        results = job.get_results()
        print(results)
        self.set_sso_source(results)

    def query_observations(self):
        query = """SELECT
                source_id, observation_id, number_mp, epoch, ra, dec, x_gaia, y_gaia, z_gaia
                FROM gaiadr2.sso_observation
                WHERE source_id={source_id}
                """.format(source_id=self.source_id)

        job = Gaia.launch_job(query)
        results = job.get_results()
        print(results)
        self.observations = results

    def set_transits(self):
        observation_id = self.observations['observation_id'].data

        transit_id = observation_id / 10
        transit_id = np.unique(transit_id)
        transit_ccd = []
        ccd = []
        for i in transit_id:
            for j in observation_id:
                if i == (j / 10):
                    ccd.append(j % 10)
            transit_ccd.append(ccd.copy())
            ccd.clear()
        self.transits = transit_id
        self.transit_ccds = np.array(transit_ccd, dtype=object)
    
    def plot_observations(self):
        ra = self.observations['ra']
        dec = self.observations['dec']
        plt.scatter(ra, dec)
    
    def get_transit_obs(self, index):
        if index >= len(self.transits):
            print('Index larger than transit array length')
        transit = self.transits[index]
        ra = []
        dec = []
        for observation in self.observations:
            if observation['observation_id'] / 10 == transit:
                ra.append(observation['ra'])
                dec.append(observation['dec'])
        return [ra,dec]

    def plot_transit(self, index):
        ra, dec = self.get_transit_obs(index)
        ra = ra * 3600000
        dec = dec * 3600000
        ccds = self.transit_ccds[index]
        fig = plt.figure()
        for i in range(0,len(ccds)):
            plt.scatter(ra[i], dec[i], color=(1-ccds[i]/10, ccds[i]/10, 1))
            plt.xlabel('RA (mas)')

    def plot_all_transits(self):
        figSize = int(np.ceil(np.sqrt(len(self.transits))))
        fig, ax = plt.subplots(nrows=figSize, ncols=figSize, figsize=(7,7))

        for index in range(0,len(self.transits)):
            row = int(index / figSize)
            col = int(index % figSize)
            ccds = self.transit_ccds[index]
            ra, dec = self.get_transit_obs(index)
            ra = ra * 3600000
            dec = dec * 3600000
            for i in range(0,len(ccds)):
                curax = ax[row,col]
                curax.scatter(ra[i], dec[i], color=(1-ccds[i]/10, ccds[i]/10, 1))



test = Asteroid(number_mp=8)
test.query_sso_source_from_number_mp()
test.query_observations()
test.set_transits()
test.plot_transit(0)

#%%
import asteroid

# x = test.observations['x_gaia']
# y = test.observations['y_gaia']
# z = test.observations['z_gaia']


# fig, ax = plt.subplots(nrows=1, ncols=2)
# ax[0] = plt.axes(projection = '3d')
# ax[0].scatter3D(x, y, z)
# ra = test.observations['ra']
# dec = test.observations['dec']
# ax[1].scatter(ra, dec)
# #%%
# import asteroid
# # %%

# query = """SELECT
#         source_id, number_mp, epoch, ra, dec
#         FROM gaiadr2.sso_observation
#         WHERE number_mp={number_mp}
#         """.format(number_mp=self.number_mp)

# job = Gaia.launch_job(query)
# results = job.get_results()
# print(results)
#t = Gaia.load_table('gaiadr3.')