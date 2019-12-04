"""
Simply start up PIT with its example data.
"""

from pyqtgraph.Qt import QtGui
from data_slicer.pit import MainWindow

app = QtGui.QApplication([])
mw = MainWindow()
app.exec_()

