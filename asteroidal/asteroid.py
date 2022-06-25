import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from astroquery.gaia import Gaia
from astroquery.mpc import MPC

class Asteroid(object):
    """An asteroid in Gaia.sso_source database with observations.

    Asteroid object should be initialized with one of three inputs: number_mp, 
    denomination, or source_id (if more than three are inputed, will prioritize
    initializing in given order). Initialization will query Gaia for the remaining
    attributes unless the asteroid does not exist in Gaia.

    Args:
        source_id (int): Unique source identifier from gaia_source.
        number_mp (int): Minor Planet number attributed by MPC.
        denomination (string): Name of asteroid in MPC database.

    Attributes:
        source_id (int): Unique source identifier from gaia_source.
        number_mp (int): Minor Planet number attributed by MPC.
        denomination (string): Name of asteroid in MPC database.
        num_of_obs (int): Number of observations for the asteroid 
            that appear in sso_observation.
        observations (table): Table of observations from sso_observation. 
            Includes source_id, observation_id, number_mp, epoch, 
            ra, dec, x_gaia, y_gaia, z_gaia.
        transits (ndarray of int): Array of individual transits from observation.
        transit_ccds (ndarray of list of int): Array of lists of ccd detectors activated 
            for an observation for each transit. 
        mpc_data (dict): All data from querying MPC.
        orbit_data (ndarray of float): Array of orbit data (eccentricity, semimajor axis)
            queried from MPC.

    """
    def __init__(self, number_mp=0, denomination='', source_id=0):
        if number_mp > -1:
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
        self.query_mpc()

    def query_source(self, search_col):
        """Queries gaiadr2.sso_source for asteroid given number_mp, 
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
        """Sets attributes of Asteroid object from results of querying gaiadr2.sso_source

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
        """Queries gaiadr2.sso_observation for all observations for specific asteroid object.
        Adds observations attribute

        Returns:
            Table: Table of results from query job including source_id, observation_id,
                number_mp, epoch, ra, dec, x_gaia, y_gaia, z_gaia
        """
        if self.source_id == 0:
            return
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
        """Adds transits and transit_ccds attributes from total observations

        Returns:
            ndarray: Array of int, individual transits from observations
        """
        if self.source_id == 0:
            return
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
        """Plots ra and dec of all observations
        """
        ra = self.observations['ra']
        dec = self.observations['dec']
        plt.scatter(ra, dec)
    
    def get_transit_obs(self, index):
        """Returns ra and dec of observations of a specific transit, 
        specified by index in transits array

        Args:
            index (int): index of transits array
        
        Returns:
            list: Returns list of ra and list of dec
        """
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
        """Plots observations in specific transit, specified by index in transits array.

        Args:
            index (int): index of transits array
        """
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
        """Plots all observations for each transit in single figure.
        """
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

    def query_mpc(self):
        """Queries MPC for all orbit data

        Returns:
            dict: All orbit data in form of dict
        """
        if self.number_mp == 0:
            return
        result = MPC.query_object('asteroid', number=self.number_mp)[0]
        self.mpc_data = result
        self.orbit_data = np.array([
            float(result['semimajor_axis']),
            float(result['eccentricity'])
        ])
        return self.orbit_data
    
    def plot_orbits(self):
        """Plots sun and orbits of planets and asteroid
        """
        fig,ax = plt.subplots(subplot_kw={'projection':'polar'}, figsize=(10, 10))
        planet_orbit(ax)
        orbit(ax, self.orbit_data, 'purple', self.denomination + '({NUM})'.format(NUM=self.number_mp), lw=3)
        plt.title('Orbit of {NAME} ({NUM})'.format(NAME=self.denomination,NUM=self.number_mp))



def orbit(ax, orbit_params, color, olabel, lw=1, alp=1):
    """Plots simple orbit of object given semimajor axis and eccentricity
    in polar coordinates.

    Args:
        ax (axes): Axes to plot onto
        orbit_params (ndarray): Orbit parameters (semimajor axis, eccentricity)
        color (string): Color of orbit plot
        olabel (string): Label of orbit as seen in legend
        lw (float): Linewidth of orbit plot
        a (float within 0-1): Alpha value of orbit plot
    """
    a = orbit_params[0]
    e = orbit_params[1]
    theta = np.arange(0, 2*np.pi, 0.01)
    r = a*(1.-e**2)/(1.+e*np.cos(theta))
    ax.plot(theta, r, c=color, label=olabel, linewidth=lw, alpha=alp)
    ax.legend()

def planet_orbit(ax):
    """Plots sun and orbits of planets

    Args:
        ax (axes): Axes to plot onto
    """
    ax.axis('off')
    mercury = np.array([0.387098, 0.205630])
    venus = np.array([0.723332, 0.006772])
    earth = np.array([1.00, 0.0167086])
    mars = np.array([1.52368055, 0.0934])
    jupyter = np.array([5.2038, 0.0489])

    ax.plot(0, 0, color='yellow', markerfacecolor='yellow', label='Sun', marker='o', markersize=5, markeredgecolor='black')
    orbit(ax, mercury, 'gray', 'Mercury')
    orbit(ax, venus, 'orange', 'Venus')
    orbit(ax, earth, 'green', 'Earth')
    orbit(ax, mars, 'red', 'Mars')
    orbit(ax, jupyter, 'pink', 'Jupyter')

def plot_multiple_orbits(asteroids):
    """Plots orbit of multiple asteroids in array along with sun and planets

    Args:
        asteroids (ndarray of Asteroid object): Array of asteroid objects
    """
    fig,ax = plt.subplots(subplot_kw={'projection':'polar'}, figsize=(10, 10))
    planet_orbit(ax)
    plt.title('Orbits for Multiple Asteroids')
    for asteroid in asteroids:
        if asteroid.number_mp == 0:
            continue
        orbit(ax, asteroid.orbit_data, 'purple', asteroid.denomination + '({NUM})'.format(NUM=asteroid.number_mp), lw=1, alp=0.3)
    