# Import libraries
from pyqtgraph.Qt import QtGui

from data_slicer import dataloading
from data_slicer.widgets import ThreeDSliceWidget

# Create a Qt Window and set its size
app = QtGui.QApplication([])
window = QtGui.QMainWindow()
window.resize(600, 500)

# Create a "dummy-widget" that just contains the layout
layout_widget = QtGui.QWidget()
window.setCentralWidget(layout_widget)
# Create the layout and link it to the central widget
layout = QtGui.QGridLayout()
layout_widget.setLayout(layout)

# Create a QPushButton
load_button = QtGui.QPushButton()
load_button.setText('Load')

# Create the ThreeDSliceWidget and add it to the window
widget = ThreeDSliceWidget()

# Add the widgets to the layout. The syntax for a QGridLayout is 
# addWidget(widget_to_add, row, column, rowspan, columnspan)
layout.addWidget(load_button, 0, 0, 1, 1)
layout.addWidget(widget, 1, 0, 1, 1)

# Define the function that is executed whenever the button is clicked
def load_data() :
    """ Open a Filedialog and use the file selected by the user to load some 
    data into the ThreeDSliceWidget.
    """
    # Open the file selection dialog and store the selected file as *fname*
    fname = QtGui.QFileDialog.getOpenFileName(layout_widget, 'Select file')
    print(fname[0])
    
    # Load the selected data into the ThreeDSliceWidget
    D = dataloading.load_data(fname[0])
    widget.set_data(D.data)

load_button.clicked.connect(load_data)

# Show the window and run the app
window.show()
app.exec_()

