"""
Simply start up PIT with its example data.
"""
from pyqtgraph.Qt import QtCore

from data_slicer.pit import MainWindow

def create_pit() :
    mw = MainWindow()
    return mw

def test_pit(qtbot) :
    mw = create_pit()
    qtbot.add_widget(mw)
    # Write something to the console
    # This likely does not work due to the interaction with the ipython kernel
#    qtbot.mouseClick(mw.console, QtCore.Qt.LeftButton)
#    qtbot.keyClicks(mw.console, 'mw.brain()')
#    qtbot.keyClick(mw.console, QtCore.Qt.Key_Enter)

    # Just try loading the brain data instead
    mw.brain()

    shape = mw.data_handler.get_data().shape
    # Original data has (196, 118, 56), brain has (256, 256, 124)
    assert shape == (256, 256, 124)

    # Test moving the slice line with the arrow keys
    wait_time = 500
    n_intervals = 5
    n_presses = 10
    for i in range(n_intervals) :
        qtbot.wait(wait_time)
        for j in range(n_presses) :
            qtbot.keyClick(mw.integrated_plot, QtCore.Qt.Key_Right)
    assert mw.integrated_plot.pos.get_value() == n_intervals*n_presses

    # Test increasing the integration width with arrow keys
    for i in range(n_intervals) :
        qtbot.wait(wait_time)
        qtbot.keyClick(mw.integrated_plot, QtCore.Qt.Key_Up)
    assert mw.integrated_plot.slider_width.get_value() == 2*n_intervals+1

if __name__ == "__main__" :
    from pyqtgraph.Qt import QtGui

    app = QtGui.QApplication([])
    mw = create_pit()
    app.exec_()

