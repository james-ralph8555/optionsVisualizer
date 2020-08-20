from pandas_datareader.data import Options
from dateutil.parser import parse
from datetime import datetime
from numpy import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.colors import LogNorm
#from implied_vol import BlackScholes
from functools import partial
from scipy import optimize
from scipy import stats
from scipy import interpolate
import numpy as np
from scipy.interpolate import griddata
import yfinance as yf
import pandas as pd
import pandas_market_calendars as mcal
from matplotlib.colors import LinearSegmentedColormap
from parula import parula


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


def nan_helper(y):
    return np.isnan(y), lambda z: z.nonzero()[0]

def oprice(otype, S0=None, K=None, vol=None, r=None, T=None, q=0):
        d1 = (np.log(S0/K)+(r - q + vol**2/2)*T)/(vol*np.sqrt(T))
        d2 = d1-vol*np.sqrt(T)
        if otype == 'Call':
            return S0*np.exp(-q*T)*stats.norm.cdf(d1)-K*np.exp(-r*T)*stats.norm.cdf(d2)
        elif otype == 'Put':
            return K*np.exp(-r*T)*stats.norm.cdf(-d2) - S0*np.exp(-q*T)*stats.norm.cdf(-d1)

def plot3D(X,Y,Z):
   fig = plt.figure()
   ax = Axes3D(fig, azim = -29, elev = 50)

   ax.plot(X,Y,Z,'o')

   plt.xlabel("expiry")
   plt.ylabel("strike")
   plt.show()

def toT(bid, ask, expiry):
    daysInYear = 255
    nyse = mcal.get_calendar('NYSE')
    price = (bid+ask)/2.0
    expiry = expiry.to_numpy()
    expDay = expiry.astype('datetime64', copy=False)
    T = (np.busday_count(np.datetime64('today'), expDay, holidays=nyse.holidays().holidays)+2)/daysInYear
    return T

def get_surf(ticker, otype):
   tick = yf.Ticker(ticker)
   underlying = (tick.info['bid'] + tick.info['ask'])/2
   dates = list(tick.options)
   nyse = mcal.get_calendar('NYSE')
   for i in dates:
       if np.busday_count(np.datetime64('today'), np.datetime64(i), holidays=nyse.holidays().holidays) < 2:
           dates.remove(i)

   ran = 0
   for d in dates:
       if ran == 0:
           if otype == 'Put':
               q = tick.option_chain(d).puts
           elif otype == 'Call':
               q = tick.option_chain(d).calls
           q.insert(14, 'expiry', [d for i in range(len(q.index))])
           q = q[q['volume'] >= 10]
           ran = 1
       else:
           if otype == 'Put':
               temp = tick.option_chain(d).puts
           elif otype == 'Call':
               temp = tick.option_chain(d).calls
           temp.insert(14, 'expiry', [d for i in range(len(temp.index))])
           temp = temp[temp['volume'] >= 10]
           q = q.append(temp)
   q['expiry'] = toT(q['bid'], q['ask'], q['expiry'])
   q = q[['expiry', 'strike', 'impliedVolatility']]
   q = q[q['expiry'] < 0.25]
   q = q[(q['strike'].astype('float') > underlying * 0.5) & (q['strike'].astype('float') < underlying * 1.5)]
   vals = q.to_numpy().T
   vals = vals.astype(np.float64)
   fig = plt.figure()
   ax = Axes3D(fig, azim = 170, elev = 40)
   mesh_plot2(vals[0],vals[1],vals[2], len(set(q['expiry'])),fig, ax, ticker + ' ' + otype + ' Volatility Surface')

def make_surf(X,Y,Z,nDates):
   XX,YY = meshgrid(linspace(min(X),max(X),nDates),linspace(min(Y),max(Y),int(max(Y)-min(Y))))
   ZZ = griddata(array([X,Y]).T,array(Z),(XX,YY), method='linear')
   nans, x = nan_helper(ZZ)
   ZZ[nans] = np.interp(x(nans), x(~nans), ZZ[~nans])
   return XX,YY,ZZ

def mesh_plot2(X,Y,Z,nDates,fig,ax, title):
   parula_map = LinearSegmentedColormap.from_list('parula', parula())
   XX,YY,ZZ = make_surf(X,Y,Z,nDates)
   ax.plot_surface(XX,YY,ZZ, cmap=parula_map)
   ax.set_xlabel("Years to Expiry")
   ax.set_ylabel("Strike")
   ax.set_zlabel("Implied Volatility")
   ax.set_title(title)


get_surf('SPY', 'Put')