"""
This file contains classes that represent pyqtgraph widgets which can be used 
and combined in Qt applications.
"""
import logging

import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore

from data_slicer.cmaps import cmaps, ds_cmap
from data_slicer.cutline import Cutline
from data_slicer.imageplot import ImagePlot, Scalebar
from data_slicer.utilities import make_slice, TracedVariable

logger = logging.getLogger('ds.'+__name__)

#_Parameters____________________________________________________________________

DEFAULT_CMAP = 'Greys'
# Default translation for objects
T = -0.5

#_Classes_______________________________________________________________________

class ColorSliders(QtGui.QWidget) :
    """ A simple widget providing a *gamma* and *vmax* slider. 
    
    **Signals**

    =============  =============================================================
    gamma_changed  emitted when the value of *gamma* changes
    vmax_changed   emitted when the value of *vmax* changes
    =============  =============================================================
    """
    sig_gamma_changed = QtCore.Signal()
    sig_vmax_changed = QtCore.Signal()

    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

        self.gamma = 1
        self.vmax = 1

        # gamma
        gamma_slider = Scalebar()
        self.gamma_values = np.concatenate((np.linspace(0.1, 1, 50), 
                                            np.linspace(1.1, 10, 50)))
        gamma_slider.pos.set_value(0.5)
        gamma_slider.pos.sig_value_changed.connect(self.on_gamma_slider_move)
        # put a label
        gamma_label = pg.TextItem('γ', anchor=(0.5, 0.5))
        gamma_label.setPos(0.5, 0.5)
        gamma_slider.addItem(gamma_label)
        self.gamma_slider = gamma_slider
        
        # vmax (relative colorscale maximum)
        vmax_slider = Scalebar()
        vmax_slider.pos.set_value(self.vmax)
        vmax_slider.pos.sig_value_changed.connect(self.on_vmax_slider_move)
        # put a label
        vmax_label = pg.TextItem('Colorscale', anchor=(0.5, 0.5))
        vmax_label.setPos(0.5, 0.5)
        vmax_slider.addItem(vmax_label)
        self.vmax_slider = vmax_slider

        self.align()

    def align(self) :
        layout = QtGui.QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.gamma_slider, 1, 1)
        layout.addWidget(self.vmax_slider, 2, 1)

    def on_gamma_slider_move(self) :
        """ When the user moves the gamma slider, update gamma. """
        ind = min(int(100*self.gamma_slider.pos.get_value()), 
                  len(self.gamma_values)-1)
        self.gamma = self.gamma_values[ind]
        self.sig_gamma_changed.emit()

    def on_vmax_slider_move(self) :
        """ When the user moves the vmax slider, update vmax. """
        vmax = int(np.round(100*self.vmax_slider.pos.get_value()))/100
        self.vmax = vmax
        self.sig_vmax_changed.emit()

class ThreeDWidget(QtGui.QWidget) :
    """
    A widget that contains a :class:`GLViewWidget 
    <pyqtgraph.opengl.GLViewWidget>` that allows displaying 2D colormeshes in 
    a three dimensional scene.
    This class mostly functions as a base class for more refined variations.
    """

    def __init__(self, *args, data=None, **kwargs) :
        """
        Set up the :class: `GLViewWidget <pyqtgraph.opengl.GLViewWidget>` 
        as this widget's central widget.
        """
        super().__init__(*args, **kwargs)

        # Initialize instance variables
        self.data = TracedVariable(None, name='data')
        self.cmap = cmaps[DEFAULT_CMAP]
        self.lut = cmaps[DEFAULT_CMAP].getLookupTable()
        self.gloptions = 'translucent'

        # Create a GLViewWidget and put it into the layout of this view
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.glview = gl.GLViewWidget()

        # Add the scalebar
        self._initialize_sub_widgets()

        # Put all widgets in place
        self.align()

        # Add some coordinate axes to the view
        self.coordinate_axes = gl.GLAxisItem()
        self.glview.addItem(self.coordinate_axes)
        self.set_coordinate_axes(True)

        # Try to set the default data
        if data is not None :
            self.set_data(data)

    def _initialize_sub_widgets(self) :
        """ Create the slider subwidget. This method exists so it can be 
        overridden by subclasses.
        """
        self.slider_xy = Scalebar(name='xy-slider')
        self.slider_xy.pos.sig_value_changed.connect(self.update_xy)
        self.slider_xy.add_text('xy plane', relpos=(0.5, 0.5))

    def align(self) :
        """ Put all sub-widgets and elements into the layout. """
        l = self.layout

        l.addWidget(self.glview, 0, 0, 5, 5)

        l.addWidget(self.slider_xy, 4, 2, 1, 1)

    def set_coordinate_axes(self, on=True) :
        """ 
        Turn the visibility of the coordinate axes on or off. 

        **Parameters**

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
        Set this widget's data in a :class:`TracedVariable 
        <data_slicer.utilities.TracedVariable>` instance to allow direct 
        updates whenever the data changes.

        **Parameters**

        ====  ==================================================================
        data  np.array of shape (x, y, z); the data cube to be displayed.
        ====  ==================================================================
        """
        self.data.set_value(data)
        self.levels = [data.min(), data.max()]
        self.xscale, self.yscale, self.zscale = [1/s for s in data.shape]
        self._update_sliders()

        self._initialize_planes()

    def _initialize_planes(self) :
        """ This wrapper exists to be overriden by subclasses. """
        self.initialize_xy()

    def _update_sliders(self) :
        """ Update the allowed values for of the plane slider(s). """
        data = self.data.get_value()
        self.slider_xy.pos.set_allowed_values(range(data.shape[2]))

    def get_slice(self, d, i, integrate=0, silent=True) :
        """
        Wrap :func:`make_slice <data_slicer.utilities.make_slice>` to create 
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
        """ Wrapper for :func:`makeRGBA <pyqtgraph.makeRGBA>`."""
        return pg.makeRGBA(cut, levels=self.levels, 
                           lut=self.lut)[0]

    def initialize_xy(self) :
        """ Create the xy plane. """
        # Get out if no data is present
        if self.data.get_value() is None : return
        # Remove any old planes
        if hasattr(self, 'xy') :
            self.glview.removeItem(self.xy)
        # Get the data and texture to create the GLImageItem object
        cut = self.get_xy_slice(0)
        texture = self.make_texture(cut)
        self.xy = gl.GLImageItem(texture, glOptions=self.gloptions)
        # Scale and translate to origin and add to glview
        self.xy.scale(self.xscale, self.yscale, 1)
        self.xy.translate(T, T, T)
        # Put to position in accordance with slider
        self.old_z = self.slider_xy.pos.get_value()
        self.update_xy()
        # Add to GLView
        self.glview.addItem(self.xy)

    def update_xy(self) :
        """ Update both texture and position of the xy plane. """
        if not hasattr(self, 'xy') : return

        # Get the current position
        z = self.slider_xy.pos.get_value()

        # Translate
        self.xy.translate(0, 0, self.zscale*(z-self.old_z))

        # Update the texture (this needs to happen after the translation 
        # because self.get_xy_slice updates the value of self.old_z)
        cut = self.get_xy_slice(z)
        texture = self.make_texture(cut)
        self.xy.setData(texture)

    def set_cmap(self, cmap) :
        """ Change the used colormap to a :class:`ds_cmap 
        <data_slicer.cmaps.ds_cmap>` instance.
        """
        if isinstance(cmap, str) :
            self.cmap = cmaps[cmap]
        elif isinstance(cmap, ds_cmap) :
            self.cmap = cmap
        else :
            raise TypeError('*cmap* has to be a valid colormap name or a '
                            '*ds_cmap* instance')
        # Update the necessary elements
        self.lut = self.cmap.getLookupTable()
        self._on_cmap_change()

    def _on_cmap_change(self) :
        """ Update all elements affected by the cmap change. """
        self.update_xy()

class ThreeDSliceWidget(ThreeDWidget) :
    """
    A :class:`ThreeDWidget <data_slicer.widgets.ThreeDWidget>` that can 
    slice along x, y and z.
    """
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

    def align(self) :
        """ 
        Put all sub-widgets and elements into the layout as follows::

          
               0     1     2  
            +-----+-----+-----+
            |                 | 0
            +                 +  
            |                 | 1
            +     GLView      +
            |                 | 2
            +                 +  
            |                 | 3
            +-----+-----+-----+
            | xy  | yz  | zx  | 4
            +-----+-----+-----+

            5 units in height
            3 units in width
        """
        l = self.layout

#        for slider in [self.slider_xy, self.slider_yz, self.slider_zx] :
#            slider.orientation = 'vertical'
#            slider.orientate()
        
        l.addWidget(self.glview, 0, 0, 5, 3)
        l.addWidget(self.slider_xy, 4, 0, 1, 1)
        l.addWidget(self.slider_yz, 4, 1, 1, 1)
        l.addWidget(self.slider_zx, 4, 2, 1, 1)

    def _initialize_sub_widgets(self) :
        """ Create all three sliders (:class:`Scalebar 
        <data_slicer.imageplot.Scalebar>` instances.
        """
        # xy
        super()._initialize_sub_widgets()
        # yz
        self.slider_yz = Scalebar(name='yz-slider')
        self.slider_yz.pos.sig_value_changed.connect(self.update_yz)
        self.slider_yz.add_text('yz plane', relpos=(0.5, 0.5))
        # zx
        self.slider_zx = Scalebar(name='zx-slider')
        self.slider_zx.pos.sig_value_changed.connect(self.update_zx)
        self.slider_zx.add_text('zx plane', relpos=(0.5, 0.5))

    def _initialize_planes(self) :
        """ Initialize all three planes. """
        self.initialize_xy()
        self.initialize_yz()
        self.initialize_zx()

    def initialize_yz(self) :
        """ Create the yz plane. """
        # Get out if no data is present
        if self.data.get_value() is None : return
        # Remove any old planes
        if hasattr(self, 'yz') :
            self.glview.removeItem(self.yz)
        # Get the data and texture to create the GLImageItem object
        cut = self.get_yz_slice(0)
        texture = self.make_texture(cut)
        self.yz = gl.GLImageItem(texture, glOptions=self.gloptions)
        # Scale and translate to origin and add to glview (this plane has 
        # shape (y, z))
        self.yz.scale(self.yscale, self.zscale, 1)
        self.yz.translate(T, T, 0)
        self.yz.rotate(90, 0, 1, 0)
        self.yz.rotate(90, 1, 0, 0)
        self.yz.translate(T, 0, 0)
        # Put to position in accordance with slider
        self.update_yz()
        # Add to GLView
        self.glview.addItem(self.yz)

    def get_yz_slice(self, i, integrate=0) :
        """ Shorthand to get an yz slice, i.e. *d=0*. """
        self.old_x = i
        return self.get_slice(0, i, integrate)

    def initialize_zx(self) :
        """ Create the zx plane. """
        # Get out if no data is present
        if self.data.get_value() is None : return
        # Remove any old planes
        if hasattr(self, 'zx') :
            self.glview.removeItem(self.zx)
        # Get the data and texture to create the GLImageItem object
        cut = self.get_zx_slice(0)
        texture = self.make_texture(cut)
        self.zx = gl.GLImageItem(texture, glOptions=self.gloptions)
        # Scale and translate to origin and add to glview (this plane has 
        # shape (x, z))
        self.zx.scale(self.xscale, self.zscale, 1)
        self.zx.translate(T, T, 0)
        self.zx.rotate(90, 1, 0, 0)
        self.zx.translate(0, T, 0)
        # Put to position in accordance with slider
        self.update_zx()
        # Add to GLView
        self.glview.addItem(self.zx)

    def get_zx_slice(self, i, integrate=0) :
        """ Shorthand to get an yz slice, i.e. *d=1*. """
        self.old_y = i
        return self.get_slice(1, i, integrate)

    def _update_sliders(self) :
        """ Update the allowed values for of the plane slider(s). """
        data = self.data.get_value()
        self.slider_xy.pos.set_allowed_values(range(data.shape[2]))
        self.slider_yz.pos.set_allowed_values(range(data.shape[0]))
        self.slider_zx.pos.set_allowed_values(range(data.shape[1]))

    def update_yz(self) :
        """ Update both texture and position of the yz plane. """
        if not hasattr(self, 'yz') : return
        # Get the current position
        x = self.slider_yz.pos.get_value()

        # Translate
        self.yz.translate(self.xscale*(x-self.old_x), 0, 0)

        # Update the texture (this needs to happen after the translation 
        # because self.get_yz_slice updates the value of self.old_x)
        cut = self.get_yz_slice(x)
        texture = self.make_texture(cut)
        self.yz.setData(texture)

    def update_zx(self) :
        """ Update both texture and position of the zx plane. """
        if not hasattr(self, 'zx') : return
        # Get the current position
        y = self.slider_zx.pos.get_value()

        # Translate
        self.zx.translate(0, self.yscale*(y-self.old_y), 0)

        # Update the texture (this needs to happen after the translation 
        # because self.get_zx_slice updates the value of self.old_y)
        cut = self.get_zx_slice(y)
        texture = self.make_texture(cut)
        self.zx.setData(texture)

    def _on_cmap_change(self) :
        """ Update all elements affected by the cmap change. """
        self.update_xy()
        self.update_yz()
        self.update_zx()

class FreeSliceWidget(ThreeDWidget) :
    """ A :class:`ThreeDWidget <data_slicer.widgets.ThreeDWidget>` which 
    represents its xy plane in an additional 2D panel.
    In this "selector" panel, there's a :class:`Cutline 
    <data_slicer.cutline.Cutline>` with which arbitrary slices can be 
    generated, which will in turn be shown in the 3D GLView.
    """
    def _initialize_sub_widgets(self) :
        """ Create the ImagePlot with the Cutline. """
        super()._initialize_sub_widgets()
        self.slider_xy.pos.sig_value_changed.connect(self.update_selector)
        self.selector = ImagePlot()

    def align(self) :
        """
        Layout::

              0   1   2   3   4   5   6   7
            +---+---+---+---+---+---+---+---+
            |               |               | 0
            +               |               +
            |               |               | 1
            +  Selector     |   GLView      +
            |               |               | 2
            +               |               +  
            |               |               | 3
            +               |   +---+---+   +
            |               |   |  xy   |   | 4
            +---+---+---+---+---+---+---+---+
        """
        l = self.layout

        l.addWidget(self.selector, 0, 0, 5, 4)
        l.addWidget(self.glview, 0, 4, 5, 4)
        l.addWidget(self.slider_xy, 4, 5, 1, 2)

    def _initialize_planes(self) :
        """ Create the xy plane, the arbitrary cut plane and the view in the 
        selector panel.
        """
        # xy
        super()._initialize_planes()
        # selector
        xy = self.get_xy_slice(0)
        self.selector.set_image(xy, lut=self.lut)
        # cutline in selector
        if not hasattr(self, 'cutline') :
            self.cutline = Cutline(self.selector)
        self.cutline.initialize()
        # cut plane
        if hasattr(self, 'cutplane') :
            self.glview.removeItem(self.cutplane)
        cut, coords = self.get_cutline_cut()
        cut_texture = self.make_texture(cut)
        self.cutplane = gl.GLImageItem(cut_texture, glOptions=self.gloptions)

        # Scale and move to origin in upright position
        self.cutplane.scale(self.xscale, self.zscale, 1)
        self.cutplane.rotate(90, 1, 0, 0)
        self.cutplane.translate(T, 0, T)
        self.transform0 = self.cutplane.transform()

        self.glview.addItem(self.cutplane)
        self.cutline.sig_region_changed.connect(self.update_cut)

    def get_cutline_cut(self) :
        """ Wrapper for :meth:`~data_slicer.cutline.Cutline.get_array_region`.
        """
        data = self.data.get_value()
        cut, coords = self.cutline.get_array_region(data, 
                                           self.selector.image_item, 
                                           returnCoords=True)
        return cut, coords

    def update_cut(self) :
        """ 
        Update the texture and position of the cutline cut in the 
        GLGraphicsView. 
        """
        ## Update the texture
        cut, coords = self.get_cutline_cut()
        texture = self.make_texture(cut)
        self.cutplane.setData(texture)

        ## Update the position in 3D space

        # Get handle positions (in data pixel coordinates (?))
        try :
            x0, y0 = coords[[0, 1], [0, 0]]
            x1, y1 = coords[[0, 1], [-1, -1]]
        except IndexError :
            return

        # Figure out the translation vector
        tx = x0*self.xscale
        ty = y0*self.yscale

        # Calculate the rotation angle
        delta_y = y1 - y0
        try :
            # arctan (delta y) / (delta x)
            alpha = np.arctan(delta_y / (x1 - x0))
        except ZeroDivisionError :
            alpha = np.sign(delta_y) * np.pi/2
        # Correct for special cases
        if x1 < x0 :
            alpha -= np.sign(delta_y) * np.pi
        alpha_degree = 180/np.pi * alpha
        
        # Apply the transformations in inverse order
        t = QtGui.QMatrix4x4()
        t.translate(tx+T, ty+T, T)
        t.scale(self.xscale, self.yscale, 1)
        t.rotate(alpha_degree, 0, 0, 1)
        t.rotate(90, 1, 0, 0)
        t.scale(1, self.zscale, 1)
        self.cutplane.setTransform(t)

    def update_selector(self) :
        """ When the slider position changes, update the image displayed in 
        the selector to represent the correct cut.
        """ 
        z = self.slider_xy.pos.get_value()
        cut = self.get_xy_slice(z)
        self.selector.set_image(cut, lut=self.lut)

    def _on_cmap_change(self) :
        """ Update all elements affected by the cmap change. """
        self.update_xy()
        self.update_cut()
        self.update_selector()

#_Testing_______________________________________________________________________

if __name__ == "__main__" :
    import pickle
    import pkg_resources

    import numpy as np

    import data_slicer.set_up_logging
    # Set up Qt Application skeleton
    app = QtGui.QApplication([])
    window = QtGui.QMainWindow()
    window.resize(800, 800)

    # Add layouting-widget
    cw = QtGui.QWidget()
    window.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    # Add our custom widgets
    w = ThreeDSliceWidget()
    w = FreeSliceWidget()
    layout.addWidget(w, 0, 0, 1, 2)

    button1 = QtGui.QPushButton()
    button1.setText('Reset')
    layout.addWidget(button1, 1, 0, 1, 1)

    button2 = QtGui.QPushButton()
    button2.setText('Randomize')
    layout.addWidget(button2, 1, 1, 1, 1)

    # Necessary for both widgets to be visible
#    layout.setRowStretch(0, 2)
#    layout.setRowStretch(1, 2)

    # Load example data
    data_path = pkg_resources.resource_filename('data_slicer', 'data/')
    datafile = 'testdata_100_150_200.p'
    with open(data_path + datafile, 'rb') as f :
        data = pickle.load(f)
    w.set_data(data)

    # Button actions
    def reset_data() :
        w.set_data(data)
    button1.clicked.connect(reset_data)

    def randomize_data() :
        w.set_data(np.random.rand(42, 123, 234))
    button2.clicked.connect(randomize_data)

    # Run
    window.show()

    

    app.exec_()

