"""
Subclass of ViewBox with custom menu items.
"""
import logging

from pyqtgraph.Qt import QtGui
from pyqtgraph.graphicsItems.ViewBox import ViewBox, ViewBoxMenu

logger = logging.getLogger('ds.'+__name__)

class DSViewBoxMenu(ViewBoxMenu.ViewBoxMenu) :
    """ Subclass of ViewBoxMenu with custom menu items. """
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)

        self._remove_unwanted_actions()

        # Define own menu entries
        self.mpl_export = QtGui.QAction('MPL export', self)
        self.addAction(self.mpl_export)

        self.transpose = QtGui.QAction('Transpose', self)
        self.addAction(self.transpose)

        self.toggle_cursor = QtGui.QAction('Show cursor', self, checkable=True)
        self.addAction(self.toggle_cursor)

    def _remove_unwanted_actions(self) :
        # Remove unwanted menu entries
        unwanted_texts = ['View All',
                          'Mouse Mode',
                          'Plot Options',
                          'Export...']
        for action in self.actions() :
            if action.text() in unwanted_texts :
                self.removeAction(action)

class DSViewBox(ViewBox) :
    """
    Subclass of ViewBox with custom menu items, as defined in 
    :class:`~data_slicer.dsviewbox.DSViewBoxMenu`.
    """
    def __init__(self, imageplot, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        logger.debug(imageplot)
        self.imageplot = imageplot

        # Connect signal handling and make the menu entry appear
        self.menu = DSViewBoxMenu(self)

        self.menu.mpl_export.triggered.connect(self.imageplot.mpl_export)
        self.menu.transpose.triggered.connect(self.imageplot.transpose)
        self.menu.toggle_cursor.triggered.connect(self.imageplot.toggle_cursor)

