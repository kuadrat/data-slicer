"""
PIT is a widget that combines slices from different sides with intensity 
distribution curves and other convenient features.
"""

import importlib
import logging
import pathlib
import pickle
import pkg_resources
import sys
from copy import copy
from types import FunctionType

import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
import pyqtgraph.console
from pyqtgraph.Qt import QtGui, QtCore
from qtconsole.rich_ipython_widget import RichIPythonWidget, RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager

import data_slicer.dataloading as dl
# Importing ds_cmap is necessary in order to load from pickle
from data_slicer.cmaps import convert_ds_to_matplotlib, ds_cmap, \
                              load_user_cmaps
from data_slicer.cutline import Cutline
from data_slicer.imageplot import *
from data_slicer.model import Model
from data_slicer.utilities import CACHED_CMAPS_FILENAME, CONFIG_DIR, \
                                  make_slice, plot_cuts, TracedVariable

logger = logging.getLogger('ds.'+__name__)

# +-----------------------------------------+ #
# | Appearance definitions and preparations | # ================================
# +-----------------------------------------+ #

app_style="""
QMainWindow{
    background-color: black;
    }
"""

console_style = """
color: rgb(0, 0, 0);
background-color: rgb(255, 255, 255);
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
SAMPLE_DATA_FILE = data_path + 'pit.p'

# Add the plugin directory to the python path
plugin_path = pathlib.Path.home() / CONFIG_DIR / 'plugins/'
sys.path.append(str(plugin_path))

# Load cmaps
with open(data_path + CACHED_CMAPS_FILENAME, 'rb') as f :
    cmaps = pickle.load(f)
load_user_cmaps(cmaps)

# Number of dimensions to handle
NDIM = 3

# +-----------------------+ #
# | Main class definition | # ==================================================
# +-----------------------+ #

class PITDataHandler() :
    """ Object that keeps track of a set of 3D data and allows 
    manipulations on it. In a Model-View-Controller framework this could be 
    seen as the Model, while :class:`MainWindow <data_slicer.pit.MainWindow>` 
    would be the View part.
    """
    def __init__(self, main_window) :
        self.main_window = main_window

        # Initialize instance variables
        # np.array that contains the 3D data
        self.data = None
        self.axes = np.array([[0, 1], [0, 1], [0, 1]])
        # Indices of *data* that are displayed in the main plot 
        self.displayed_axes = (0,1)
        # Index along the z axis at which to produce a slice
        self.z = TracedVariable(0, name='z')
        ## Number of slices to integrate along z
        #integrate_z = TracedVariable(value=0, name='integrate_z')
        # How often we have rolled the axes from the original setup
        self._roll_state = 0

    def get_config_dir(self) :
        """ Return the path to the configuration directory on this system. """
        return pathlib.Path.home() / CONFIG_DIR

    def get_data(self) :
        """ Convenience `getter` method. Allows writing ``self.get_data()``
        instead of ``self.data.get_value()``. 
        """
        return self.data.get_value()

    def set_data(self, data) :
        """ Convenience `setter` method. Allows writing ``self.set_data(d)`` 
        instead of ``self.data.set_value(d)``. 
        """
        self.data.set_value(data)

    def prepare_data(self, data, axes=3*[None]) :
        """ Load the specified data and prepare the corresponding z range. 
        Then display the newly loaded data.

        **Parameters**

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
        self.z.sig_value_changed.connect( \
            lambda : self.main_window.update_main_plot(emit=False))
        self.data.sig_value_changed.connect(self.on_data_change)

        self.main_window.update_main_plot()
        self.main_window.set_axes()

    def load(self, filename) :
        """ Alias to :func:`open <data_slicer.pit.PITDataHandler.open>`. """ 
        self.open(filename)

    def open(self, filename) :
        """ Open a file that's readable by :mod:`dataloading 
        <data_slicer.dataloading>`.
        """
        D = dl.load_data(filename)
        self.prepare_data(D.data, D.axes)

    def get_main_data(self) :
        """ Return the 2d array that is currently displayed in the main plot. 
        """
        return self.main_window.main_plot.image_data

    def get_cut_data(self) :
        """ Return the 2d array that is currently displayed in the cut plot. 
        """
        return self.main_window.cut_plot.image_data

    def get_hprofile(self) :
        """ Return an array containing the y values displayed in the 
        horizontal profile plot (mw.y_plot).

        .. seealso::
            :func:`data_slicer.imageplot.CursorPlot.get_data`
        """
        return self.main_window.y_plot.get_data()[1]

    def get_vprofile(self) :
        """ Return an array containing the x values displayed in the 
        vertical profile plot (mw.x_plot).

        .. seealso::
            :func:`data_slicer.imageplot.CursorPlot.get_data`
        """
        return self.main_window.x_plot.get_data()[0]

    def get_iprofile(self) :
        """ Return an array containing the y values displayed in the 
        integrated intensity profile plot (mw.integrated_plot).

        .. seealso::
            :func:`data_slicer.imageplot.CursorPlot.get_data`
        """
        return self.main_window.integrated_plot.get_data()[1]


    def update_z_range(self) :
        """ When new data is loaded or the axes are rolled, the limits and 
        allowed values along the z dimension change.
        """
        # Determine the new ranges for z
        self.zmin = 0
        self.zmax = self.get_data().shape[2] - 1

        self.z.set_allowed_values(range(self.zmin, self.zmax+1))
#        self.z.set_value(self.zmin)

    def reset_data(self) :
        """ Put all data and metadata into its original state, as if it was 
        just loaded from file.
        """
        logger.debug('reset_data()')
        self.set_data(copy(self.original_data))
        self.axes = copy(self.original_axes)
        self.prepare_axes()
        # Roll back to the view we had before reset_data was called
        self._roll_axes(self._roll_state, update=False)

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

    def on_z_dim_change(self) :
        """ Called when either completely new data is loaded or the dimension 
        from which we look at the data changed (e.g. through :func:`roll_axes 
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
        Skip this if the z value happens to be out of range, which can happen 
        if the image data changes and the z scale hasn't been updated yet.
        """
        logger.debug('update_image_data()')
        z = self.z.get_value()
        integrate_z = \
        int(self.main_window.integrated_plot.slider_width.get_value()/2)
        data = self.get_data()
        try :
            self.main_window.image_data = make_slice(data, dim=2, index=z, 
                                                     integrate=integrate_z) 
        except IndexError :
            logger.debug(('update_image_data(): z index {} out of range for '
                          'data of length {}.').format(
                             z, self.image_data.shape[0]))

    def roll_axes(self, i=1) :
        """ Change the way we look at the data cube. While initially we see 
        an Y vs. X slice in the main plot, roll it to Z vs. Y. A second call 
        would roll it to X vs. Z and, finally, a third call brings us back to 
        the original situation.

        **Parameters**

        =  =====================================================================
        i  int; Number of dimensions to roll.
        =  =====================================================================
        """
        self._roll_axes(i, update=True)

    def _roll_axes(self, i=1, update=True) :
        """ Backend for :func:`roll_axes <arpys.pit.PITDataHandler.roll_axes>`
        that allows suppressing updating the roll-state, which is useful for
        :func:`reset_data <arpys.pit.PITDataHandler.reset_data>`.
        """
        logger.debug('roll_axes()')
        data = self.get_data()
        res = np.roll([0, 1, 2], i)
        self.axes = np.roll(self.axes, -i)
        self.set_data(np.moveaxis(data, [0,1,2], res))
        # Setting the data triggers a call to self.redraw_plots()
        self.on_z_dim_change()
        # Reset cut_plot's axes
        cp = self.main_window.cut_plot
#        cp.xlim = None
#        cp.ylim = None
        self.main_window.set_axes()
        if update :
            self._roll_state = (self._roll_state + i) % NDIM

    def lineplot(self, plot='main', dim=0, ax=None, n=10, offset=0.2, lw=0.5, 
                 color='k', label_fmt='{:.2f}', n_ticks=5, **getlines_kwargs) :
        """
        Create a matplotlib figure with *n* lines extracted out of one of the 
        visible plots. The lines are normalized to their global maximum and 
        shifted from each other by *offset*.
        See :func:`get_lines <data_slicer.utilities.get_lines>` for more 
        options on the extraction of the lines.
        This wraps the :class:`ImagePlot <data_slicer.imageplot.ImagePlot>`'s
        lineplot method.

        **Parameters**

        ===============  =======================================================
        plot             str; either "main" or "cut", specifies from which 
                         plot to extract the lines.
        dim              int; either 0 or 1, specifies in which direction to 
                         take the lines.
        ax               matplotlib.axes.Axes; the axes in which to plot. If 
                         *None*, create a new figure with a fresh axes.
        n                int; number of lines to extract.
        offset           float; spacing between neighboring lines.
        lw               float; linewidth of the plotted lines.
        color            any color argument understood by matplotlib; color 
                         of the plotted lines.
        label_fmt        str; a format string for the ticklabels.
        n_ticks          int; number of ticks to print.
        getlines_kwargs  other kwargs are passed to :func:`get_lines 
                         <data_slicer.utilities.get_lines>`
        ===============  =======================================================

        **Returns**

        ===========  ===========================================================
        lines2ds     list of Line2D objects; the drawn lines.
        xticks       list of float; locations of the 0 intensity value of 
                     each line.
        xtickvalues  list of float; if *momenta* were supplied, corresponding 
                     xtick values in units of *momenta*. Otherwise this is 
                     just a copy of *xticks*.
        xticklabels  list of str; *xtickvalues* formatted according to 
                     *label_fmt*.
        ===========  ===========================================================

        .. seealso::
            :func:`get_lines <data_slicer.utilities.get_lines>`
        """
        # Get the specified data
        if plot == 'main' :
            imageplot = self.main_window.main_plot
        elif plot == 'cut' :
            imageplot = self.main_window.cut_plot
        else :
            raise ValueError('*plot* should be one of ("main", "cut").')

        # Create a mpl axis object if none was given
        if ax is None : fig, ax = plt.subplots(1)

        return imageplot.lineplot(ax=ax, dim=dim, n=n, offset=offset, lw=lw, 
                                  color=color, label_fmt=label_fmt, 
                                  n_ticks=n_ticks, **getlines_kwargs)

    def plot_all_slices(self, dim=2, integrate=0, zs=None, labels='default', 
                        max_ppf=16, max_nfigs=2, **kwargs) :
        """ Wrapper for :func:`plot_cuts <data_slicer.utilities.plot_cuts>`.
        Plot all (or only the ones specified by `zs`) slices along dimension 
        `dim` on separate suplots onto matplotlib figures.

        **Parameters**

        =========  ============================================================
        dim        int; one of (0,1,2). Dimension along which to take the cuts.
        integrate  int or 'full'; number of slices to integrate around each 
                   extracted cut. If 'full', take the maximum number possible, 
                   depending on *zs* and whether the number of cuts is reduced 
                   due to otherwise exceeding *max_nfigs*.
        zs         1D np.array; selection of indices along dimension `dim`. 
                   Only the given indices will be plotted.
        labels     1D array/list of length z. Optional labels to assign to the 
                   different cuts. By default the values of the respective axis
                   are used. Set to *None* to suppress labels.
        max_ppf    int; maximum number of plots per figure.
        max_nfigs  int; maximum number of figures that are created. If more 
                   would be necessary to display all plots, a warning is 
                   issued and only every N'th plot is created, where N is 
                   chosen such that the whole 'range' of plots is represented 
                   on the figures. 
        kwargs     dict; keyword arguments passed on to :func:`pcolormesh 
                   <matplotlib.axes._subplots.AxesSubplot.pcolormesh>`. 
                   Additionally, the kwarg `gamma` for power-law color mapping 
                   is accepted.
        =========  ============================================================

        .. seealso::
            :func:`~data_slicer.utilities.plot_cuts`
        """
        data = self.get_data()
        if labels == 'default' :
            # Use the values of the respective axis as default labels
            labels = self.axes[dim]

        # The default values for the colormap are taken from the main_window 
        # settings
        gamma = self.main_window.gamma
        vmax = self.main_window.vmax * data.max()
        cmap = convert_ds_to_matplotlib(self.main_window.cmap, 
                                        self.main_window.cmap_name)
        plot_cuts(data, dim=dim, integrate=integrate, zs=zs, labels=labels, 
                  cmap=cmap, vmax=vmax, gamma=gamma, max_ppf=max_ppf, 
                  max_nfigs=max_nfigs)

    def overlay_model(self, model) :
        """ Display a model over the data. *model* should be function of two 
        variables, namely the currently displayed x- and y-axes.

        **Parameters**

        =====  =================================================================
        model  callable or :class:`Model <data_slicer.model.Model>`;
        =====  =================================================================

        .. seealso::
            :class:`Model <data_slicer.model.Model>`
        """
        if isinstance(model, FunctionType) :
            model = Model(model)
        elif not isinstance(model, Model) :
            raise ValueError('*model* has to be a function or a '
                             'data_slicer.Model instance')
        # Remove the old model
        self.remove_model()

        # Calculate model data in the required range and get an isocurve
        self.model = model
        # Bypass the minimum axes size limitation
        self.model.MIN_AXIS_LENGTH = 0
        model_axes = [self.axes[i] for i in self.displayed_axes]
        # Invert order for transposed view
        if self.main_window.main_plot.transposed.get_value() :
            self.model.set_axes(model_axes[::-1])
        else :
            self.model.set_axes(model_axes)
        self._update_isocurve()
        self._update_model_cut()

        # Connect signal handling
        self.z.sig_value_changed.connect(self._update_isocurve)
        self.main_window.cutline.sig_region_changed.connect(self._update_model_cut)

    def remove_model(self) :
        """ Remove the current model's visible and invisible parts. """
        # Remove the visible items from the plots
        try :
            self.main_window.main_plot.removeItem(self.iso)
            self.iso = None
            self.model = None
        except AttributeError :
            logger.debug('remove_model(): no model to remove found.')
            return
        # Remove signal handling
        try :
            self.z.sig_value_changed.disconnect(self._update_isocurve)
        except TypeError as e :
            logger.debug(e)
        try :
            self.main_window.cutline.sig_region_changed.disconnect(
                self._update_model_cut)
        except TypeError as e :
            logger.debug(e)

        # Redraw clean plots
        self.main_window.redraw_plots()

    def _update_isocurve(self) :
        try :
            self.iso = self.model.get_isocurve(self.z.get_value(), 
                                               axisOrder='row-major')
        except AttributeError :
            logger.debug('_update_isocurve(): no model found.')
            return
        # Make sure the isocurveItem is above the plot and add it to the main 
        # plot
        self.iso.setZValue(10)
        self.iso.setParentItem(self.main_window.main_plot.image_item)

    def _update_model_cut(self) :
        try :
            model_cut = self.main_window.cutline.get_array_region(
                            self.model.data.T,
                            self.main_window.main_plot.image_item,
                            self.displayed_axes)
        except AttributeError :
            logger.debug('_update_model_cut(): model or data not found.')
            return
        self.model_cut = self.main_window.cut_plot.plot(model_cut, 
                                                        pen=self.iso.pen)

class MainWindow(QtGui.QMainWindow) :
    """ The main window of PIT. Defines the basic GUI layouts and 
    acts as the controller, keeping track of the data and handling the 
    communication between the different GUI elements. 
    """
    title = 'Python Image Tool'
    # width, height in pixels
    size = (1200, 800)

    def __init__(self, data=None, background='default') :
        super().__init__()

        # Initialize instance variables
        # Plot transparency alpha
        self.alpha = 1
        # Plot powerlaw normalization exponent gamma
        self.gamma = 1
        # Relative colormap maximum
        self.vmax = 1

        # Need to store original transformation information for `rotate()`
        self._transform_factors = []

        self.data_handler = PITDataHandler(self)

         # Aesthetics
        self.setStyleSheet(app_style)
        self.set_cmap(DEFAULT_CMAP)

        # Autoload plugins (needs to happen before _init_UI() because the 
        # plugins are needed to populate the console's namespace)
        self._autoloaded_plugins = self._autoload_plugins()

        self._init_UI()

        # Connect signal handling
        self.cutline.sig_initialized.connect(self.on_cutline_initialized)

        # Prepare sample data for initialization
        if data is None :
            with open(SAMPLE_DATA_FILE, 'rb') as f :
                data = pickle.load(f)
        self.data_handler.prepare_data(data)

    def _init_UI(self) :
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
        self.main_plot.show_cursor()
        self.cut_plot = CrosshairImagePlot(name='cut_plot')

        # Create the intensity distribution plots
        self.x_plot = CursorPlot(name='x_plot', orientation='horizontal')
        self.y_plot = CursorPlot(name='y_plot')
        self.x_plot.register_traced_variable(self.cut_plot.pos[1])
        self.y_plot.register_traced_variable(self.cut_plot.pos[0])
        self.x_plot.pos.sig_value_changed.connect(self.update_y_plot)
        self.y_plot.pos.sig_value_changed.connect(self.update_x_plot)

#        self.cut_plot.sig_image_changed.connect(self.update_xy_plots)

        # Set up the python console
        namespace = dict(pit=self.data_handler, mw=self)
        # Add the autoloaded plugins
        for name, plugin in self._autoloaded_plugins :
            namespace.update({name: plugin})
        self.console = EmbedIPython(**namespace)
        self.console.kernel.shell.run_cell('%pylab qt')
        self.console.setStyleSheet(console_style)
        for name, plugin in self._autoloaded_plugins :
            self.print_to_console('Autoloaded plugin {}'.format(name))
#        self.console.syntax_style = 'monokai'
        
        # Connect singal handling for printing to console
        self.main_plot.sig_clicked.connect(self.print_to_console)
        self.cut_plot.sig_clicked.connect(self.print_to_console)

        # Create the integrated intensity plot
        ip = CursorPlot(name='z selector')
        ip.register_traced_variable(self.data_handler.z)
        ip.change_width_enabled = True
        ip.slider_width.sig_value_changed.connect( \
            lambda : self.update_main_plot(emit=False))
        self.integrated_plot = ip

        # Disable context menus
        for plot in [self.x_plot, self.y_plot, self.integrated_plot] :
            plot.plotItem.vb.setMenuEnabled(False)

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
        self._align()
        self.show()

    def _align(self) :
        """ Align all the GUI elements in the QLayout::
        
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

    def _autoload_plugins(self) :
        """ Load all the plugins specified in the config file 
        ``CONF_DIR/plugins/autoload.txt``.
        """
        logger.debug('Autoloading plugins...')

        # Parse the autoload.txt file if it exists
        try :
            with open(plugin_path / 'autoload.txt', 'r') as f :
                lines = f.readlines()
        except FileNotFoundError :
            logger.debug('autoload.txt not found at {}.'.format(plugin_path))
            return []

        # Load all the plugins!
        plugins = []
        for line in lines :
            # Skip commented lines
            if line.startswith('#') : continue
            plugin_name = line.strip()
            plugin = self.load_plugin(plugin_name)
            # Try to use a shortname
            if plugin.shortname is not None :
                plugin_name = plugin.shortname
            plugins.append((plugin_name, plugin))
        return plugins

    def load_plugin(self, plugin_name) :
        """ Load a user supplied plugin and connect the plugin's `main` class 
        with PIT.
        The plugin should be a python module which is placed in the 
        pythonpath or in the `plugins` directory. 

        **Parameters**

        ===========  ===========================================================
        plugin_name  str; name of the plugin module as it appears in the 
                     `plugins` directory.
        ===========  ===========================================================
        """
        # For debug purposes, determine the full path to the module location.
        path_to_plugin = str(plugin_path / plugin_name)
        logger.debug('Importing {}.'.format(path_to_plugin))
        # Load the module and connect it to PIT
        module = importlib.import_module(plugin_name)
        plugin = module.main(self, self.data_handler)
        print('Importing plugin {} ({}).'.format(plugin_name, plugin.name))
#        self.print_to_console('Importing plugin {} ({}).'.format(plugin_name, 
#                                                                 plugin.name))
        return plugin

    def print_to_console(self, message) :
        """ Print a *message* to the embedded ipython console. """
        self.console.kernel.stdout.write(str(message) + '\n')

    def update_main_plot(self, **image_kwargs) :
        """ Change *self.main_plot*`s currently displayed
        :class:`image_item <data_slicer.imageplot.ImagePlot.image_item>` to 
        the slice of *self.data_handler.data* corresponding to the current 
        value of *self.z*.
        """
        logger.debug('update_main_plot()')

        self.data_handler.update_image_data()

        logger.debug('self.image_data.shape={}'.format(self.image_data.shape))

        if image_kwargs != {} :
            self.image_kwargs = image_kwargs

        # Add image to main_plot
        self.set_image(self.image_data, **image_kwargs)

    def set_axes(self) :
        """ Set the x- and y-scales of the plots. The :class:`ImagePlot 
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
        pos = self.y_plot.pos
        i_x = int( min(pos.get_value(), pos.allowed_values.max()-1))
        logger.debug(('xp.pos.get_value()={}; i_x: '
                      '{}').format(xp.pos.get_value(), i_x))
        if not self.main_plot.transposed.get_value() :
            xprofile = self.data_handler.cut_data[i_x]
        else :
            xprofile = self.data_handler.cut_data[:,i_x]
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
        pos = self.x_plot.pos
        i_y = int( min(pos.get_value(), pos.allowed_values.max()-1)) 
        logger.debug(('yp.pos.get_value()={}; i_y: '
                      '{}').format(yp.pos.get_value(), i_y))
        if not self.main_plot.transposed.get_value() :
            yprofile = self.data_handler.cut_data[:,i_y]
        else :
            yprofile = self.data_handler.cut_data[i_y]
        x = np.arange(len(yprofile)) + 0.5
        yp.plot(x, yprofile)

    def update_xy_plots(self) :
        """ Update the x and y profile plots. """
        logger.debug('update_xy_plots()')
        self.update_x_plot()
        self.update_y_plot()

    def set_cmap(self, cmap) :
        """ Set the colormap to *cmap* where *cmap* is one of the names 
        registered in :mod:`<data_slicer.cmaps>` which includes all matplotlib and 
        kustom cmaps.
        """
        try :
            self.cmap = cmaps[cmap]
        except KeyError :
            print('Invalid colormap name. Use one of: ')
            print(cmaps.keys())
        self.cmap_name = cmap
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

    def transpose(self) :
        """ Transpose the main_plot, i.e. swap out its x- and y-axes. This 
        wraps the main_plot's :meth:`transpose 
        <data_slicer.imageplot.ImagePlot.transpose>` method.
        """
        self.main_plot.transpose()

    def rotate(self, alpha=0) :
        """ Rotate the main image by the given angle *alpha* (in degrees). """
        self.main_plot.rotate(alpha)

    def keyPressEvent(self, event) :
        """ Define all responses to keyboard presses. 
        Currently defined:

        ===     ================================================================
        key     action
        ===     ================================================================
        r       Flip orientation of cutline. Also useful to bring it back to 
                visibility.
        ===     ================================================================
        """
        key = event.key()
        logger.debug('keyPressEvent(): key={}'.format(key))
#        if key == QtCore.Qt.Key_Right :
#            self.data_handler.z.set_value(self.data_handler.z.get_value() + 1)
#        elif key == QtCore.Qt.Key_Left :
#            self.data_handler.z.set_value(self.data_handler.z.get_value() - 1)
        # Flip Cutline on *R* key
        if key == QtCore.Qt.Key_R :
            self.cutline.flip_orientation()
        else :
            event.ignore()
            return
        # If any if-statement matched, we accepted the event
        event.accept()

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
        See :func:`~data_slicer.imageplot.ImagePlot3d.set_image`. *image* can 
        be *None* i.e. in order to just update the plot with a new colormap.
        """
        # Reset the transformation
        self._transform_factors = []
        if image is None :
            image = self.image_data
        self.main_plot.set_image(image, *args, lut=self.lut, **kwargs)

    def update_cut(self) :
        """ Take a cut of *self.data_handler.data* along *self.cutline*. This 
        is used to update only the cut plot without affecting the main plot.
        """
        logger.debug('update_cut()')
        data = self.data_handler.get_data()
        axes = self.data_handler.displayed_axes
        # Transpose, if necessary
        if self.main_plot.transposed.get_value() :
            axes = axes[::-1]
        try :
            cut = self.cutline.get_array_region(data, 
                                                self.main_plot.image_item,
                                                axes=axes)
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
        ind = min(int(100*self.scalebar1.pos.get_value()), 
                  len(self.gamma_values)-1)
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

def start_main_window() :
    app = QtGui.QApplication([])
    mw = MainWindow()
    app.exec_()

if __name__=="__main__" :
    from data_slicer import set_up_logging
    start_main_window()

