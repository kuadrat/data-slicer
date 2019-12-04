"""
A widget that combines slices from different sides with intensity 
distribution curves and other convenient features.
"""

import logging
import pickle
import pkg_resources
from copy import copy

import numpy as np
#import pyqtgraph as pg
import pyqtgraph.console
from pyqtgraph.Qt import QtGui, QtCore
from qtconsole.rich_ipython_widget import RichIPythonWidget, RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager

from data_slicer.cmaps import cmaps
from data_slicer.cutline import Cutline
from data_slicer.imageplot import *
from data_slicer.utilities import TracedVariable

logger = logging.getLogger('ds.'+__name__)

# +------------------------+ #
# | Appearance definitions | # =================================================
# +------------------------+ #

app_style="""
QMainWindow{
    background-color: black;
    }
"""

console_style = """
color: rgb(255, 255, 255);
background-color: rgb(0, 0, 0);
border: 1px solid rgb(50, 50, 50);
"""

DEFAULT_CMAP = 'viridis'

class EmbedIPython(RichJupyterWidget):
    """ Some voodoo to get an ipython console in a Qt application. """
    def __init__(self, **kwarg):
        super(RichJupyterWidget, self).__init__()
        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel
        self.kernel.gui = 'qt4'
        self.kernel.shell.push(kwarg)
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()

# Prepare sample data
data_path = pkg_resources.resource_filename('data_slicer', 'data/')
SAMPLE_DATA_FILE = data_path + 'testdata_100_150_200.p'

# +-----------------------+ #
# | Main class definition | # ==================================================
# +-----------------------+ #

class PITDataHandler() :
    """ Object that keeps track of a set of 3D data and allows 
    manipulations on it. In a Model-View-Controller framework this could be 
    seen as the Model, while :class: `MainWindow 
    <data_slicer.pit.MainWindow>` would be the View part.
    """
    # np.array that contains the 3D data
    data = None
    axes = np.array([[0, 1], [0, 1], [0, 1]])
    # Indices of *data* that are displayed in the main plot 
    displayed_axes = (0,1)
    # Index along the z axis at which to produce a slice
    z = TracedVariable(0, name='z')
    # Number of slices to integrate along z
#    integrate_z = TracedVariable(value=0, name='integrate_z')

    def __init__(self, main_window) :
        self.main_window = main_window

    def get_data(self) :
        """ Convenience `getter` method. Allows writing `self.get_data()` 
        instead of ``self.data.get_value()``. 
        """
        return self.data.get_value()

    def set_data(self, data) :
        """ Convenience `setter` method. Allows writing `self.set_data(d)` 
        instead of ``self.data.set_value(d)``. 
        """
        self.data.set_value(data)

    def prepare_data(self, data, axes=3*[None]) :
        """ Load the specified data and prepare the corresponding z range. 
        Then display the newly loaded data.

        *Parameters*
        ====  ==================================================================
        data  3d array; the data to display
        axes  len(3) list or array of 1d-arrays or None; the units along the 
              x, y and z axes respectively. If any of those is *None*, pixels 
              are used.
        ====  ==================================================================
        """
        logger.debug('prepare_data()')

        self.data = TracedVariable(data, name='data')
        self.axes = np.array(axes)

        # Retain a copy of the original data and axes so that we can reset later
        # NOTE: this effectively doubles the used memory!
        self.original_data = copy(self.data.get_value())
        self.original_axes = copy(self.axes)

        self.prepare_axes()
        self.on_z_dim_change()
        
        # Connect signal handling so changes in data are immediately reflected
        self.z.sig_value_changed.connect(self.main_window.update_main_plot)
        self.data.sig_value_changed.connect(self.on_data_change)

        self.main_window.update_main_plot()
        self.main_window.set_axes()

    def load(self, data, axes=3*[None]) :
        """ Convenient alias for :func: `prepare_data 
        <data_slicer.pit.PITDataHandler.prepare_data>`. """
        self.prepare_data(data, axes)

    def open(self, data, axes=3*[None]) :
        """ Convenient alias for :func: `prepare_data 
        <data_slicer.pit.PITDataHandler.prepare_data>`. """
        self.prepare_data(data, axes)

    def update_z_range(self) :
        """ When new data is loaded or the axes are rolled, the limits and 
        allowed values along the z dimension change.
        """
        # Determine the new ranges for z
        self.zmin = 0
        self.zmax = self.get_data().shape[2] - 1

        self.z.set_allowed_values(range(self.zmin, self.zmax+1))
        self.z.set_value(self.zmin)

    def reset_data(self) :
        """ Put all data and metadata into its original state, as if it was 
        just loaded from file.
        """
        logger.debug('reset_data()')
        self.data.set_value(copy(self.original_data))
        self.set_data(self.data)
        self.axes = copy(self.original_axes)
        self.prepare_axes()
        self.main_window.set_axes()
        # Redraw the integrated intensity plot
        self.on_z_dim_change()

    def prepare_axes(self) :
        """ Create a list containing the three original x-, y- and z-axes 
        and replace *None* with the amount of pixels along the given axis.
        """
        shapes = self.data.get_value().shape
        # Avoid undefined axes scales and replace them with len(1) sequences
        for i,axis in enumerate(self.axes) :
            if axis is None :
                self.axes[i] = np.arange(shapes[i])

    def on_data_change(self) :
        """ Update self.main_window.image_data and replot. """
        logger.debug('on_data_change()')
        self.update_image_data()
        self.main_window.redraw_plots()
        # Also need to recalculate the intensity plot
        self.on_z_dim_change()

#    def on_z_change(self, caller=None) :
#        """ Callback to the :signal: `sig_z_changed`. Ensure self.z does not go 
#        out of bounds and update the Image slice with a call to :func: 
#        `update_main_plot <data_slicer.imageplot.ImagePlot.update_main_plot>`.
#        """
        # Update: AFAIK TracedVariable takes care of not going out of bounds 
        # itself.
#        # Ensure z doesn't go out of bounds
#        z = self.z.get_value()
#        clipped_z = clip(z, self.zmin, self.zmax)
#        if z != clipped_z :
#            # NOTE this leads to unnecessary signal emitting. Should avoid 
#            # emitting the signal from inside a slot (slot: function 
#            # connected to that signal)
#            self.z.set_value(clipped_z)
#        self.main_window.update_main_plot()

    def on_z_dim_change(self) :
        """ Called when either completely new data is loaded or the dimension 
        from which we look at the data changed (e.g. through :func: `roll_axes 
        <data_slicer.pit.PITDataHandler.roll_axes>`).
        Update the z range and the integrated intensity plot.
        """
        logger.debug('on_z_dim_change()')
        self.update_z_range()

        # Get a shorthand for the integrated intensity plot
        ip = self.main_window.integrated_plot
        # Remove the old integrated intensity curve
        try :
            old = ip.listDataItems()[0]
            ip.removeItem(old)
        except IndexError :
            pass

        # Calculate the integrated intensity and plot it
        self.calculate_integrated_intensity()
        ip.plot(self.integrated)

        # Also display the actual data values in the top axis
        zscale = self.axes[2]
        zmin = zscale[0]
        zmax = zscale[-1]
        ip.set_secondary_axis(zmin, zmax)

    def calculate_integrated_intensity(self) :
        self.integrated = self.get_data().sum(0).sum(0)

    def update_image_data(self) :
        """ Get the right (possibly integrated) slice out of *self.data*, 
        apply postprocessings and store it in *self.image_data*. 
        Skip this if the z value should be out of range, which can happen if 
        the image data changes and the z scale hasn't been updated yet.
        """
        logger.debug('update_image_data()')
        z = self.z.get_value()
        integrate_z = \
        int(self.main_window.integrated_plot.slider_width.get_value()/2)
        data = self.get_data()
        try :
            self.main_window.image_data = self.make_slice(data, 2, z, 
                                                          integrate_z)
        except IndexError :
            logger.debug(('update_image_data(): z index {} out of range for '
                          'data of length {}.').format(
                             z, self.image_data.shape[0]))

    def make_slice(self, data, dimension, index, integrate) :
        """ Create a slice out of the 3d data (l x m x n) along dimension d 
        (0,1,2) at index i. Optionally integrate around i.

        *Parameters*
        =======================================================================
        data       array-like; data of the shape (l x m x n)
        dimension  int, d in (0, 1, 2); dimension along which to slice
        index      int, 0 <= i < data.size[d]; The index at which to create 
                   the slice
        integrate  int, 0 <= integrate < |i - n|; the number of slices above 
                   and below slice i over which to integrate
        =======================================================================

        *Returns*
        =======================================================================
        res        np.array; Slice at index with dimensions shape[:d] + shape[d+1:]
                   where shape = (l, m, n).
        =======================================================================
        """
        # Get the relevant dimensions
        shape = data.shape
        try :
            n_slices = shape[dimension]
        except IndexError :
            print(('dimension ({}) can only be 0, 1 or 2 and data must be '
                   '3D.').format(dimension))
            return

        # Set the integration indices and adjust them if they go out of scope
        start = index - integrate
        stop = index + integrate + 1
        if start < 0 :
            start = 0
        if stop > n_slices :
            stop = n_slices

        # Initialize data container and fill it with data from selected slices
        if dimension == 0 :
            sliced = data[start:stop,:,:].sum(dimension)
        elif dimension == 1 :
            sliced = data[:,start:stop,:].sum(dimension)
        elif dimension == 2 :
            sliced = data[:,:,start:stop].sum(dimension)

        return sliced

    def roll_axes(self, i=1) :
        """ Change the way we look at the data cube. While initially we see 
        an Y vs. X slice in the main plot, roll it to Z vs. Y. A second call 
        would roll it to X vs. Z and, finally, a third call brings us back to 
        the original situation.

        *Parameters*
        =  =====================================================================
        i  int; Number of dimensions to roll.
        =  =====================================================================
        """
        logger.debug('roll_axes()')
        data = self.get_data()
        res = np.roll([0, 1, 2], i)
        self.set_data(np.moveaxis(data, [0,1,2], res))
        # Setting the data triggers a call to self.redraw_plots()
        self.axes = np.roll(self.scales, i)
        self.on_z_dim_change()
        self.main_window.set_axes()

class MainWindow(QtGui.QMainWindow) :
    """ The main window of PIT. Defines the basic GUI layouts and 
    acts as the controller, keeping track of the data and handling the 
    communication between the different GUI elements. 
    """

    title = 'Python Image Tool'
    # width, height in pixels
    size = (1200, 800)

    # Plot transparency alpha
    alpha = 1
    # Plot powerlaw normalization exponent gamma
    gamma = 1
    # Relative colormap maximum
    vmax = 1

    # Need to store original transformation information for `rotate()`
    transform_factors = []

    def __init__(self, data=None, background='default') :
        super().__init__()
        self.data_handler = PITDataHandler(self)

         # Aesthetics
        self.setStyleSheet(app_style)
        self.set_cmap(DEFAULT_CMAP)

        self.init_UI()
        
        # Connect signal handling
        self.cutline.sig_initialized.connect(self.on_cutline_initialized)

        # Prepare sample data for initialization
        if data is None :
            with open(SAMPLE_DATA_FILE, 'rb') as f :
                data = pickle.load(f)
        self.data_handler.prepare_data(data)

    def init_UI(self) :
        """ Initialize the elements of the user interface. """
        # Set the window title
        self.setWindowTitle(self.title)
        self.resize(*self.size)

        # Create a "central widget" and its layout
        self.central_widget = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # Create the 3D (main) and cut ImagePlots 
        self.main_plot = ImagePlot(name='main_plot')
        self.cut_plot = CrosshairImagePlot(name='cut_plot')

        # Create the intensity distribution plots
        self.x_plot = CursorPlot(name='x_plot', orientation='horizontal')
        self.y_plot = CursorPlot(name='y_plot')
        self.x_plot.register_traced_variable(self.cut_plot.pos[0])
        self.y_plot.register_traced_variable(self.cut_plot.pos[1])
#        for traced_variable in self.cut_plot.pos :
#            traced_variable.sig_value_changed.connect(
#                self.update_xy_plots)
        self.cut_plot.pos[0].sig_value_changed.connect(self.update_y_plot)
        self.cut_plot.pos[1].sig_value_changed.connect(self.update_x_plot)

        self.cut_plot.sig_image_changed.connect(self.update_xy_plots)

        # Set up the python console
        namespace = dict(pit=self.data_handler, mw=self)
        self.console = pyqtgraph.console.ConsoleWidget(namespace=namespace)
        self.console = EmbedIPython(**namespace)
        self.console.kernel.shell.run_cell('%pylab qt')
        self.console.setStyleSheet(console_style)

        # Create the integrated intensity plot
        ip = CursorPlot(name='z selector')
        ip.register_traced_variable(self.data_handler.z)
        ip.change_width_enabled = True
        ip.slider_width.sig_value_changed.connect(self.update_main_plot)
        self.integrated_plot = ip

        # Add ROI to the main ImageView
        self.cutline = Cutline(self.main_plot)
        self.cutline.initialize()

        # Scalebars. scalebar1 is for the `gamma` value
        scalebar1 = Scalebar()
        self.gamma_values = np.concatenate((np.linspace(0.1, 1, 50), 
                                            np.linspace(1.1, 10, 50)))
        scalebar1.pos.set_value(0.5)
        scalebar1.pos.sig_value_changed.connect(self.on_gamma_slider_move)
        # Label the scalebar
        gamma_label = pg.TextItem('γ', anchor=(0.5, 0.5))
        gamma_label.setPos(0.5, 0.5)
        scalebar1.addItem(gamma_label)
        self.scalebar1 = scalebar1
        
        # scalebar2 is for  vmax (relative colorscale maximum)
        scalebar2 = Scalebar()
        scalebar2.pos.set_value(self.vmax)
        scalebar2.pos.sig_value_changed.connect(self.on_vmax_slider_move)
        # Label the scalebar
        vmax_label = pg.TextItem('Colorscale', anchor=(0.5, 0.5))
        vmax_label.setPos(0.5, 0.5)
        scalebar2.addItem(vmax_label)
        self.scalebar2 = scalebar2

        # Align all the gui elements
        self.align()
        self.show()

    def align(self) :
        """ Align all the GUI elements in the QLayout. 
        
          0   1   2   3   4
        +---+---+---+---+---+
        |       |       | e | 0
        + main  |  cut  | d +
        |       |       | c | 1
        +-------+-------+---+
        |       |  mdc  |   | 2
        +   z   +-------+---+
        |       |  console  | 3
        +---+---+---+---+---+
        
        (Units of subdivision [sd])
        """
        # subdivision 
        sd = 3
        # Get a short handle
        l = self.layout
        # addWIdget(row, column, rowSpan, columnSpan)
        # Main (3D) ImageView in top left
        l.addWidget(self.main_plot, 0, 0, 2*sd, 2*sd)
        # Cut to the right of Main
        l.addWidget(self.cut_plot, 0, 2*sd, 2*sd, 2*sd)
        # EDC and MDC plots
        l.addWidget(self.x_plot, 0, 4*sd, 2*sd, 2)
        l.addWidget(self.y_plot, 2*sd, 2*sd, 1*sd, 2*sd)
        # Integrated z-intensity plot
        l.addWidget(self.integrated_plot, 2*sd, 0, 2*sd, 2*sd)
        # Console
        l.addWidget(self.console, 3*sd, 2*sd, 1*sd, 3*sd)

        # Scalebars
        l.addWidget(self.scalebar1, 2*sd, 4*sd, 1, 1*sd)
        l.addWidget(self.scalebar2, 2*sd+1, 4*sd, 1, 1*sd)

        nrows = 4*sd
        ncols = 5*sd
        # Need to manually set all row- and columnspans as well as min-sizes
        for i in range(nrows) :
            l.setRowMinimumHeight(i, 50)
            l.setRowStretch(i, 1)
        for i in range(ncols) :
            l.setColumnMinimumWidth(i, 50)
            l.setColumnStretch(i, 1)

    def update_main_plot(self, **image_kwargs) :
        """ Change *self.main_plot*`s currently displayed
        `image_item <data_slicer.imageplot.ImagePlot.image_item>` to the slice 
        of *self.data_handler.data* corresponding to the current value of 
        *self.z*.
        """
        logger.debug('update_main_plot()')

        self.data_handler.update_image_data()

        logger.debug('self.image_data.shape={}'.format(self.image_data.shape))

        if image_kwargs != {} :
            self.image_kwargs = image_kwargs

        # Add image to main_plot
        self.set_image(self.image_data, **image_kwargs)

    def set_axes(self) :
        """ Set the x- and y-scales of the plots. The :class: `ImagePlot 
        <data_slicer.imageplot.ImagePlot>` object takes care of keeping the 
        scales as they are, once they are set.
        """
        xaxis = self.data_handler.axes[0]
        yaxis = self.data_handler.axes[1]
        zaxis = self.data_handler.axes[2]
        logger.debug(('set_axes(): len(xaxis), len(yaxis)={}, ' +
                      '{}').format(len(xaxis), len(yaxis)))
        self.main_plot.set_xscale(xaxis)
        self.main_plot.set_yscale(yaxis, update=True)
        self.main_plot.fix_viewrange()

        # Kind of a hack to get the crosshair to the right position...
        self.cut_plot.sig_axes_changed.emit()
        self.cutline.initialize()

    def update_x_plot(self) :
        logger.debug('update_x_plot()')
        # Get shorthands for plot
        xp = self.x_plot
        try :
            old = xp.listDataItems()[0]
            xp.removeItem(old)
        except IndexError :
            pass

        # Get the correct position indicator
        pos = self.cut_plot.pos[1]
        i_x = int( min(pos.get_value(), pos.allowed_values.max()-1))
        logger.debug(('xp.pos.get_value()={}; i_x: '
                      '{}').format(xp.pos.get_value(), i_x))
        xprofile = self.data_handler.cut_data[i_x]
        y = np.arange(len(xprofile)) + 0.5
        xp.plot(xprofile, y)

    def update_y_plot(self) :
        logger.debug('update_y_plot()')
        # Get shorthands for plot
        yp = self.y_plot
        try :
            old = yp.listDataItems()[0]
            yp.removeItem(old)
        except IndexError :
            pass
        # Get the correct position indicator
        pos = self.cut_plot.pos[0]
        i_y = int( min(pos.get_value(), pos.allowed_values.max()-1)) 
        logger.debug(('yp.pos.get_value()={}; i_y: '
                      '{}').format(yp.pos.get_value(), i_y))
        yprofile = self.data_handler.cut_data[:,i_y]
        x = np.arange(len(yprofile)) + 0.5
        yp.plot(x, yprofile)

    def update_xy_plots(self) :
        """ Update the x and y profile plots. """
        logger.debug('update_xy_plots()')
        self.update_x_plot()
        self.update_y_plot()

    def set_cmap(self, cmap) :
        """ Set the colormap to *cmap* where *cmap* is one of the names 
        registered in `<data_slicer.cmaps>` which includes all matplotlib and 
        kustom cmaps.
        """
        try :
            self.cmap = cmaps[cmap]
        except KeyError :
            print('Invalid colormap name. Use one of: ')
            print(cmaps.keys())
        # Since the cmap changed it forgot our settings for alpha and gamma
        self.cmap.set_alpha(self.alpha)
        self.cmap.set_gamma(self.gamma)
        self.cmap_changed()

    def cmap_changed(self) :
        """ Recalculate the lookup table and redraw the plots such that the 
        changes are immediately reflected.
        """
        self.lut = self.cmap.getLookupTable()
        self.redraw_plots()

    def redraw_plots(self, image=None) :
        """ Redraw plotted data to reflect changes in data or its colors. """
        logger.debug('redraw_plots()')
        try :
            # Redraw main plot
            self.set_image(image, 
                           displayed_axes=self.data_handler.displayed_axes)
            # Redraw cut plot
            self.update_cut()
        except AttributeError as e :
            # In some cases (namely initialization) the mainwindow is not 
            # defined yet
            logger.debug('AttributeError: {}'.format(e))

    def set_image(self, image=None, *args, **kwargs) :
        """ Wraps the underlying ImagePlot3d's set_image method.
        See :func: `<data_slicer.imageplot.ImagePlot3d.set_image>`. *image* can 
        be *None* i.e. in order to just update the plot with a new colormap.
        """
        # Reset the transformation
        self.transform_factors = []
        if image is None :
            image = self.image_data
        self.main_plot.set_image(image, *args, lut=self.lut, **kwargs)

    def update_cut(self) :
        """ Take a cut of *self.data_handler.data* along *self.cutline*. This 
        is used to update only the cut plot without affecting the main plot.
        """
        logger.debug('update_cut()')
        try :
            cut = self.cutline.get_array_region(self.data_handler.get_data(), 
                                       self.main_plot.image_item, 
                                       axes=self.data_handler.displayed_axes)
        except Exception as e :
            logger.error(e)
            return

        self.data_handler.cut_data = cut
        self.cut_plot.set_image(cut, lut=self.lut)

    def on_cutline_initialized(self) :
        """ Need to reconnect the signal to the cut_plot. And directly update 
        the cut_plot.
        """
        self.cutline.sig_region_changed.connect(self.update_cut)
        self.update_cut()

    def on_gamma_slider_move(self) :
        """ When the user moves the gamma slider, update gamma. """
        ind = min(int(100*self.scalebar1.pos.get_value()), len(self.gamma_values)-1)
        gamma = self.gamma_values[ind]
        self.set_gamma(gamma)

    def on_vmax_slider_move(self) :
        """ When the user moves the vmax slider, update vmax. """
        vmax = int(np.round(100*self.scalebar2.pos.get_value()))/100
        self.set_vmax(vmax)

    def set_alpha(self, alpha) :
        """ Set the alpha value of the currently used cmap. *alpha* can be a 
        single float or an array of length ``len(self.cmap.color)``.
        """
        self.alpha = alpha
        self.cmap.set_alpha(alpha)
        self.cmap_changed()

    def set_gamma(self, gamma=1) :
        """ Set the exponent for the power-law norm that maps the colors to 
        values. I.e. the values where the colours are defined are mapped like 
        ``y=x**gamma``.
        """
        self.gamma = gamma
        self.cmap.set_gamma(gamma)
        self.cmap_changed()
        # Additionally, we need to update the slider position. We need to 
        # hack a bit to avoid infinite signal loops: avoid emitting of the 
        # signal and update the slider position by hand with a call to 
        # scalebar1.set_position().
        self.scalebar1.pos._value = indexof(gamma, self.gamma_values)/100
        self.scalebar1.set_position()

    def set_vmax(self, vmax=1) :
        """ Set the relative maximum of the colormap. I.e. the colors are 
        mapped to the range `min(data)` - `vmax*max(data)`.
        """
        self.vmax = vmax
        self.cmap.set_vmax(vmax)
        self.cmap_changed()
        # Additionally, we need to update the slider position. We need to 
        # hack a bit to avoid infinite signal loops: avoid emitting of the 
        # signal and update the slider position by hand with a call to 
        # scalebar1.set_position().
        self.scalebar2.pos._value = vmax
        self.scalebar2.set_position()
    
    def cmap_changed(self) :
        """ Recalculate the lookup table and redraw the plots such that the 
        changes are immediately reflected.
        """
        self.lut = self.cmap.getLookupTable()
        self.redraw_plots()

if __name__=="__main__" :
    from data_slicer import set_up_logging
    app = QtGui.QApplication([])
    mw = MainWindow()
    app.exec_()

