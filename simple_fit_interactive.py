import pyspeckit
import matplotlib
import numpy as np

if not 'savedir' in globals():
    savedir = ''

# load a FITS-compliant spectrum
spec = pyspeckit.Spectrum('10074-190_HCOp.fits')
# The units are originally frequency (check this by printing spec.xarr.units).
# I want to know the velocity.  Convert!
# Note that this only works because the reference frequency is set in the header
# this is no longer necessary!  #spec.xarr.frequency_to_velocity()
# Default conversion is to m/s, but we traditionally work in km/s
spec.xarr.convert_to_unit('km/s')
# plot it up!
spec.plotter()
# Subtract a baseline (the data is only 'mostly' reduced)
spec.baseline(interactive=True)

# specify x points in data units.  We need to transform them to axis units
# because the axis are not consistently generated by mpl
xpoints = [-270,-150,55,218,218]
ypoints = [0]*5
buttons = [1,1,1,1,2]
transform = spec.plotter.axis.transData.transform_point
xy = [transform((xp,yp)) for xp,yp in zip(xpoints,ypoints)]

events = [matplotlib.backend_bases.MouseEvent('button_press_event', spec.plotter.axis.figure.canvas,xp,yp,button=bt)
          for (xp,yp),bt in zip(xy,buttons)]

for ev in events:
    print ev.xdata,ev.ydata
    spec.baseline.event_manager(ev)

spec.baseline.highlight_fitregion()

spec.specfit(interactive=True)

xpoints = [-52,-5,-26,-29,-29]
ypoints = [0, 0, 0.14, 0.07, 0]
buttons = [1,1,2,2,3]
xy = [transform((xp,yp)) for xp,yp in zip(xpoints,ypoints)]

for ev in events:
    print ev.xdata,ev.ydata
    spec.baseline.event_manager(ev)

events = [matplotlib.backend_bases.KeyEvent('button_press_event', spec.plotter.axis.figure.canvas,x=xp,y=yp,key=bt)
          for (xp,yp),bt in zip(xy,buttons)]

for ev in events:
    print ev.xdata,ev.ydata
    spec.specfit.event_manager(ev)


print "Includemask before excludefit: ",spec.xarr[spec.baseline.includemask]," length = ",spec.baseline.includemask.sum()
spec.baseline(excludefit=True)
spec.baseline.highlight_fitregion()
print "Includemask after excludefit: ",spec.xarr[spec.baseline.includemask]," length = ",spec.baseline.includemask.sum()
spec.specfit(guesses=spec.specfit.modelpars)

spec.plotter.figure.savefig(savedir+"simple_fit_interactive_HCOp.png")

print "Doing the interactive thing now"
event1 = matplotlib.backend_bases.KeyEvent('key_press_event', spec.plotter.axis.figure.canvas,key='o')
# event 1 is clicking the zoom button
x,y = transform((-100,-0.07))
event2 = matplotlib.backend_bases.MouseEvent('button_press_event', spec.plotter.axis.figure.canvas,button=1,x=x,y=y)
event2.inaxes = spec.plotter.axis

event3 = matplotlib.backend_bases.MouseEvent('motion_notify_event', spec.plotter.axis.figure.canvas,button=1,x=x,y=y)
event3.inaxes = spec.plotter.axis

x,y = transform((20,0.16))
event4 = matplotlib.backend_bases.MouseEvent('button_release_event', spec.plotter.axis.figure.canvas,button=1,x=x,y=y)
event4.inaxes = spec.plotter.axis

if hasattr(spec.plotter.figure.canvas,'toolbar'):
    spec.plotter.figure.canvas.toolbar.press_zoom(event2)
    spec.plotter.figure.canvas.toolbar._xypress=[(event2.x,event2.y,spec.plotter.axis,0,spec.plotter.axis.viewLim.frozen(),spec.plotter.axis.transData.frozen())]
    spec.plotter.figure.canvas.toolbar.drag_zoom(event3)
    spec.plotter.figure.canvas.toolbar.release_zoom(event4)

    # make sure zoom worked
    np.testing.assert_array_almost_equal(spec.plotter.axis.get_xlim(), [-100, 20])
    np.testing.assert_array_almost_equal(spec.plotter.axis.get_ylim(), [-0.07, 0.16])
else:
    spec.plotter.axis.set_xlim(-100, 20)
    spec.plotter.axis.set_ylim(-0.07, 0.16)

#spec.plotter.debug=True
print "Includemask before excludefit with window limits: ",spec.xarr[spec.baseline.includemask]," length = ",spec.baseline.includemask.sum()
spec.baseline(excludefit=True,use_window_limits=True,highlight=True)
spec.baseline.highlight_fitregion()
print "Includemask after excludefit with window limits: ",spec.xarr[spec.baseline.includemask]," length = ",spec.baseline.includemask.sum()
# total 512 pixels, 5 should be excluded inside, 107 should be available
assert spec.baseline.includemask.sum() == 103
spec.specfit(use_window_limits=True)

# Regression test: make sure baseline selection works
# this should *NOT* be 107!  107 is ALL data between -100 and +20
# this should be 103, which tells you that the fit has been excluded!
# (note added 2/12/2014)
print spec.baseline.includemask.sum()
assert spec.baseline.includemask.sum() == 103
assert spec.baseline.includemask[spec.xarr.x_to_pix(-27.16)] == False

event1 = matplotlib.backend_bases.KeyEvent('key_press_event', spec.plotter.axis.figure.canvas,key='B')
spec.plotter.parse_keys(event1)
print "spec.baseline.includemask.sum()",spec.baseline.includemask.sum()
assert spec.baseline.includemask.sum() == 0
x,y = transform((-153.3,-0.007))
event2 = matplotlib.backend_bases.MouseEvent('button_press_event', spec.plotter.axis.figure.canvas,button=1,x=x,y=y)
event2.inaxes,event2.button,event2.xdata,event2.ydata = spec.plotter.axis,1,-153.3,-0.007
spec.baseline.event_manager(event2,debug=True)
event2.inaxes,event2.button,event2.xdata,event2.ydata = spec.plotter.axis,1,-41.5,-0.01
spec.baseline.event_manager(event2,debug=True)
assert spec.baseline.includemask.sum() == 99

event2.inaxes,event2.button,event2.xdata,event2.ydata = spec.plotter.axis,1,59,-0.1
spec.baseline.event_manager(event2,debug=True)
event2.inaxes,event2.button,event2.xdata,event2.ydata = spec.plotter.axis,1,244,0.1
spec.baseline.event_manager(event2,debug=True)
assert spec.baseline.includemask.sum() == 264

event2.inaxes,event2.button,event2.xdata,event2.ydata = spec.plotter.axis,3,244,0.1
spec.baseline.event_manager(event2,debug=True)
np.testing.assert_array_almost_equal(spec.baseline.baselinepars, np.array([-0.00016474, -0.01488391]))


spec.baseline.selectregion(reset=True)
assert np.all(spec.baseline.includemask)
spec.baseline(interactive=True)
assert np.all(spec.baseline.includemask)
# reset_selection intentionally has a different behavior than reset
# for interactive, you want POSITIVE selection, not negative
spec.baseline(interactive=True, reset_selection=True)
assert np.all(True-spec.baseline.includemask)
