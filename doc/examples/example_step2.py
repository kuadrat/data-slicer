# Import libraries
from pyqtgraph.Qt import QtGui

from data_slicer.widgets import ThreeDSliceWidget

# Create a Qt Window and set its size
app = QtGui.QApplication([])
window = QtGui.QMainWindow()
window.resize(600, 500)

# NEW: Create a "dummy-widget" that just contains the layout
layout_widget = QtGui.QWidget()
window.setCentralWidget(layout_widget)
# NEW: Create the layout and link it to the central widget
layout = QtGui.QGridLayout()
layout_widget.setLayout(layout)

# NEW: Create a QPushButton
load_button = QtGui.QPushButton()
load_button.setText('Load')

# Create the ThreeDSliceWidget and add it to the window
widget = ThreeDSliceWidget()
# NEW: This is no longer the central widget - thus the following line has to 
# be removed
#window.setCentralWidget(widget)

# NEW: Add the widgets to the layout. The syntax for a QGridLayout is 
# addWidget(widget_to_add, row, column, rowspan, columnspan)
layout.addWidget(load_button, 0, 0, 1, 1)
layout.addWidget(widget, 1, 0, 1, 1)

# Show the window and run the app
window.show()
app.exec_()

