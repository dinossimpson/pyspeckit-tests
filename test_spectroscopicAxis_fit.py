import numpy as np
from pyspeckit.spectrum.models.inherited_gaussfitter import gaussian_fitter
from pyspeckit import Spectrum
import matplotlib.pyplot as plt

xarr = np.linspace(-100,100,200)
gf = gaussian_fitter()
params = [1.0, 2.0, 20.]
passes = {'passes': [0,0,0], 'avg_difference': [0,0,0]}
fails = {'fails': [0,0,0], 'avg_difference': [0, 0, 0]}

for i in range(100):
	passed = True
	parameter_error_amplitude = [1/5, 1., 5.]
	parameter_noise = [params[0] + abs(np.random.randn()) * parameter_error_amplitude[0], 
                       params[1] + abs(np.random.randn()) * parameter_error_amplitude[1],
                       params[2] + abs(np.random.randn()) * parameter_error_amplitude[2]]
	guesses = np.array(params)+parameter_noise
	sp = Spectrum(xarr=xarr, data=gf.n_modelfunc(pars=params)(xarr)+np.random.randn(xarr.size)/100., error=np.ones(xarr.size)/100)
	# sp = Spectrum(xarr=xarr, data=gf.n_modelfunc(pars=params)(xarr))
	sp.plotter(axis=plt.gca())
	sp.specfit(guesses=guesses)
	print 'guesses:',guesses
	assertion = ((np.array(sp.specfit.fitter.mpp)-np.array(params))/parameter_noise)**2
	print '(mpp - params / param_noise )^2 = ', assertion
	
	for j,result in enumerate(assertion):
		if result >= 2: 
			passed = False
			continue
	if passed:
		for j in range(3):
			passes['passes'][j]+=1
			passes['avg_difference'][j] += abs(assertion[j] - params[j])
	else:
		for j in range(3):
			fails['fails'][j]+=1
			fails['avg_difference'][j] += abs(assertion[j] - params[j])
	# plt.show()

for i,j in enumerate(passes['avg_difference']):
	if passes['passes'][i]:
		passes['avg_difference'][i] = j/passes['passes'][i]
for i,j in enumerate(fails['avg_difference']):
	if fails['fails'][i]:
		fails['avg_difference'][i] = j/fails['fails'][i]

print 'passes:', passes
print 'fails:', fails