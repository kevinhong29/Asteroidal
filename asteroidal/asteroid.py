import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from astroquery.gaia import Gaia

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
        transits (ndarray of int): Array of individual transits from observation.
        transit_ccds (ndarray of list of int): Array of lists of ccd detectors activated 
            for an observation for each transit. 
    """
    def __init__(self, number_mp=1, denomination='', source_id=0):
        if number_mp > 0:
            self.number_mp = number_mp
            self.query_source('number_mp')
        elif denomination != '':
            self.denomination = denomination
            self.query_source('denomination')
        elif source_id != 0:
            self.source_id = source_id
            self.query_source('source_id')
        self.query_observations()
        self.set_transits()

    def query_source(self, search_col):
        """
        Queries gaiadr2.sso_source for asteroid given number_mp, 
        denomination, or source_id.

        Args:
            search_col (string): Specifies which column name to query by. 
                Either 'number_mp', 'denomination', or 'source_id'
        
        Returns:
            Table: Table of results from query job including source_id, num_of_obs, number_mp, denomination
        """
        if search_col == 'number_mp':
            value = self.number_mp
        elif search_col == 'denomination':
            value = self.denomination
        elif search_col == 'source_id':
            value = self.source_id
        else:
            print('Not Valid Column Name.')
            return
            
        query = """SELECT
                source_id, num_of_obs, number_mp, denomination
                FROM gaiadr2.sso_source
                WHERE {search}={val}
                """.format(search=search_col, val=value)
        job = Gaia.launch_job(query)
        results = job.get_results()
        return self.set_sso_source(results)

    def set_sso_source(self, sso_source_results):
        """
        Sets attributes of Asteroid object from results of querying gaiadr2.sso_source

        Args:
            sso_source_results (Table): Table of results from query job for gaia.sso_source.
                Includes source_id, num_of_obs, number_mp, denomination. If table is empty, 
                does not intialize attributes.
        
        Returns:
            Table: Table of results from query job including source_id, num_of_obs, number_mp, denomination
        """
        if len(sso_source_results) < 1:
            print('Asteroid does not exist in Gaia.')
            self.source_id = 0
            self.number_mp = 0
            self.num_of_obs = 0
            self.denomination = ''
            self.source = sso_source_results
            return self.source
        self.source_id = sso_source_results['source_id'][0]
        self.num_of_obs = sso_source_results['num_of_obs'][0]
        self.number_mp = sso_source_results['number_mp'][0]
        self.denomination = sso_source_results['denomination'][0]
        self.source = sso_source_results
        
        return self.source

    def query_observations(self):
        """
        Queries gaiadr2.sso_observation for all observations for specific asteroid object.
        Adds observations attribute

        Returns:
            Table: Table of results from query job including source_id, observation_id,
                number_mp, epoch, ra, dec, x_gaia, y_gaia, z_gaia
        """
        query = """SELECT
                source_id, observation_id, number_mp, epoch, ra, dec, x_gaia, y_gaia, z_gaia
                FROM gaiadr2.sso_observation
                WHERE source_id={source_id}
                """.format(source_id=self.source_id)

        job = Gaia.launch_job(query)
        results = job.get_results()
        self.observations = results
        return self.observations

    def set_transits(self):
        """
        Adds transits and transit_ccds attributes from total observations

        Returns:

        """
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
        return self.transits
    
    def plot_observations(self):
        ra = self.observations['ra']
        dec = self.observations['dec']
        plt.scatter(ra, dec)
    
    def get_transit_obs(self, index):
        if index >= len(self.transits):
            print('Index larger than transit array length.')
            return [[],[]]
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
        if len(ra) == 0 or len(dec) == 0:
            print('No transits observed.')
            return
        d_ra = 3600000*(ra - np.min(ra))
        d_dec = 3600000*(dec - np.min(dec))
        ccds = self.transit_ccds[index]
        fig = plt.figure()
        for i in range(0,len(ccds)):
            plt.scatter(d_ra[i], d_dec[i], color=(1-ccds[i]/10, ccds[i]/10, 1))
            plt.xlabel(r'$\Delta$' + 'RA (mas)')
            plt.ylabel(r'$\Delta$' + 'DEC (mas)')
            plt.title('{NAME} ({NUM})\nTransit {TRANSIT:.0f} at \n(RA, DEC) = ({RA}, {DEC}) in deg'.format(NAME=self.denomination,NUM=self.number_mp,TRANSIT=self.transits[index],RA=np.min(ra), DEC=np.min(dec)))

    def plot_all_transits(self):
        numTransits = len(self.transits)
        nFig = int(np.ceil(np.sqrt(numTransits)))
        if nFig == 0:
            print('No transits observed.')
            return
        fig, ax = plt.subplots(nrows=nFig, ncols=nFig, figsize=(2+2*nFig, 2+2*nFig))
        
        for index in range(0,nFig**2):
            row = int(index / nFig)
            col = int(index % nFig)
            if index < numTransits:
                ccds = self.transit_ccds[index]
                ra, dec = self.get_transit_obs(index)
                d_ra = 3600000*(ra - np.min(ra))
                d_dec = 3600000*(dec - np.min(dec))
                for i in range(0,len(ccds)):
                    curax = ax[row,col]
                    curax.scatter(d_ra[i], d_dec[i], color=(1-ccds[i]/10, ccds[i]/10, 1))
                    plt.xticks(fontsize=20/nFig)
                    plt.yticks(fontsize=20/nFig)
            else:
                fig.delaxes(ax[row][col])

        numRows = int((numTransits-1)/nFig) + 1
        emptyRows = nFig - numRows
        fig.text(0.5, 0.02+emptyRows/nFig, r'$\Delta$' + 'RA (mas)', ha='center')
        fig.text(0.07, 0.5, r'$\Delta$' + 'DEC (mas)', va='center', rotation='vertical')
        fig.text(0.5, 0.92, '{NAME} ({NUM})\nAll Transits Observed By Gaia'.format(NAME=self.denomination, NUM=self.number_mp), ha='center')



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