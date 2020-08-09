#from marketData import marketData
import pandas_market_calendars as mcal
import numpy as np
from scipy import optimize
from scipy import stats

class option():
    def __init__(self, otype, S0, K, q=0, marketPrice=None, T=None, expDay=None, vol=None, r=0.025):
        self.S0=S0
        self.K=K
        self.r=r
        self.otype=otype.lower()
        self.daysInYear = 252
        self.q=q
        
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
            
    def inpcheck(self, S0=None, K=None, vol=None, r=None, T=None, q=0):
        if S0 is None: S0 = self.S0
        if K is None: K = self.K
        if vol is None: vol = self.vol
        if r is None: r = self.r
        if T is None: T = self.T
        return S0, K, vol, r, T, q
    
    def d1d2(self, S0=None, K=None, vol=None, r=None, T=None, q=0):
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1 = (np.log(S0/K)+(r - q + vol**2/2)*T)/(vol*np.sqrt(T))
        d2 = d1-vol*np.sqrt(T)
        return d1, d2
    
    def price(self, S0=None, K=None, vol=None, r=None, T=None, q=0):
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        if self.otype == 'call':
            return S0*np.exp(-q*T)*stats.norm.cdf(d1)-K*np.exp(-r*T)*stats.norm.cdf(d2)
        elif self.otype == 'put':
            return K*np.exp(-r*T)*stats.norm.cdf(-d2) - S0*np.exp(-q*T)*stats.norm.cdf(-d1)
    
    def IV(self):
        c = lambda x: (self.price(vol=x)-self.marketPrice)**2
        x = 0.2
        res = optimize.minimize(c, x)
        return res.x[0]
    
    #variables
    #V - option price (referred to as price in code)
    #S - underlying stock price (referred to as S0 in code)
    #K - strike price
    #vol - volatility
    #r - risk free rate
    #q - annual dividend yield
    #T - time to expiration in years
    
    
    def delta(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #dV/dS
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        if self.otype == 'call':
            return np.exp(-q*T)*stats.norm.cdf(d1)
        elif self.otype == 'put':
            return np.exp(-q*T)*stats.norm.cdf(-d1)
        
    def vega(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #dV/dvol
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        return np.exp(-q*T)*S0*np.sqrt(T)*stats.norm.pdf(d1)
    
    def theta(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #-dV/dT
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        if self.otype == 'call':
            return -(np.exp(-q*T)*S0*stats.norm.pdf(d1)*vol)/(2*np.sqrt(T)) - r*K*np.exp(-r*T)*stats.norm.cdf(d2) + q*S0*np.exp(-q*T)*stats.norm.cdf(d1) 
        elif self.otype == 'put':
            return -(np.exp(-q*T)*S0*stats.norm.pdf(-d1)*vol)/(2*np.sqrt(T)) + r*K*np.exp(-r*T)*stats.norm.cdf(-d2) - q*S0*np.exp(-q*T)*stats.norm.cdf(-d1) 
    
    def rho(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #dV.dr
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        if self.otype == 'call':
            return K*T*np.exp(-r*T)*stats.norm.cdf(d2)
        elif self.otype == 'put':
            return -K*T*np.exp(-r*T)*stats.norm.cdf(-d2)
        
    def omega(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #aka lambda - leverage = dV/dS * S/V
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        return self.delta(S0, K, vol, r, T, q) * (S0/self.price(S0, K, vol, r, T, q))
    
    def gamma(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #d^2V/dS^2
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        return np.exp(-q*T)*(stats.norm.pdf(d1)/(S0*vol*np.sqrt(T)))
    
    def vanna(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #d^2V/dSdvol
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        return -np.exp(-q*T)*stats.norm.pdf(d1)*d2/vol
    
    def charm(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #-d^2V/dTdS
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        if self.otype == 'call':
            return q*np.exp(-q*T)*stats.norm.cdf(d1) - np.exp(-q*T)*stats.norm.pdf(d1)*((2*(r-q)*T - d2*vol*np.sqrt(T))/(2*T*vol*np.sqrt(T)))
        elif self.otype == 'put':
            return -q*np.exp(-q*T)*stats.norm.cdf(-d1) - np.exp(-q*T)*stats.norm.pdf(d1)*((2*(r-q)*T - d2*vol*np.sqrt(T))/(2*T*vol*np.sqrt(T)))
    
    def vomma(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #d^2V/dvol^2
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        return S0*np.exp(-q*T)*stats.norm.pdf(d1)*np.sqrt(T)*((d1*d2)/vol)
    
    def veta(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #d^2V/dvoldT
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        return -S0*np.exp(-q*T)*stats.norm.pdf(d1)*np.sqrt(T)*(q+(((r-q)*d1)/(vol*np.sqrt(T)))-(1+d1*d2)/(2*T))
    
    def speed(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #d^3V/dS^3
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        return -np.exp(-q*T)*((stats.norm.pdf(d1))/(S0**2*vol*np.sqrt(T)))*(d1/(vol*np.sqrt(T))+1)
    
    def zomma(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #d^3V/dS^2dvol
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        return np.exp(-q*T)*((stats.norm.pdf(d1)*(d1*d2-1))/(S0*vol**2*np.sqrt(T)))
    
    def color(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #d^3V/dS^2dT
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        return -np.exp(-q*T)*(stats.norm.pdf(d1)/(2*S0*T*vol*np.sqrt(T)))
    
    def ultima(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #d^3V/dvol^3
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        return (-self.vega(S0, K, vol, r, T, q)/vol**2)*(d1*d2*(1-d1*d2)+d1**2+d2**2)
    
    def dualDelta(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #dV/dK
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        if self.otype == 'call':
            return -np.exp(-r*T)*stats.norm.cdf(d2)
        elif self.otype == 'put':
            return -np.exp(-r*T)*stats.norm.cdf(-d2)
    
    def dualGamma(self, S0=None, K=None, vol=None, r=None, T=None, q=0): #d^2V/dK^2
        S0, K, vol, r, T, q = self.inpcheck(S0, K, vol, r, T, q)
        d1, d2 = self.d1d2(S0, K, vol, r, T, q)
        return np.exp(-r*T)*(stats.norm.pdf(d2)/(K*vol*np.sqrt(T)))
    
    #toSweep dictionary with variables to sweep as key and value as (min, max, steps)
    def sweep(self, toSweep, toGrab):
        inps = {'S0':self.S0, 'K':self.K, 'vol':self.vol, 'r':self.r, 'T':self.T, 'q':self.q}
        vectors = dict([(k, np.linspace(toSweep[k][0], toSweep[k][1], toSweep[k][2])) for k in toSweep])
        scalars = dict([(k, inps[k]) for k in inps if k not in vectors])
        if len(toSweep) == 1:
            out = vectors.values[0]
        if len(toSweep) == 2:
            out = np.meshgrid(list(vectors.values())[0], list(vectors.values())[1])
        if len(toSweep) == 3:
            out = np.meshgrid(list(vectors.values())[0], list(vectors.values())[1], list(vectors.values())[2])
        grids = dict([(k, out[i]) for i, k in enumerate(vectors)])
        combined = {**grids, **scalars}
        
        data = (combined['S0'], combined['K'], combined['vol'], combined['r'], combined['T'], combined['q'])
        out = {}
        
        if 'price' in toGrab: out['price'] = self.price(*data)
        if 'delta' in toGrab: out['delta'] = self.delta(*data)
        if 'vega' in toGrab: out['vega'] = self.vega(*data)
        if 'theta' in toGrab: out['theta'] = self.theta(*data)
        if 'rho' in toGrab: out['rho'] = self.rho(*data)
        if 'omega' in toGrab: out['omega'] = self.omega(*data)
        if 'gamma' in toGrab: out['gamma'] = self.gamma(*data)
        if 'vanna' in toGrab: out['vanna'] = self.vanna(*data)
        if 'charm' in toGrab: out['charm'] = self.charm(*data)
        if 'vomma' in toGrab: out['vomma'] = self.vomma(*data)
        if 'veta' in toGrab: out['veta'] = self.veta(*data)
        if 'speed' in toGrab: out['speed'] = self.speed(*data)
        if 'zomma' in toGrab: out['zomma'] = self.zomma(*data)
        if 'color' in toGrab: out['color'] = self.color(*data)
        if 'ultima' in toGrab: out['ultima'] = self.ultima(*data)
        if 'dualDelta' in toGrab: out['dualDelta'] = self.dualDelta(*data)
        if 'dualGamma' in toGrab: out['dualGamma'] = self.dualGamma(*data)
        
        return {**combined, **out}
