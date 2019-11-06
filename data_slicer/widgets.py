"""
This file contains classes that represent pyqtgraph widgets which can be used 
and combined in Qt applications.
"""
import logging

import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtGui

from data_slicer.imageplot import Scalebar
from data_slicer.cmaps import cmaps
from data_slicer.utilities import make_slice, TracedVariable

logger = logging.getLogger('ds.'+__name__)

#_Parameters____________________________________________________________________

DEFAULT_CMAP = 'Greys'
# Default translation for objects
T = -0.5

#_Classes_______________________________________________________________________

class ThreeDWidget(QtGui.QWidget) :
    """
    A widget that contains a :class: `GLViewWidget 
    <pyqtgraph.opengl.GLViewWidget>` that allows displaying 2D colormeshes in 
    a three dimensional scene.
    This class mostly functions as a base class for more refined variations.
    """

    data = TracedVariable(None)
    lut = cmaps[DEFAULT_CMAP].getLookupTable()
    gloptions = 'translucent'

    def __init__(self, *args, data=None, **kwargs) :
        """
        Set up the :class: `GLViewWidget <pyqtgraph.opengl.GLViewWidget>` 
        as this widget's central widget.
        """
        super().__init__(*args, **kwargs)

        # Create a GLViewWidget and put it into the layout of this view
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.glview = gl.GLViewWidget()

        # Add the scalebar
        self.slider_xy = Scalebar()
        self.slider_xy.pos.sig_value_changed.connect(self.update_xy)

        # Put all widgets in place
        self.align()

        # Add some coordinate axes to the view
        self.coordinate_axes = gl.GLAxisItem()
        self.glview.addItem(self.coordinate_axes)
        self.set_coordinate_axes(True)

        # Try to set the default data
        if data is not None :
            self.set_data(data)

        # Connect signal of data update
#        self.data.sig_value_changed.connect(self.update_xy)

    def align(self) :
        """ Put all sub-widgets and elements into the layout. """
        l = self.layout

        l.addWidget(self.glview, 0, 0, 5, 5)

        l.addWidget(self.slider_xy, 4, 2, 1, 1)

    def set_coordinate_axes(self, on=True) :
        """ 
        Turn the visibility of the coordinate axes on or off. 

        *Parameters*
        ==  ====================================================================
        on  bool or one of ('on', 1); if not `True` or any of the values stated,
            turn the axes off. Otherwise turn them on.
        ==  ====================================================================
        """
        if on in [True, 'on', 1] :
            logger.debug('Turning coordinate axes ON')
            self.coordinate_axes.show()
        else :
            logger.debug('Turning coordinate axes OFF')
            self.coordinate_axes.hide()

    def set_data(self, data) :
        """
        Set this widget's data in a :class: `TracedVariable 
        <data_slicer.utilities.TracedVariable>` instance to allow direct 
        updates whenever the data changes.

        *Parameters*
        ====  ==================================================================
        data  np.array of shape (x, y, z); the data cube to be displayed.
        ====  ==================================================================
        """
        self.data.set_value(data)
        self.levels = [data.min(), data.max()]
        self.xscale, self.yscale, self.zscale = [1/s for s in data.shape]
        # Set the allowed values for the slider
        self.slider_xy.pos.set_allowed_values(range(data.shape[2]))

        self.initialize_xy()

    def get_slice(self, d, i, integrate=0, silent=True) :
        """
        Wrap :func: `make_slice <data_slicer.utilities.make_slice>` to create 
        slices out of this widget's `self.data`.
        Confer respective documentation for details.
        """
        return make_slice(self.data.get_value(), d, i, integrate=integrate, 
                          silent=silent)

    def get_xy_slice(self, i, integrate=0) :
        """ Shorthand to get an xy slice, i.e. *d=2*. """
        self.old_z = i
        return self.get_slice(2, i, integrate)

    def make_texture(self, cut) :
        """ Wrapper for :func: `makeRGBA <pyqtgraph.makeRGBA>`. """
        return pg.makeRGBA(cut, levels=self.levels, lut=self.lut)[0]

    def initialize_xy(self) :
        """ Create the xy plane. """
        # Get out if no data is present
        if self.data.get_value() is None : return
        # Get the data and texture to create the GLImageItem object
        cut = self.get_xy_slice(0)
        texture = self.make_texture(cut)
        self.xy = gl.GLImageItem(texture, glOptions=self.gloptions)
        # Scale and translate to origin and add to glview
        self.xy.scale(self.xscale, self.yscale, 1)
        self.xy.translate(T, T, T)
        self.glview.addItem(self.xy)

    def update_xy(self) :
        """ Update both texture and position of the xy plane. """
        # Get the current position
        z = self.slider_xy.pos.get_value()

        # Translate
        self.xy.translate(0, 0, self.zscale*(z-self.old_z))

        # Update the texture (this needs to happen after the translation 
        # because self.get_xy_slice updates the value of self.old_z)
        cut = self.get_xy_slice(z)
        texture = self.make_texture(cut)
        self.xy.setData(texture)

#_Testing_______________________________________________________________________

if __name__ == "__main__" :
    import pickle
    import pkg_resources

    import set_up_logging
    # Set up Qt Application skeleton
    app = QtGui.QApplication([])
    window = QtGui.QMainWindow()
    window.resize(800, 800)

    # Add our custom widgets
    w = ThreeDWidget()
    window.setCentralWidget(w)

    # Run
    window.show()

    data_path = pkg_resources.resource_filename('data_slicer', '../data/')
    datafile = 'testdata_100_150_200.p'
    with open(data_path + datafile, 'rb') as f :
        data = pickle.load(f)
    w.set_data(data)

    app.exec_()

