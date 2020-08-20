
import logging

import pyqtgraph as pg
from pyqtgraph import Qt as qt
from pyqtgraph import QtGui, Point
from pyqtgraph.functions import affineSlice

logger = logging.getLogger('ds.'+__name__)

class CustomizableLineSegmentROI(pg.LineSegmentROI) :
    """ Subclass of :class:`LineSegmentROI 
    <pyqtgraph.LineSegmentROI>`. Implements a few features that were missing 
    from the parent class, namely customizable hover pen.
    """
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        # Set a default pen
        self.set_hover_pen(color=(255, 255, 0))

    def set_hover_pen(self, *args, **kwargs) :
        """ Set the pen used for drawing this widget when it is in the 
        `hovered` state. Accepts function arguments to :func: `mkPen 
        pyqtgraph.mkPen`
        """
        self.hover_pen = pg.mkPen(*args, **kwargs)

    def _makePen(self) :
        """ Overrided parent's :func: `_makePen 
        <pyqtgrapch.graphicsItems.ROI.makePen()>` function to allow custom 
        hover styles.
        """
        if self.mouseHovering :
            return self.hover_pen
        else :
            return self.pen

class CustomizableHandle(pg.graphicsItems.ROI.Handle) :
    """ Same concept as :class:`CustomizableLineSegmentROI 
    <data_slicer.cutline.CustomizableLineSegmentROI`>. Subclass to allow 
    customization of hover pen.

    .. Note::

       This class is unused because that would require setting these handles 
       as the handles for `CustomizableLineSegmentROI`. Too much work for a 
       relatively unimportant feature.
    """
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        # Set a default pen
        self.set_hover_pen(color=(255, 255, 0))

    def set_hover_pen(self, *args, **kwargs) :
        """ Set the pen used for drawing this widget when it is in the 
        *hovered* state. Accepts function arguments to :func:` 
        pyqtgraph.mkPen` 
        """
        self.hover_pen = pg.mkPen(*args, **kwargs)

    def hoverEvent(self, ev) :
        """ This just copies the code of the parent class with the difference 
        of a variable hover pen.
        """
        hover = False
        # Check if it is appropriate to change the state to `hover`
        if not ev.isExit() :
            if ev.acceptDrags(QtCore.Qt.LeftButton) :
                hover=True
            for btn in [QtCore.Qt.LeftButton, QtCore.Qt.RightButton, 
                        QtCore.Qt.MidButton] :
                if (int(self.acceptedMouseButtons() & btn) > 0 and 
                    ev.acceptClicks(btn)) : 
                    hover=True

        if hover :
            # This is the only changed line
            self.currentPen = self.hover_pen
        else :
            self.currentPen = self.pen
        self.update()

class Cutline(qt.QtCore.QObject) :
    """ Wrapper class allowing easy adding and removing of 
    :class:`pyqtgraph.LineSegmentROI` to a 
    :class:`pyqtgraph.PlotWidget`.
    It both
    has-a LineSegmentROI
    and
    has-a PlotWidget
    and handles interactions between the two.

    Needs to inherit from :class:`pyqtgraph.qt.QtCore.QObject` in order to 
    have signals.

    **Signals**

    ==================  ========================================================
    sig_region_changed  wraps the underlying :class:`LineSegmentROI 
                        <pyqtgraph.LineSegmentROI>`'s sigRegionChange. 
                        Emitted whenever the ROI is moved or changed.
    sig_initialized     emitted when a new :class:`LineSegmentROI 
                        <pyqtgraph.LineSegmentROI>` has been 
                        created and assigned as this :class:`Cutline 
                        <data_slicer.cutline.Cutline>`'s `roi`.
    ==================  ========================================================
    """
    sig_initialized = qt.QtCore.Signal()

    def __init__(self, plot_widget=None, orientation='horizontal', 
                 handles=(None, None), **kwargs) :
        super().__init__(**kwargs)


        if plot_widget :
            self.add_to_plot(plot_widget)
        self.orientation = orientation
        self.roi = None

        # Define default pens
        self.pen = pg.mkPen((255, 255, 0), width=3)
        self.hover_pen = pg.mkPen((255, 150, 10), width=3)

    def add_to_plot(self, plot_widget) :
        """ Add this cutline to a :class:`PlotWidget <pyqtgraph.PlotWidget>`.
        This is effectively implemented by setting this :class:`Cutline 
        <data_slicer.cutline.Cutline>`'s plot attribute to the given *plot_widget*.
        """
        self.plot = plot_widget
        # Signal connection: whenever the viewRange changes, the cutline should 
        # be updated. Make sure to not accumulate connections by trying to 
        # disconnect first.
        try :
            self.plot.sigRangeChanged.disconnect(self.initialize)
        except TypeError :
            pass
        self.plot.sig_axes_changed.connect(self.initialize)

    def initialize(self, orientation=None) :
        """ Emits :signal:`sig_initialized`. """
        logger.debug('initialize()')
        # Change the orientation if one is given
        if orientation :
            self.orientation = orientation

        # Remove the old LineSegmentROI if necessary
        self.plot.removeItem(self.roi)

        # Put a new LineSegmentROI in the center of the plot in the right 
        # orientation
        lower_left, upper_right = self.calculate_endpoints()
        self.roi = CustomizableLineSegmentROI(positions=[lower_left, upper_right], 
                                              pen='m')
        self.roi.setPen(self.pen)
        self.roi.set_hover_pen(self.hover_pen)
        # Set default handle style
        self.set_handle_style()
        self.plot.addItem(self.roi, ignoreBounds=True)

        # Reconnect signal handling
        # Wrap the LineSegmentROI's sigRegionChanged
        self.sig_region_changed = self.roi.sigRegionChanged

        logger.info('Emitting sig_initialized.')
        self.sig_initialized.emit()

    def set_handle_style(self, radius=8, color=(200, 255, 200), width=2) :
        """ Set the size and pen of the handles. """
        for h in self.roi.getHandles() :
            # Delete cached shapes
            h._shape = None
            h.radius = radius
            h.pen = pg.mkPen(color, width=width)

            # Need to redraw path
            h.buildPath()

    def recenter(self) :
        """ Put the ROI in the center of the current plot. """
        logger.info('Recentering ROI.')
        lower_left, upper_right = self.calculate_endpoints()

    def calculate_endpoints(self) :
        """ Get sensible initial values for the endpoints of the 
        :class:`LineSegmentROI <pyqtgraph.LineSegmentROI>` from the 
        :class:`pyqtrgaph.PlotWidget`'s current view range.  Depending on the 
        state of `self.orientation` these endpoints correspond either to a 
        vertical or horizontal line centered at the center of the plot and 
        spanning exactly the whole plot range.

        Returns a tuple of len(2) lists: (lower_left, top_right) 
        corresponding to the  two endpoints.
        """
        # Get the current range of the plot
        [[xmin, xmax], [ymin, ymax]] = self.plot.get_limits()
        x = 0.5*(xmax+xmin)
        y = 0.5*(ymax+ymin)

        # Set the start and endpoint depending on the orientation
        if self.orientation is 'horizontal' :
            lower_left = [xmin, y]
            upper_right = [xmax, y]
        elif self.orientation is 'vertical' :
            lower_left = [x, ymin]
            upper_right = [x, ymax]

        logger.debug('lower_left: {}, upper_right: {}'.format(lower_left, 
                                                              upper_right))
        return lower_left, upper_right

    def flip_orientation(self) :
        """ Change the cutline's orientation from vertical to horitontal or 
        vice-versa and re-initialize it in the new orientation.
        """
        # Find out which orientation we're currently in and change 
        # accordingly 
        orientations = ['horizontal', 'vertical']
        # `i` will be the index of the orientation we currently don't have
        i = (orientations.index(self.orientation) + 1) % 2
        self.orientation = orientations[i]
        logger.info('New orientation: {}'.format(self.orientation))
        self.initialize()

    def get_array_region(self, *args, **kwargs) :
        """ Wrapper for the underlying ROI's
        :meth:`~data_slicer.cutline.Cutline.roi.getArrayRegion`. 
        """
        return self.roi.getArrayRegion(*args, **kwargs)
 
