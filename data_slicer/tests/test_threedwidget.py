if __name__ == "__main__" :
    import pickle
    import pkg_resources

    import numpy as np
    from pyqtgraph.Qt import QtGui

    import data_slicer.set_up_logging
    from data_slicer.widgets import ThreeDWidget


    # Set up Qt Application skeleton
    app = QtGui.QApplication([])
    window = QtGui.QMainWindow()
    window.resize(800, 800)

    # Add layouting-widget
    cw = QtGui.QWidget()
    window.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    # Add our custom widgets
    w = ThreeDWidget()
    layout.addWidget(w, 0, 0, 1, 2)

    button1 = QtGui.QPushButton()
    button1.setText('Reset')
    layout.addWidget(button1, 1, 0, 1, 1)

    button2 = QtGui.QPushButton()
    button2.setText('Randomize')
    layout.addWidget(button2, 1, 1, 1, 1)

    # Necessary for both widgets to be visible
    #layout.setRowStretch(0, 2)
    #layout.setRowStretch(1, 2)

    # Load example data
    data_path = pkg_resources.resource_filename('data_slicer', 'data/')
#    datafile = 'testdata_100_150_200.p'
    datafile = 'pit.p'
    with open(data_path + datafile, 'rb') as f :
        data = pickle.load(f)
    w.set_data(data)

    # Button actions
    def reset_data() :
        w.set_data(data)
    button1.clicked.connect(reset_data)

    def randomize_data() :
        w.set_data(np.random.rand(100, 150, 200))
    button2.clicked.connect(randomize_data)

    # Run
    window.show()



    app.exec_()

