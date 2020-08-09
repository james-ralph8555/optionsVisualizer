from pricing import option
from scipy import io
import numpy as np

def sumprice(outs):
    for i in range(len(outs)):
        outs[i]['price']=np.array(outs[i]['price'])
        if i == 0:
            price=outs[0]['price']
        else:
            price+=outs[i]['price']
    return price

pb = option(otype='put', marketPrice=5.78, S0=334.54, K=325, expDay='2020-09-18', q=0.0171)
ps = option(otype='put', marketPrice=8.98, S0=334.54, K=335, expDay='2020-09-18', q=0.0171)
cs = option(otype='call', marketPrice=7.89, S0=334.54, K=335, expDay='2020-09-18', q=0.0171)
cb = option(otype='call', marketPrice=3.14, S0=334.54, K=345, expDay='2020-09-18', q=0.0171)
toSweep = {'S0' : (315, 355, 100), 'T' : (0.01, 0.11, 100)}
toGrab = ('price')
outs = []
outs.append(pb.sweep(toSweep, toGrab))
outs.append(ps.sweep(toSweep, toGrab))
outs.append(cs.sweep(toSweep, toGrab))
outs.append(cb.sweep(toSweep, toGrab))

price = sumprice(outs)

io.savemat('data1.mat', {'S01': outs[0]['S0'], 'T1': outs[0]['T'], 'price1': price})

toSweep = {'S0' : (315, 355, 100), 'vol' : (0.1, 0.3, 100)}
toGrab = ('price')
outs = []
outs.append(pb.sweep(toSweep, toGrab))
outs.append(ps.sweep(toSweep, toGrab))
outs.append(cs.sweep(toSweep, toGrab))
outs.append(cb.sweep(toSweep, toGrab))

price = sumprice(outs)

io.savemat('data2.mat', {'S02': outs[0]['S0'], 'vol2': outs[2]['vol'], 'price2': price})

toSweep = {'vol' : (0.1, 0.3, 100), 'T' : (0.01, 0.11, 100)}
toGrab = ('price')
outs = []
outs.append(pb.sweep(toSweep, toGrab))
outs.append(ps.sweep(toSweep, toGrab))
outs.append(cs.sweep(toSweep, toGrab))
outs.append(cb.sweep(toSweep, toGrab))

price = sumprice(outs)

io.savemat('data3.mat', {'vol3': outs[2]['vol'], 'T3': outs[0]['T'], 'price3': price})

