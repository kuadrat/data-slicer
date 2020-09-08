
if __name__ == "__main__" :
    import pickle
    import pkg_resources

    from pyqtgraph.Qt import QtCore, QtGui
    import numpy as np
    import pyqtgraph as pg
    import pyqtgraph.opengl as gl

    from data_slicer.cmaps import cmaps

    #_Parameters________________________________________________________________

    DATA_PATH = pkg_resources.resource_filename('data_slicer', 'data/')
#    datafile = DATA_PATH + 'testdata_100_150_200.p'
    datafile = DATA_PATH + 'pit.p'

    ## Visual
    gloption = 'opaque'
    gloption = 'translucent'
    cmap = 'viridis'

    #_GUI_setup_________________________________________________________________

    # Initialize the application
    app = QtGui.QApplication([])

    # Set up the main window and set a central widget
    window = QtGui.QMainWindow()
    window.resize(800, 800)
    central_widget = QtGui.QWidget()
    window.setCentralWidget(central_widget)

    # Create a layout
    layout = QtGui.QGridLayout()
    central_widget.setLayout(layout)

    # Set up the main 3D view widget
    main = gl.GLViewWidget()
    layout.addWidget(main, 0, 0)


    window.show()

    #_Data_loading_and_presenting_______________________________________________

    # Load data
    with open(datafile, 'rb') as f :
        data = pickle.load(f)

    nx, ny, nz = data.shape
    print(nx, ny, nz)
    x0, y0, z0 = 0, 0, 0
    x0, y0, z0 = [int(2*n/5) for n in [nx, ny, nz]]

    # Create Textures
    levels = [data.min(), data.max()]
    cmap = cmaps[cmap]
    lut = cmap.getLookupTable()
    textures = [pg.makeRGBA(d, levels=levels, lut=lut)[0] for d in [data[x0], 
                                                                    data[:,y0], 
                                                                    data[:,:,z0]]]
    planes = [gl.GLImageItem(texture, glOptions=gloption) for texture in textures] 

    ## Apply transformations to get lanes where they need to go
    xscale, yscale, zscale = 1/nx, 1/ny, 1/nz
    # xy plane
    xy = planes[2]
    xy.scale(xscale, yscale, 1)
    xy.translate(-1/2, -1/2, -1/2 + z0*zscale)
    main.addItem(xy)

    # yz plane (appears in the coordinate system along xy)
    yz = planes[0]
    yz.scale(yscale, zscale, 1)
    yz.rotate(90, 0, 0, 1)
    yz.rotate(90, 0, 1, 0)
    yz.translate(-1/2 + x0*xscale, -1/2, -1/2)
    main.addItem(yz)

    # xz plane (appears in the coordinate system along xy)
    xz = planes[1]
    xz.scale(xscale, zscale, 1)
    xz.rotate(90, 1, 0, 0)
    xz.translate(-1/2, -1/2 + y0*yscale, -1/2)
    main.addItem(xz)

    #main.setCameraPosition

    # Draw a coordinate system
    #line_x = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [1, 0, 0]]), color=(1, 0, 0, 1))
    #line_y = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 1, 0]]), color=(0, 1, 0, 1))
    #line_z = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 0, 1]]), color=(0, 0, 1, 1))
    #main.addItem(line_x)
    #main.addItem(line_y)
    #main.addItem(line_z)
    axis = gl.GLAxisItem()
    main.addItem(axis)
    # Add a grid test grid
    #grid = gl.GLGridItem()
    #grid.scale(2, 2, 1)
    #main.addItem(grid)

    app.exec_()
    #if __name__ == '__main__':
    #    import sys
    #    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #        QtGui.QApplication.instance().exec_()

