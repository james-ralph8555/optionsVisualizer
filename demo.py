from pricing import option
from scipy import io
import numpy as np

pb = option(otype='put', marketPrice=5.78, S0=334.54, K=325, expDay='2020-09-18')
ps = option(otype='put', marketPrice=8.98, S0=334.54, K=335, expDay='2020-09-18')
cs = option(otype='call', marketPrice=7.89, S0=334.54, K=335, expDay='2020-09-18')
cb = option(otype='call', marketPrice=3.14, S0=334.54, K=345, expDay='2020-09-18')
toSweep = {'S0' : (315, 355, 100), 'T' : (0.01, 0.11, 100)}
outs = []
outs.append(pb.sweep(toSweep))
outs.append(ps.sweep(toSweep))
outs.append(cs.sweep(toSweep))
outs.append(cb.sweep(toSweep))

data = np.array(outs)

io.savemat('data1.mat', {'S01': data[0,0], 'K1': data[:,1], 'vol1': data[:,2], 'r1': data[0,3], 'T1': data[0,4], 'price1': data[:,5]})

toSweep = {'S0' : (315, 355, 100), 'vol' : (0.1, 0.3, 100)}
outs = []
outs.append(pb.sweep(toSweep))
outs.append(ps.sweep(toSweep))
outs.append(cs.sweep(toSweep))
outs.append(cb.sweep(toSweep))

data = np.array(outs)

io.savemat('data2.mat', {'S02': data[0,0], 'K2': data[:,1], 'vol2': data[2,2], 'r2': data[0,3], 'T2': data[0,4], 'price2': data[:,5]})

toSweep = {'vol' : (0.1, 0.3, 100), 'T' : (0.01, 0.11, 100)}
outs = []
outs.append(pb.sweep(toSweep))
outs.append(ps.sweep(toSweep))
outs.append(cs.sweep(toSweep))
outs.append(cb.sweep(toSweep))

data = np.array(outs)

io.savemat('data3.mat', {'S03': data[0,0], 'K3': data[:,1], 'vol3': data[2,2], 'r3': data[0,3], 'T3': data[0,4], 'price3': data[:,5]})