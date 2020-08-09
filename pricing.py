#from marketData import marketData
import pandas_market_calendars as mcal
import numpy as np
from scipy import optimize
from scipy import stats
#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
#from matplotlib.colors import LinearSegmentedColormap
#from parula import parula

#parula_map = LinearSegmentedColormap.from_list('parula', parula())

class option():
    #dayOffset=1 means 1 day in future
    def __init__(self, otype, S0, K, marketPrice=None, T=None, expDay=None, vol=None, r=0.025):
        self.S0=S0
        self.K=K
        self.r=r
        self.otype=otype.lower()
        self.daysInYear = 252
        
        if T is None and expDay is None:
            print('Please enter days to expiry or expiration day')
        elif T is None:
            expDay = np.datetime64(expDay)
            nyse = mcal.get_calendar('NYSE')
            self.T= (np.busday_count(np.datetime64('today'), expDay, holidays=nyse.holidays().holidays)+1)/self.daysInYear
        else:
            self.T=T
        
        if marketPrice is None and vol is None:
            print('Please enter either market price or implied vol of option')
        elif marketPrice is None:
            self.vol=vol
            self.marketPrice=self.price()
        elif vol is None:
            self.marketPrice=marketPrice
            self.vol=self.IV()
    
    def d1d2(self, S0=None, K=None, vol=None, r=None, T=None):
        if S0 is None:
            S0 = self.S0
        if K is None:
            K = self.K
        if vol is None:
            vol = self.vol
        if r is None:
            r = self.r
        if T is None:
            T = self.T
        d1 = (np.log(S0/K)+(r + vol**2/2)*T)/(vol*np.sqrt(T))
        d2 = d1-vol*np.sqrt(T)
        return d1, d2
    
    def price(self, S0=None, K=None, vol=None, r=None, T=None):
        if S0 is None:
            S0 = self.S0
        if K is None:
            K = self.K
        if vol is None:
            vol = self.vol
        if r is None:
            r = self.r
        if T is None:
            T = self.T
        d1, d2 = self.d1d2(S0, K, vol, r, T)
        if self.otype == 'call':
            return S0*stats.norm.cdf(d1)-K*np.exp(-r*T)*stats.norm.cdf(d2)
        elif self.otype == 'put':
            return K*np.exp(-r*T)*stats.norm.cdf(-d2) - S0*stats.norm.cdf(-d1)
    
    def IV(self):
        c = lambda x: (self.price(vol=x)-self.marketPrice)**2
        x = 0.2
        res = optimize.minimize(c, x)
        return res.x[0]
    
    def delta(self, S0=None, K=None, vol=None, r=None, T=None):
        if S0 is None:
            S0 = self.S0
        if K is None:
            K = self.K
        if vol is None:
            vol = self.vol
        if r is None:
            r = self.r
        if T is None:
            T = self.T
        d1, d2 = self.d1d2(S0, K, vol, r, T)
        if self.otype == 'call':
            return stats.norm.cdf(d1)
        elif self.otype == 'put':
            return stats.norm.cdf(d1) - 1
    
    def thetaperday(self, S0=None, K=None, vol=None, r=None, T=None):
        return self.theta()/self.daysInYear
    
    def theta(self, S0=None, K=None, vol=None, r=None, T=None):
        if S0 is None:
            S0 = self.S0
        if K is None:
            K = self.K
        if vol is None:
            vol = self.vol
        if r is None:
            r = self.r
        if T is None:
            T = self.T
        d1, d2 = self.d1d2(S0, K, vol, r, T)
        if self.otype == 'call':
            return (-(S0*stats.norm.pdf(d1)*vol)/(2*np.sqrt(T)) - r*K*np.exp(-r*T)*stats.norm.cdf(d2))
        elif self.otype == 'put':
            return (-(S0*stats.norm.pdf(d1)*vol)/(2*np.sqrt(T)) + r*K*np.exp(-r*T)*stats.norm.cdf(-d2))
        
    def gamma(self, S0=None, K=None, vol=None, r=None, T=None):
        if S0 is None:
            S0 = self.S0
        if K is None:
            K = self.K
        if vol is None:
            vol = self.vol
        if r is None:
            r = self.r
        if T is None:
            T = self.T
        d1, d2 = self.d1d2(S0, K, vol, r, T)
        return (stats.norm.pdf(d1)/(S0*vol*np.sqrt(T)))
    
    def vega(self, S0=None, K=None, vol=None, r=None, T=None):
        if S0 is None:
            S0 = self.S0
        if K is None:
            K = self.K
        if vol is None:
            vol = self.vol
        if r is None:
            r = self.r
        if T is None:
            T = self.T
        d1, d2 = self.d1d2(S0, K, vol, r, T)
        return S0*np.sqrt(T)*stats.norm.pdf(d1)
    
    def rho(self, S0=None, K=None, vol=None, r=None, T=None):
        if S0 is None:
            S0 = self.S0
        if K is None:
            K = self.K
        if vol is None:
            vol = self.vol
        if r is None:
            r = self.r
        if T is None:
            T = self.T
        d1, d2 = self.d1d2(S0, K, vol, r, T)
        if self.otype == 'call':
            return K*T*np.exp(-r*T)*stats.norm.cdf(d2)
        elif self.otype == 'put':
            return -K*T*np.exp(-r*T)*stats.norm.cdf(-d2)
    
    #toSweep dictionary with variables to sweep as key and value as (min, max, steps)
    def sweep(self, toSweep):
        inps = {'S0':self.S0, 'K':self.K, 'vol':self.vol, 'r':self.r, 'T':self.T}
        vectors = dict([(k, np.linspace(toSweep[k][0], toSweep[k][1], toSweep[k][2])) for k in toSweep if k in ('S0', 'K', 'vol', 'r', 'T')])
        scalars = dict([(k, inps[k]) for k in inps if k not in vectors])
        if len(toSweep) == 1:
            out = vectors.values[0]
        if len(toSweep) == 2:
            out = np.meshgrid(list(vectors.values())[0], list(vectors.values())[1])
        if len(toSweep) == 3:
            out = np.meshgrid(list(vectors.values())[0], list(vectors.values())[1], list(vectors.values())[2])
        grids = dict([(k, out[i]) for i, k in enumerate(vectors)])
        combined = {**grids, **scalars}
            
        price = self.price(combined['S0'], combined['K'], combined['vol'], combined['r'], combined['T'])
        delta = self.delta(combined['S0'], combined['K'], combined['vol'], combined['r'], combined['T'])
        theta = self.theta(combined['S0'], combined['K'], combined['vol'], combined['r'], combined['T'])
        gamma = self.gamma(combined['S0'], combined['K'], combined['vol'], combined['r'], combined['T'])
        vega = self.vega(combined['S0'], combined['K'], combined['vol'], combined['r'], combined['T'])
        rho = self.rho(combined['S0'], combined['K'], combined['vol'], combined['r'], combined['T'])
        return combined['S0'], combined['K'], combined['vol'], combined['r'], combined['T'], price, delta, theta, gamma, vega, rho 
