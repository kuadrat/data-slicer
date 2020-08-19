"""
Simply start up PIT with its example data.
"""

if __name__ == "__main__" :
    from pyqtgraph.Qt import QtGui
    from data_slicer.pit import MainWindow

    app = QtGui.QApplication([])
    mw = MainWindow()
    app.exec_()

