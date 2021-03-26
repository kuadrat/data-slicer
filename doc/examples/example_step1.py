# Import libraries
from pyqtgraph.Qt import QtGui

from data_slicer.widgets import ThreeDSliceWidget

# Create a Qt Window and set its size
app = QtGui.QApplication([])
window = QtGui.QMainWindow()
window.resize(600, 500)

# Create the ThreeDSliceWidget and add it to the window
widget = ThreeDSliceWidget()
window.setCentralWidget(widget)

# Show the window and run the app
window.show()
app.exec_()
