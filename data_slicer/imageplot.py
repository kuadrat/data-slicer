""" matplotlib pcolormesh equivalent in pyqtgraph (more or less) """

import logging

import matplotlib.pyplot as plt
import pyqtgraph as pg
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from numpy import arange, array, clip, inf, linspace, ndarray
from pyqtgraph import Qt as qt #import QtCore
from pyqtgraph import PlotDataItem
from pyqtgraph.graphicsItems.ImageItem import ImageItem
from pyqtgraph.widgets import PlotWidget, GraphicsView

from data_slicer.dsviewbox import DSViewBox
from data_slicer.utilities import get_lines, TracedVariable, indexof

logger = logging.getLogger('ds.'+__name__)

BASE_LINECOLOR = (255,255,0,255)
HOVER_COLOR = (195,155,0,255)

class MPLExportDialog(qt.QtGui.QDialog) :
    """ A dialog that provides a GUI to 
    :meth:`~data_slicer.imageplot.ImagePlot.mpl_export`.
    """
    figwidth = 5
    figheight = 5

    def __init__(self, imageplot, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        self.imageplot = imageplot

        # Convert the lookuptable (lut) to a matplotlib colormap
        lut = self.imageplot.image_item.lut
        lut = lut/lut.max()
        cmap_array = array([[a[0], a[1], a[2], 1.] for a in lut])
        self.cmap = ListedColormap(cmap_array)

        ## Dialog window layout
        self.setWindowTitle('MPL Export Options')

        # Title textbox
        self.label_title = qt.QtGui.QLabel('Title')
        self.box_title = qt.QtGui.QLineEdit(self)

        # x- and y-axis textboxes
        self.label_xlabel = qt.QtGui.QLabel('x axis label')
        self.box_xlabel = qt.QtGui.QLineEdit(self)
        self.label_ylabel = qt.QtGui.QLabel('y axis label')
        self.box_ylabel = qt.QtGui.QLineEdit(self)

        # Invert and transpose checkboxes
        self.checkbox_invertx = qt.QtGui.QCheckBox('invert x')
        self.checkbox_inverty = qt.QtGui.QCheckBox('invert y')
        self.checkbox_transpose = qt.QtGui.QCheckBox('transpose')

        # x limits
        self.label_xlim = qt.QtGui.QLabel('x limits')
        self.box_xmin = qt.QtGui.QLineEdit()
        self.box_xmin.setValidator(qt.QtGui.QDoubleValidator())
        self.box_xmax = qt.QtGui.QLineEdit()
        self.box_xmax.setValidator(qt.QtGui.QDoubleValidator())

        # y limits
        self.label_ylim = qt.QtGui.QLabel('y limits')
        self.box_ymin = qt.QtGui.QLineEdit()
        self.box_ymin.setValidator(qt.QtGui.QDoubleValidator())
        self.box_ymax = qt.QtGui.QLineEdit()
        self.box_ymax.setValidator(qt.QtGui.QDoubleValidator())

        # Figsize
        self.label_width = qt.QtGui.QLabel('Figure width (inch)')
        self.box_width = qt.QtGui.QLineEdit()
        self.box_width.setValidator(qt.QtGui.QDoubleValidator(0, 99, 2))
        self.box_width.setText(str(self.figwidth))
        self.label_height = qt.QtGui.QLabel('Figure height (inch)')
        self.box_height = qt.QtGui.QLineEdit()
        self.box_height.setValidator(qt.QtGui.QDoubleValidator(0, 99, 2))
        self.box_height.setText(str(self.figheight))

        # Make changes update the figure
        for box in [self.box_title, self.box_xlabel, self.box_ylabel, 
                    self.box_xmin, self.box_xmax, self.box_ymin, 
                    self.box_ymax, self.box_width, self.box_height] :
#            box.editingFinished.connect(self.plot_preview)
            box.textChanged.connect(self.plot_preview)
        for checkbox in [self.checkbox_invertx, self.checkbox_inverty, 
                         self.checkbox_transpose] :
            checkbox.stateChanged.connect(self.plot_preview)

        # Figsize warning label
        self.label_figsize = qt.QtGui.QLabel('Preview figure size is not to '
                                             'scale.')

        # Preview canvas
        self.figure = Figure(figsize=(self.figwidth, self.figheight), 
                             constrained_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)

        # 'OK' and 'Cancel' buttons
        QBtn = qt.QtGui.QDialogButtonBox.Ok | qt.QtGui.QDialogButtonBox.Cancel
        self.button_box = qt.QtGui.QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.plot_preview()
        self.align()

    def align(self) :
        """ Create and apply the dialog's layout. """
        layout = qt.QtGui.QGridLayout()
        ncol = 4
        i = 1
        # Title
        layout.addWidget(self.label_title, i, 1, 1, 1)
        layout.addWidget(self.box_title, i, 2, 1, 1)
        i += 1
        # x label
        layout.addWidget(self.label_xlabel, i, 1, 1, 1)
        layout.addWidget(self.box_xlabel, i, 2, 1, 1)
        i += 1
        # y label
        layout.addWidget(self.label_ylabel, i, 1, 1, 1)
        layout.addWidget(self.box_ylabel, i, 2, 1, 1)
        i += 1
        # Invert and transpose checkboxes
        layout.addWidget(self.checkbox_invertx, i, 1, 1, 1)
        layout.addWidget(self.checkbox_inverty, i, 2, 1, 1)
        layout.addWidget(self.checkbox_transpose, i, 3, 1, 1)
        i += 1
        # Limits
        layout.addWidget(self.label_xlim, i, 1, 1, 1)
        xlims = qt.QtGui.QHBoxLayout()
        xlims.addWidget(self.box_xmin)
        xlims.addWidget(self.box_xmax)
        layout.addLayout(xlims, i, 2, 1, 1)
        layout.addWidget(self.label_ylim, i, 3, 1, 1)
        ylims = qt.QtGui.QHBoxLayout()
        ylims.addWidget(self.box_ymin)
        ylims.addWidget(self.box_ymax)
        layout.addLayout(ylims, i, 4, 1, 1)
        i += 1
        # Figsize fields
        layout.addWidget(self.label_width, i, 1, 1, 1)
        layout.addWidget(self.box_width, i, 2, 1, 1)
        layout.addWidget(self.label_height, i, 3, 1, 1)
        layout.addWidget(self.box_height, i, 4, 1, 1)
        i += 1
        # Preview
        layout.addWidget(self.label_figsize, i, 1, 1, ncol)
        i += 1
        layout.addWidget(self.canvas, i, 1, 1, ncol)
        i += 1
        # OK and Cancel buttons
        layout.addWidget(self.button_box, i, 1, 1, ncol)
        self.setLayout(layout)

    def plot_preview(self) :
        """ Update the plot in the preview window with the currently selected 
        options. 
        """
        # Remove previous plot and get up-to-date data
        self.ax.clear()
        ip = self.imageplot

        xaxis, yaxis, data = ip.xscale, ip.yscale, ip.image_data.T
        # Fix unassigned x- and yscales
        if xaxis is None :
            xaxis = range(data.shape[1])
        if yaxis is None :
            yaxis = range(data.shape[0])
        # Transpose
        if self.checkbox_transpose.isChecked() :
            xaxis, yaxis, data = yaxis, xaxis, data.T
        mesh = self.ax.pcolormesh(xaxis, yaxis, data, cmap=self.cmap)

        # Limits
        limits = [b.text() for b in [self.box_xmin, self.box_xmax, 
                                     self.box_ymin, self.box_ymax]]
        datalimits = [xaxis[0], xaxis[-1], yaxis[0], yaxis[-1]]
        for i,lim in enumerate(limits) :
            if lim == '' :
                limits[i] = datalimits[i]
            else :
                limits[i] = float(lim)
        self.ax.set_xlim([limits[0], limits[1]])
        self.ax.set_ylim([limits[2], limits[3]])

        # Apply options
        invertx = self.checkbox_invertx.isChecked() 
        inverty = self.checkbox_inverty.isChecked() 
        if invertx : self.ax.invert_xaxis()
        if inverty : self.ax.invert_yaxis()

        # Labels
        self.ax.set_title(self.box_title.text())
        self.ax.set_xlabel(self.box_xlabel.text())
        self.ax.set_ylabel(self.box_ylabel.text())

        self.canvas.draw()

class Crosshair() :
    """ Crosshair made up of two InfiniteLines. """
    def __init__(self, pos=(0,0)) :
        # Store the positions in TracedVariables
        self.hpos = TracedVariable(pos[1], name='hpos')
        self.vpos = TracedVariable(pos[0], name='vpos')

        # Initialize the InfiniteLines
        self.hline = pg.InfiniteLine(pos[1], movable=True, angle=0)
        self.vline = pg.InfiniteLine(pos[0], movable=True, angle=90)

        # Set the color
        self.set_color(BASE_LINECOLOR, HOVER_COLOR)

        # Register some callbacks
        self.hpos.sig_value_changed.connect(self.update_position_h)
        self.vpos.sig_value_changed.connect(self.update_position_v)

        self.hline.sigDragged.connect(self.on_dragged_h)
        self.vline.sigDragged.connect(self.on_dragged_v)

    def add_to(self, widget) :
        """ Add this crosshair to a Qt widget. """
        for line in [self.hline, self.vline] :
            line.setZValue(1)
            widget.addItem(line)

    def remove_from(self, widget) :
        """ Remove this crosshair from a pyqtgraph widget. """
        for line in [self.hline, self.vline] :
            widget.removeItem(line)

    def set_color(self, linecolor=BASE_LINECOLOR, hover_color=HOVER_COLOR) :
        """ Set the color and hover color of both InfiniteLines that make up 
        the crosshair. The arguments can be any pyqtgraph compatible color 
        specifiers.
        """
        for line in [self.hline, self.vline] :
            line.setPen(linecolor)
            line.setHoverPen(hover_color)

    def set_movable(self, movable=True) :
        """ Set whether or not this crosshair can be dragged by the mouse. """
        for line in [self.hline, self.vline] :
            line.setMovable = movable

    def move_to(self, pos) :
        """
        **Parameters**

        ===  ===================================================================
        pos  2-tuple; x and y coordinates of the desired location of the 
             crosshair in data coordinates.
        ===  ===================================================================
        """
        self.hpos.set_value(pos[1])
        self.vpos.set_value(pos[0])

    def update_position_h(self) :
        """ Callback for the :signal:`sig_value_changed 
        <data_slicer.utilities.TracedVariable.sig_value_changed>`. Whenever the 
        value of this TracedVariable is updated (possibly from outside this 
        Crosshair object), put the crosshair to the appropriate position.
        """
        self.hline.setValue(self.hpos.get_value())

    def update_position_v(self) :
        """ Confer update_position_h. """
        self.vline.setValue(self.vpos.get_value())

    def on_dragged_h(self) :
        """ Callback for dragging of InfiniteLines. Their visual position 
        should be reflected in the TracedVariables self.hpos and self.vpos.
        """
        self.hpos.set_value(self.hline.value())

    def on_dragged_v(self) :
        """ Callback for dragging of InfiniteLines. Their visual position 
        should be reflected in the TracedVariables self.hpos and self.vpos.
        """
        self.vpos.set_value(self.vline.value())

    def set_bounds(self, xmin, xmax, ymin, ymax) :
        """ Set the area in which the infinitelines can be dragged. """
        self.hline.setBounds([ymin, ymax])
        self.vline.setBounds([xmin, xmax])

class ImagePlot(pg.PlotWidget) :
    """
    A PlotWidget which mostly contains a single 2D image (intensity 
    distribution) or a 3D array (distribution of RGB values) as well as all 
    the nice pyqtgraph axes panning/rescaling/zooming functionality.

    In addition, this allows one to use custom axes scales as opposed to 
    being limited to pixel coordinates.

    **Signals**

    =================  =========================================================
    sig_image_changed  emitted whenever the image is updated
    sig_axes_changed   emitted when the axes are updated
    sig_clicked        emitted when user clicks inside the imageplot
    =================  =========================================================
    """
    sig_image_changed = qt.QtCore.Signal()
    sig_axes_changed = qt.QtCore.Signal()
    sig_clicked = qt.QtCore.Signal(object)

    def __init__(self, image=None, parent=None, background='default', 
                 name=None, **kwargs) :
        """ Allows setting of the image upon initialization. 
        
        **Parameters**

        ==========  ============================================================
        image       np.ndarray or pyqtgraph.ImageItem instance; the image to be
                    displayed.
        parent      QtWidget instance; parent widget of this widget.
        background  str; confer PyQt documentation
        name        str; allows giving a name for debug purposes
        ==========  ============================================================
        """
        # Initialize instance variables
        # np.array, raw image data
        self.image_data = None
        # pg.ImageItem of *image_data*
        self.image_item = None
        self.image_kwargs = {}
        self.xlim = None
        self.ylim = None
        self.xscale = None
        self.yscale = None
        self.transform_factors = []
        self.transposed = TracedVariable(False, name='transposed')
        self.crosshair_cursor_visible = False

        super().__init__(parent=parent, background=background, 
                         viewBox=DSViewBox(imageplot=self), **kwargs) 

        self.name = name

        # Show top and tight axes by default, but without ticklabels
        self.showAxis('top')
        self.showAxis('right')
        self.getAxis('top').setStyle(showValues=False)
        self.getAxis('right').setStyle(showValues=False)

        if image is not None :
            self.set_image(image)

        self.sig_axes_changed.connect(self.fix_viewrange)

    def show_cursor(self, show=True) :
        """
        Toggle whether or not to show a crosshair cursor that tracks the mouse movement.
        """
        if show :
            crosshair_cursor = Crosshair()
            crosshair_cursor.set_movable(False)
            crosshair_cursor.set_color((255, 255, 255, 255), 
                                       (255, 255, 255, 255))
            crosshair_cursor.add_to(self)
            self.scene().sigMouseMoved.connect(self.on_mouse_move)
            self.crosshair_cursor = crosshair_cursor
        else :
            try :
                self.scene().sigMouseMoved.disconnect(self.on_mouse_move)
            except TypeError :
                pass
            try :
                self.crosshair_cursor.remove_from(self)
            except AttributeError :
                pass
        self.crosshair_cursor_visible = show
        self.plotItem.vb.menu.toggle_cursor.setChecked(show)

    def toggle_cursor(self) :
        """ Change the visibility of the crosshair cursor. """
        self.show_cursor(not self.crosshair_cursor_visible)

    def on_mouse_move(self, pos) :
        """ Slot for mouse movement over the plot. Calculate the mouse 
        position in data coordinates and move the crosshair_cursor there.

        **Parameters**

        ===  ===================================================================
        pos  QPointF object; x and y position of the mouse as returned by 
             :signal:`sigMouseMoved 
             <data_slicer.imageplot.ImagePlot.sigMouseMoved>`.
        ===  ===================================================================
        """
        if self.plotItem.sceneBoundingRect().contains(pos) :
            data_point = self.plotItem.vb.mapSceneToView(pos)
            self.crosshair_cursor.move_to((data_point.x(), data_point.y()))

    def mousePressEvent(self, event) :
        """ Figure out where the click happened in data coordinates and make 
        the position available through the signal :signal:`sig_clicked 
        <data_slicer.imageplot.ImagePlot.sig_clicked>`.
        """
        if event.button() == qt.QtCore.Qt.LeftButton :
            vb = self.plotItem.vb
            last_click = vb.mapToView(vb.mapFromScene(event.localPos()))
            message = 'Last click at ( {:.4f} | {:.4f} )'
            self.sig_clicked.emit(message.format(last_click.x(), last_click.y()))
        super().mousePressEvent(event)

    def remove_image(self) :
        """ Removes the current image using the parent's :meth:`removeItem 
        pyqtgraph.PlotWidget.removeItem` function. 
        """
        if self.image_item is not None :
            self.removeItem(self.image_item)
        self.image_item = None

    def set_image(self, image, emit=True, *args, **kwargs) :
        """ Expects either np.arrays or pg.ImageItems as input and sets them 
        correctly to this PlotWidget's Image with `addItem`. Also makes sure 
        there is only one Image by deleting the previous image.

        Emits :signal:`sig_image_changed`

        **Parameters**

        ========  ==============================================================
        image     np.ndarray or pyqtgraph.ImageItem instance; the image to be
                  displayed.
        emit      bool; whether or not to emit :signal:`sig_image_changed`
        (kw)args  positional and keyword arguments that are passed on to 
                  :class:`pyqtgraph.ImageItem`
        ========  ==============================================================
        """
        # Convert array to ImageItem
        if isinstance(image, ndarray) :
            if 0 not in image.shape :
                image_item = ImageItem(image, *args, **kwargs)
            else :
                logger.debug(('<{}>.set_image(): image.shape is {}. Not '
                              'setting image.').format(self.name, image.shape))
                return
        else :
            image_item = image
        # Throw an exception if image is not an ImageItem
        if not isinstance(image_item, ImageItem) :
            message = '''`image` should be a np.array or pg.ImageItem instance,
            not {}'''.format(type(image))
            raise TypeError(message)

        # Transpose if necessary
        if self.transposed.get_value() :
            image_item = ImageItem(image_item.image.T, *args, **kwargs)

        # Replace the image
        self.remove_image()
        self.image_item = image_item
        self.image_data = image_item.image
        logger.debug('<{}>Setting image.'.format(self.name))
        self.addItem(image_item)
        # Reset limits if necessary
        if self.xscale is not None and self.yscale is not None :
            axes_shape = (len(self.xscale), len(self.yscale))
            if axes_shape != self.image_data.shape :
                self.xlim = None
                self.ylim = None
        self._set_axes_scales(emit=emit)

        if emit :
            logger.info('<{}>Emitting sig_image_changed.'.format(self.name))
            self.sig_image_changed.emit()

    def set_xscale(self, xscale, update=False) :
        """ Set the xscale of the plot. *xscale* is an array of the length 
        ``len(self.image_item.shape[0])``.
        """
        if self.transposed.get_value() :
            self._set_yscale(xscale, update)
        else :
            self._set_xscale(xscale, update)

    def set_yscale(self, yscale, update=False) :
        """ Set the yscale of the plot. *yscale* is an array of the length 
        ``len(self.image_item.image.shape[1])``.
        """
        if self.transposed.get_value() :
            self._set_xscale(yscale, update)
        else :
            self._set_yscale(yscale, update)

    def _set_xscale(self, xscale, update=False, force=False) :
        """ Set the scale of the horizontal axis of the plot. *force* can be 
        used to bypass the length checking.
        """
        # Sanity check
        if not force and self.image_item is not None and \
        len(xscale) != self.image_item.image.shape[0] :
            raise TypeError('Shape of xscale does not match data dimensions.')

        self.xscale = xscale
        # 'Autoscale' the image to the xscale
        self.xlim = (xscale[0], xscale[-1])

        if update :
            self._set_axes_scales(emit=True)

    def _set_yscale(self, yscale, update=False, force=False) :
        """ Set the scale of the vertical axis of the plot. *force* can be 
        used to bypass the length checking.
        """
        # Sanity check
        if not force and self.image_item is not None and \
        len(yscale) != self.image_item.image.shape[1] :
            raise TypeError('Shape of yscale does not match data dimensions.')

        self.yscale = yscale
        # 'Autoscale' the image to the xscale
        self.ylim = (yscale[0], yscale[-1])

        if update :
            self._set_axes_scales(emit=True)

    def transpose(self) :
        """ Transpose the image, i.e. swap the x- and y-axes. """
        self.transposed.set_value(not self.transposed.get_value())
        # Swap the scales
        new_xscale = self.yscale
        new_yscale = self.xscale
        self._set_xscale(new_xscale, force=True)
        self._set_yscale(new_yscale, force=True)
        # Update the image
        if not self.transposed.get_value() :
            # Take care of the back-transposition here
            self.set_image(self.image_item.image.T, lut=self.image_item.lut)
        else :
            self.set_image(self.image_item, lut=self.image_item.lut)

    def set_xlabel(self, label) :
        """ Shorthand for setting this plot's x axis label. """
        axis = self.getAxis('bottom')
        axis.setLabel(label)

    def set_ylabel(self, label) :
        """ Shorthand for setting this plot's y axis label. """
        axis = self.getAxis('left')
        axis.setLabel(label)

    def _set_axes_scales(self, emit=False) :
        """ Transform the image such that it matches the desired x and y 
        scales.
        """
        # Get image dimensions and requested origin (x0,y0) and top right 
        # corner (x1, y1)
        nx, ny = self.image_item.image.shape
        logger.debug(('<{}>_set_axes_scales(): self.image_item.image.shape={}' + 
                     ' x {}').format(self.name, nx, ny))
        [[x0, x1], [y0, y1]] = self.get_limits()
        # Calculate the scaling factors
        sx = (x1-x0)/nx
        sy = (y1-y0)/ny
        # Ensure nonzero
        sx = 1 if sx==0 else sx
        sy = 1 if sy==0 else sy
        # Define a transformation matrix that scales and translates the image 
        # such that it appears at the coordinates that match our x and y axes.
        transform = qt.QtGui.QTransform()
        transform.scale(sx, sy)
        # Carry out the translation in scaled coordinates
        transform.translate(x0/sx, y0/sy)
        # Finally, apply the transformation to the imageItem
        self.image_item.setTransform(transform)
        self._update_transform_factors()

        if emit :
            logger.info('<{}>Emitting sig_axes_changed.'.format(self.name))
            self.sig_axes_changed.emit()

    def get_limits(self) :
        """ Return ``[[x_min, x_max], [y_min, y_max]]``. """
        # Default to current viewrange but try to get more accurate values if 
        # possible
        if self.image_item is not None :
            x, y = self.image_item.image.shape
        else :
            x, y = 1, 1

        # Set the limits to image pixels if they are not defined
        if self.xlim is None :
            self.set_xscale(arange(0, x))
        x_min, x_max = self.xlim
        if self.ylim is None :
            self.set_yscale(arange(0, y))
        y_min, y_max = self.ylim

        logger.debug(('<{}>get_limits(): [[x_min, x_max], [y_min, y_max]] = '
                    + '[[{}, {}], [{}, {}]]').format(self.name, x_min, x_max, 
                                                     y_min, y_max))
        return [[x_min, x_max], [y_min, y_max]]

    def fix_viewrange(self) :
        """ Prevent zooming out by fixing the limits of the ViewBox. """
        logger.debug('<{}>fix_viewrange().'.format(self.name))
        [[x_min, x_max], [y_min, y_max]] = self.get_limits()
        self.setLimits(xMin=x_min, xMax=x_max, yMin=y_min, yMax=y_max,
                      maxXRange=x_max-x_min, maxYRange=y_max-y_min)

    def release_viewrange(self) :
        """ Undo the effects of :meth:`fix_viewrange 
        <data_slicer.imageplot.ImagePlot.fix_viewrange>`
        """
        logger.debug('<{}>release_viewrange().'.format(self.name))
        self.setLimits(xMin=-inf,
                       xMax=inf,
                       yMin=-inf,
                       yMax=inf,
                       maxXRange=inf,
                       maxYRange=inf)

    def _update_transform_factors(self) :
        """ Create a copy of the parameters that are necessary to reproduce 
        the current transform. This is necessary e.g. for the calculation of 
        the transform in :meth:`rotate 
        <data_slicer.imageplot.ImagePlot.rotate>`.
        """
        transform = self.image_item.transform()
        dx = transform.dx()
        dy = transform.dy()
        sx = transform.m11()
        sy = transform.m22()
        wx = self.image_item.width()
        wy = self.image_item.height()
        self.transform_factors = [dx, dy, sx, sy, wx, wy]

    def rotate(self, alpha=0) :
        """ Rotate the image_item by the given angle *alpha* (in degrees).  """
        # Get the details of the current transformation
        if self.transform_factors == [] :
            self._update_transform_factors()
        dx, dy, sx, sy, wx, wy = self.transform_factors

        # Build the transformation anew, adding a rotation
        # Remember that the order in which transformations are applied is 
        # reverted to how they are added in the code, i.e. last transform 
        # added in the code will come first (this is the reason we have to 
        # completely rebuild the transformation instead of just adding a 
        # rotation...)
        transform = self.image_item.transform()
        transform.reset()
        transform.translate(dx, dy)
        transform.translate(wx/2*sx, wy/2*sy)
        transform.rotate(alpha)
        transform.scale(sx, sy)
        transform.translate(-wx/2, -wy/2)

        self.release_viewrange()

        self.image_item.setTransform(transform)

    def mpl_export(self, *args, figsize=(5,5), title='', xlabel='', 
                   ylabel='', dpi=300) :
        """ Export the content of this plot to a png image using matplotlib. 
        The resulting image will have a white background and black ticklabes 
        and should therefore be more readable than pyqtgraph's native plot
        export options.

        **Parameters**

        =======  ===============================================================
        figsize  tuple of float; (height, width) of figure in inches
        title    str; figure title
        xlabel   str; x axis label
        ylabel   str; y axis label
        dpi      int; png resolution in pixels per inch
        args     positional arguments are absorbed and discarded (necessary 
                 to connect this method to signal handling)
        =======  ===============================================================
        """
        logger.debug('<ImagePlot.mpl_export()>')

        # Show the dialog with some options
        dialog = MPLExportDialog(self, parent=self)
#        ok_button = qt.QtGui.QPushButton('Done', dialog)
        if not dialog.exec_() : return
        # Replot to update the figure
        dialog.plot_preview()

        # Get a filename first
        fd = qt.QtGui.QFileDialog()
        filename = fd.getSaveFileName()[0]
        if not filename : return
        logger.debug('Outfilename: {}'.format(filename))

        # Update figure size before saving
        width, height = [float(box.text()) for box in [dialog.box_width, 
                                                       dialog.box_height]]
        dialog.figure.set_figwidth(width)
        dialog.figure.set_figheight(height)

        dialog.figure.savefig(filename, dpi=dpi)

    def lineplot(self, ax, dim=0, n=10, offset=0.2, lw=0.5, color='k', 
                 label_fmt='{:.2f}', n_ticks=5, **getlines_kwargs) :
        """
        Create a matplotlib plot with *n* lines extracted out of one of the 
        visible plots. The lines are normalized to their global maximum and 
        shifted from each other by *offset*.
        See :func:`get_lines <data_slicer.utilities.get_lines>` for more 
        options on the extraction of the lines.

        **Parameters**

        ===============  =======================================================
        plot             str; either "main" or "cut", specifies from which 
                         plot to extract the lines.
        dim              int; either 0 or 1, specifies in which direction to 
                         take the lines.
        ax               matplotlib.axes.Axes; the axes in which to plot.
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
        """
        data = self.image_data

        # Get the right axes
        axes = [self.xscale, self.yscale]
        for i,scale in enumerate(axes) :
            # Deal with *None*
            if scale is None :
                axes[i] = np.arange(data.shape[i])
        if dim==0 :
            data = data.T
        elif dim==1 :
            axes = axes[::-1]
        else :
            raise ValueError('*dim* should be one of (0, 1).')

        # Get the lines with an utility function
        lines, indices = get_lines(data, n, offset=offset, **getlines_kwargs) 

        # Plot the lines
        line2ds = []
        for line in lines :
            line2d = ax.plot(line, axes[0], lw=lw, color=color)[0]
            line2ds.append(line2d)

        # Create tick positions and labels
        xticks = [i*offset for i in range(n)]
        xtickvalues = axes[i][indices]
        xticklabels = [label_fmt.format(x) for x in xtickvalues]

        # Only render *n_ticks* ticks
        nth = int(n/n_ticks)
        ax.set_xticks(xticks[::nth])
        ax.set_xticklabels(xticklabels[::nth])

        return line2ds, xticks, xtickvalues, xticklabels

class CrosshairImagePlot(ImagePlot) :
    """ An imageplot with a draggable crosshair. """
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs) 

        # Hide the pyqtgraph auto-rescale button
        self.getPlotItem().buttonsHidden = True

        # Initiliaze a crosshair and add it to this widget
        self.crosshair = Crosshair()
        self.crosshair.add_to(self)

        self.pos = (self.crosshair.vpos, self.crosshair.hpos)

        # Initialize range to [0, 1]x[0, 1]
        self.set_bounds(0, 1, 0, 1)

        # Disable mouse scrolling, panning and zooming for both axes
#        self.setMouseEnabled(False, False)

        # Connect a slot (callback) to dragging and clicking events
        self.sig_axes_changed.connect(
            lambda : self.set_bounds(*[x for lst in self.get_limits() for x 
                                       in lst])) 

        self.sig_image_changed.connect(self.update_allowed_values)

    def update_allowed_values(self) :
        """ Update the allowed values silently. 
        This assumes that the displayed image is in pixel coordinates and 
        sets the allowed values to the available pixels.
        """
        logger.debug('{}.update_allowed_values()'.format(self.name))
        [[xmin, xmax], [ymin, ymax]] = self.get_limits()
        self.pos[0].set_allowed_values(arange(xmin, xmax+1, 1))
        self.pos[1].set_allowed_values(arange(ymin, ymax+1, 1))

    def set_bounds(self, xmin, xmax, ymin, ymax) :
        """ Set both, the displayed area of the axis as well as the the range 
        in which the crosshair can be dragged to the intervals [xmin, xmax] 
        and [ymin, ymax]. 
        """
        logger.debug('{}.set_bounds()'.format(self.name))
        self.setXRange(xmin, xmax, padding=0.01)
        self.setYRange(ymin, ymax, padding=0.01)

        self.crosshair.set_bounds(xmin, xmax, ymin, ymax)

        # Put the crosshair in the center
        self.pos[0].set_value(0.5*(xmax+xmin))
        self.pos[1].set_value(0.5*(ymax+ymin))

class CursorPlot(pg.PlotWidget) :
    """ Implements a simple, draggable scalebar represented by a line 
    (:class:`pyqtgraph.InfiniteLine) on an axis 
    (:class:`pyqtgraph.PlotWidget).
    The current position of the slider is tracked with the 
    :class:`TracedVariable <data_slicer.utilities.TracedVariable>` self.pos 
    and its width with the `TracedVariable` self.slider_width.
    """
    hover_color = HOVER_COLOR

    def __init__(self, parent=None, background='default', name=None, 
                 orientation='vertical', slider_width=1, **kwargs) : 
        """ Initialize the slider and set up the visual tweaks to make a 
        PlotWidget look more like a scalebar.

        **Parameters**

        ===========  ============================================================
        parent       QtWidget instance; parent widget of this widget
        background   str; confer PyQt documentation
        name         str; allows giving a name for debug purposes
        orientation  str, `horizontal` or `vertical`; orientation of the cursor
        ===========  ============================================================
        """
        super().__init__(parent=parent, background=background, **kwargs) 

        # Whether to allow changing the slider width with arrow keys
        self.change_width_enabled = False

        if orientation not in ['horizontal', 'vertical'] :
            raise ValueError('Only `horizontal` or `vertical` are allowed for '
                             'orientation.')
        self.orientation = orientation
        self.orientate()

        if name is not None :
            self.name = name
        else :
            self.name = 'Unnamed'

        # Hide the pyqtgraph auto-rescale button
        self.getPlotItem().buttonsHidden = True

        # Display the right (or top) axis without ticklabels
        self.showAxis(self.right_axis)
        self.getAxis(self.right_axis).setStyle(showValues=False)

        # The position of the slider is stored with a TracedVariable
        initial_pos = 0
        pos = TracedVariable(initial_pos, name='pos')
        self.register_traced_variable(pos)

        # Set up the slider
        self.slider_width = TracedVariable(slider_width, 
                                           name='{}.slider_width'.format( 
                                           self.name))
        self.slider = pg.InfiniteLine(initial_pos, movable=True, angle=self.angle)
        self.set_slider_pen(color=(255,255,0,255), width=slider_width)

        # Add a marker. Args are (style, position (from 0-1), size #NOTE 
        # seems broken
        #self.slider.addMarker('o', 0.5, 10)
        self.addItem(self.slider)

        # Disable mouse scrolling, panning and zooming for both axes
        self.setMouseEnabled(False, False)

        # Initialize range to [0, 1]
        self.set_bounds(initial_pos, initial_pos + 1)

        # Connect a slot (callback) to dragging and clicking events
        self.slider.sigDragged.connect(self.on_position_change)
        # sigMouseReleased seems to not work (maybe because sigDragged is used)
        #self.sigMouseReleased.connect(self.onClick)
        # The inherited mouseReleaseEvent is probably used for sigDragged 
        # already. Anyhow, overwriting it here leads to inconsistent behaviour.
        #self.mouseReleaseEvent = self.onClick

    def get_data(self) :
        """ Get the currently displayed data as a tuple of arrays, one 
        containing the x values and the other the y values.

        **Returns**

        =  =====================================================================
        x  array containing the x values.
        y  array containing the y values.
        =  =====================================================================
        """
        pdi = self.listDataItems()[0]
        return pdi.getData()

    def orientate(self) :
        """ Define all aspects that are dependent on the orientation. """
        if self.orientation == 'vertical' :
            self.right_axis = 'right'
            self.secondary_axis = 'top'
            self.secondary_axis_grid = (1,1)
            self.angle = 90
            self.slider_axis_index = 0
        else :
            self.right_axis = 'top'
            self.secondary_axis = 'right'
            self.secondary_axis_grid = (2,2)
            self.angle = 0
            self.slider_axis_index = 1

    def register_traced_variable(self, traced_variable) :
        """ Set self.pos to the given TracedVariable instance and connect the 
        relevant slots to the signals. This can be used to share a 
        TracedVariable among widgets.
        """
        self.pos = traced_variable
        self.pos.sig_value_changed.connect(self.set_position)
        self.pos.sig_allowed_values_changed.connect(self.on_allowed_values_change)

    def on_position_change(self) :
        """ Callback for the :signal:`sigDragged 
        <pyqtgraph.InfiniteLine.sigDragged>`. Set the value of the 
        TracedVariable instance self.pos to the current slider position. 
        """
        current_pos = self.slider.value()
        # NOTE pos.set_value emits signal sig_value_changed which may lead to 
        # duplicate processing of the position change.
        self.pos.set_value(current_pos)

    def on_allowed_values_change(self) :
        """ Callback for the :signal:`sig_allowed_values_changed
        <data_slicer.utilities.TracedVariable.sig_allowed_values_changed>`. 
        With a change of the allowed values in the TracedVariable, we should 
        update our bounds accordingly.
        The number of allowed values can also give us a hint for a reasonable 
        maximal width for the slider.
        """
        # If the allowed values were reset, just exit
        if self.pos.allowed_values is None : return

        lower = self.pos.min_allowed
        upper = self.pos.max_allowed
        self.set_bounds(lower, upper)

        # Define a max width of the slider and the resulting set of allowed 
        # widths
        max_width = int(len(self.pos.allowed_values)/2)
        allowed_widths = [2*i + 1 for i in range(max_width+1)]
        self.slider_width.set_allowed_values(allowed_widths)

    def set_position(self) :
        """ Callback for the :signal:`sig_value_changed 
        <data_slicer.utilities.TracedVariable.sig_value_changed>`. Whenever the 
        value of this TracedVariable is updated (possibly from outside this 
        Scalebar object), put the slider to the appropriate position.
        """
        new_pos = self.pos.get_value()
        self.slider.setValue(new_pos)

    def set_bounds(self, lower, upper) :
        """ Set both, the displayed area of the axis as well as the the range 
        in which the slider (InfiniteLine) can be dragged to the interval 
        [lower, upper].
        """
        if self.orientation == 'vertical' :
            self.setXRange(lower, upper, padding=0.01)
        else :
            self.setYRange(lower, upper, padding=0.01)
        self.slider.setBounds([lower, upper])

        # When the bounds update, the mousewheelspeed should change accordingly
        # TODO This should be in a slot to self.pos.sig_value_changed now
        self.wheel_frames = 1 
        # Ensure wheel_frames is at least as big as a step in the allowed 
        # values. NOTE This assumes allowed_values to be evenly spaced.
        av = self.pos.allowed_values
        if av is not None and self.wheel_frames <= 1 and len(av) > 1 :
            self.wheel_frames = av[1] - av[0]
    
    def set_secondary_axis(self, min_val, max_val) :
        """ Create (or replace) a second x-axis on the top which ranges from 
        `min_val` to `max_val`.
        This is the right axis in case of the horizontal orientation.
        """
        # Get a handle on the underlying plotItem
        plotItem = self.plotItem

        # Remove the old top-axis
        plotItem.layout.removeItem(plotItem.getAxis(self.secondary_axis))
        # Create the new axis and set its range
        new_axis = pg.AxisItem(orientation=self.secondary_axis)
        new_axis.setRange(min_val, max_val)
        # Attach it internally to the plotItem and its layout (The arguments 
        # `*(1, 1)` or `*(2, 2)` refers to the axis' position in the GridLayout)
        plotItem.axes[self.secondary_axis]['item'] = new_axis
        plotItem.layout.addItem(new_axis, *self.secondary_axis_grid)

    def set_slider_pen(self, color=None, width=None, hover_color=None) :
        """ Define the color and thickness of the slider (InfiniteLine 
        object :class:`pyqtgraph.InfiniteLine`) and store these attribute 
        in `self.slider_width` and `self.cursor_color`).
        """
        # Default to the current values if none are given
        if color is None :
            color = self.cursor_color
        else :
            self.cursor_color = color

        if width is None :
#            width = self.slider_width.get_value()
            width = self.pen_width
        else :
            self.pen_width = width

        if hover_color is None :
            hover_color = self.hover_color
        else :
            self.hover_color = hover_color

        self.slider.setPen(color=color, width=width)
        # Keep the hoverPen-size consistent
        self.slider.setHoverPen(color=hover_color, width=width)
            
    def increase_width(self, step=1) :
        """ Increase (or decrease) `self.slider_width` by `step` units of odd 
        numbers (such that the line always has a well defined center at the 
        value it is positioned at).
        """
        old_width = self.slider_width.get_value()
        new_width = old_width + 2*step
        if new_width < 0 :
            new_width = 1
        self.slider_width.set_value(new_width)

        # Convert width in steps to width in pixels
        dmin, dmax = self.viewRange()[self.slider_axis_index]
        pmax = self.rect().getRect()[self.slider_axis_index+2]
        pixel_per_step = pmax/(dmax-dmin)
        pen_width = new_width * pixel_per_step
        self.set_slider_pen(width=pen_width)

    def increase_pos(self, step=1) :
        """ Increase (or decrease) `self.pos` by a reasonable amount. 
        I.e. move `step` steps along the list of allowed values.
        """
        allowed_values = self.pos.allowed_values
        old_index = indexof(self.pos.get_value(), allowed_values)
        new_index = int((old_index + step)%len(allowed_values))
        new_value = allowed_values[int(new_index)]
        self.pos.set_value(new_value)

    def keyPressEvent(self, event) :
        """ Define responses to keyboard interactions. """
        key = event.key()
        logger.debug('{}.keyPressEvent(): key={}'.format(self.name, key))
        if key == qt.QtCore.Qt.Key_Right :
            self.increase_pos(1)
        elif key == qt.QtCore.Qt.Key_Left :
            self.increase_pos(-1)
        elif self.change_width_enabled and key == qt.QtCore.Qt.Key_Up :
            self.increase_width(1)
        elif self.change_width_enabled and key == qt.QtCore.Qt.Key_Down :
            self.increase_width(-1)
        else :
            event.ignore()
            return
        # If any if-statement matched, we accept the event
        event.accept()

    def wheelEvent(self, event) :
        """ Override of the Qt wheelEvent method. Fired on mousewheel 
        scrolling inside the widget. 
        """
        # Get the relevant coordinate of the mouseWheel scroll
        delta = event.angleDelta().y()
        logger.debug('<{}>wheelEvent(); delta = {}'.format(self.name, delta))
        if delta > 0 :
            sign = 1
        elif delta < 0 :
            sign = -1
        else :
            # It seems that in some cases delta==0
            sign = 0
        increment = sign*self.wheel_frames
        logger.debug('<{}>wheelEvent(); increment = {}'.format(self.name, 
                                                               increment))
        self.increase_pos(increment)

class Scalebar(CursorPlot) :
    """ Simple subclass of :class:`CursorPlot 
    <data_slicer.imageplot.CursorPlot>` that is intended to simulate a 
    scalebar. This is achieved by providing simply a long, flat plot without 
    any data and no y axis, but the same draggable slider as in CursorPlot.

    **Attributes**

    =========  =================================================================
    textItems  list of (t, (rx, ry)) tuples; t is a 
               :class:`pyqtgraph.TextItem` instance and rx, ry are floats in 
               the range [0, 1] indicating the relative positioning of the 
               textitems inside the Scalebar.
    =========  =================================================================
    """
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

        # Disable the context menu
        self.plotItem.vb.setMenuEnabled(False)

        self.disableAutoRange()

        # Aesthetics and other widget configs
        for axis in ['top', 'right', 'left', 'bottom'] :
            self.showAxis(axis)
            ax = self.getAxis(axis)
            #ax.setTicks([[], []])
            ax.setStyle(showValues=False, tickLength=0)

        self.set_size(300, 50)
        self.pos.set_allowed_values(linspace(0, 1, 100))

        # Connect signal of changed allowed values to update TextItem positions
        self.pos.sig_allowed_values_changed.connect(
            self.on_allowed_values_changed)

        # Slider appearance
        slider_width = 20
        self.slider.setPen(color=(100, 100, 100), width=slider_width)
        self.slider.setHoverPen(color=(120, 120, 120), width=slider_width)

        # Initialize other attributes 
        self.textItems = []

    def set_size(self, width, height) :
        """ Set this widgets size by setting minimum and maximum sizes 
        simultaneously to the same value. 
        """
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)

    def keyPressEvent(self, event) :
        """ Override some behaviour of the superclass. """
        key = event.key()
        if key in [qt.QtCore.Qt.Key_Up, qt.QtCore.Qt.Key_Down] :
            event.ignore()
        else :
            super().keyPressEvent(event)

    def add_text(self, text, relpos=(0.5, 0.5), anchor=(0.5, 0.5)) :
        """ 
        Add text to the scalebar.

        **Parameters**

        ======  ================================================================
        text    string; the text to be displayed.
        pos     tuple; (x, y) position of the text relative to the scalebar.
        anchor  tuple; (x, y) position of the text object's anchor.
        ======  ================================================================
        """
        t = pg.TextItem(text, anchor=anchor)
        self.set_relative_position(t, relpos)
        self.addItem(t)
        self.textItems.append((t, relpos))

    def set_relative_position(self, textItem, relpos) :
        """ 
        Figure out this Scalebar's current size (in data units) and 
        reposition its textItems accordingly.
        """
        height = 1
        width = len(self.pos.allowed_values)

        x = width * relpos[0]
        y = height * relpos[1]

        logger.debug(('set_relative_position [{}] - x={:.2f}, '
                     'y={:.2f}').format(self.name, x, y))

        textItem.setPos(x, y)

    def on_allowed_values_changed(self) :
        """ Keep TextItems in correct relative position. """
        for t, relpos in self.textItems :
            self.set_relative_position(t, relpos)

