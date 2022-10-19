import pickle
import pkg_resources

import numpy as np
import pytestqt
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

import data_slicer.set_up_logging
from data_slicer.widgets import ThreeDWidget

def create_threedwindow() :
    """ Create an example window that makes use of :class:`ThreeDWidget 
    <data_slicer.widgets.ThreeDWidget>` to display a slice plane through a 3D 
    data cube.

    For convenience with 
    :func:`~data_slicer.tests.test_threedwidget.test_threedwidget`, this 
    function returns the created QWindow, the ThreeDWidget as well as the two 
    QPushButtons.
    """
    window = QtWidgets.QMainWindow()
    window.resize(800, 800)

    # Add layouting-widget
    cw = QtWidgets.QWidget()
    window.setCentralWidget(cw)
    layout = QtWidgets.QGridLayout()
    cw.setLayout(layout)

    # Add our custom widgets
    w = ThreeDWidget()
    layout.addWidget(w, 0, 0, 1, 2)

    # Create and add buttons
    button1 = QtWidgets.QPushButton()
    button1.setText('Reset')
    layout.addWidget(button1, 1, 0, 1, 1)
    button2 = QtWidgets.QPushButton()
    button2.setText('Randomize')
    layout.addWidget(button2, 1, 1, 1, 1)

    # Load example data
    data_path = pkg_resources.resource_filename('data_slicer', 'data/')
    datafile = 'pit.p'
    with open(data_path + datafile, 'rb') as f :
        data = pickle.load(f)
    shape = data.shape
    w.set_data(data)

    # Define the button actions
    def reset_data() :
        w.set_data(data)
    button1.clicked.connect(reset_data)

    def randomize_data() :
        w.set_data(np.random.rand(*shape))
    button2.clicked.connect(randomize_data)

    return window, w, button1, button2

def test_threedwidget(qtbot) :
    """ Create a ThreeDWidget and use the arrow keys to move the slice plane 
    up and down.
    """
    # Create the widget
    window, widget, button1, button2 = create_threedwindow()
    window.show()
    qtbot.add_widget(window)
    wait_short = 50
    wait_long = 500
    qtbot.wait(wait_long)

    # Move the xy plane using the arrow keys
    n_clicks = 50
    for i in range(n_clicks) :
        qtbot.keyClick(widget.slider_xy, QtCore.Qt.Key_Right)
        qtbot.wait(wait_short)
    assert widget.slider_xy.pos.get_value() == n_clicks

    # Click the randomize button
    qtbot.mouseClick(button2, QtCore.Qt.LeftButton)
    qtbot.wait(wait_long)

    # Move back down
    for i in range(n_clicks) :
        qtbot.keyClick(widget.slider_xy, QtCore.Qt.Key_Left)
        qtbot.wait(wait_short)
    assert widget.slider_xy.pos.get_value() == 0

if __name__ == "__main__" :
    # Set up Qt Application skeleton
    app = QtGui.QApplication([])
    window, widget, button1, button2 = create_threedwindow()
    window.show()
    app.exec_()
