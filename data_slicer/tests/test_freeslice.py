
import pickle
import pkg_resources

import pytestqt
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui

from data_slicer.cmaps import load_cmap
from data_slicer.imageplot import ImagePlot
from data_slicer.cutline import Cutline

def make_freeslice() :
    #_Parameters________________________________________________________________

    DATA_PATH = pkg_resources.resource_filename('data_slicer', 'data/')
    datafile = DATA_PATH + 'pit.p'

    ## Visual
    gloption = 'translucent'
    cmap = 'ocean'

    #_GUI_setup_________________________________________________________________

    # Set up the main window and set a central widget
    window = QtGui.QMainWindow()
    window.resize(800, 800)
    central_widget = QtGui.QWidget()
    window.setCentralWidget(central_widget)

    # Create a layout
    layout = QtGui.QGridLayout()
    central_widget.setLayout(layout)

    # Add the selector view
    selector = ImagePlot()
    #selector = gl.GLViewWidget()
    layout.addWidget(selector, 1, 0, 1, 1)

    # Set up the main 3D view widget
    main = gl.GLViewWidget()
    layout.addWidget(main, 0, 0, 1, 1)

    # Somehow this is needed for both widets to be visible
    layout.setRowStretch(0, 1)
    layout.setRowStretch(1, 1)

    #_Data_loading_and_presenting_______________________________________________

    # Load data
    with open(datafile, 'rb') as f :
        data = pickle.load(f)

    nx, ny, nz = data.shape
    x0, y0, z0 = 0, 0, 0
    x0, y0, z0 = [int(2*n/5) for n in [nx, ny, nz]]

    # Create Textures
    levels = [data.min(), data.max()]
    cmap = load_cmap(cmap)
    lut = cmap.getLookupTable()
    cuts = [data[x0], data[:,y0], data[:,:,z0]]
    textures = [pg.makeRGBA(d, levels=levels, lut=lut)[0] for d in cuts]
    planes = [gl.GLImageItem(texture, glOptions=gloption) for texture in textures] 

    ## Apply transformations to get lanes where they need to go
    xscale, yscale, zscale = 1/nx, 1/ny, 1/nz
    # xy plane
    xy = planes[2]
    xy.scale(xscale, yscale, 1)
    xy.translate(-1/2, -1/2, -1/2 + z0*zscale)
    main.addItem(xy)

    #_Selector__________________________________________________________________

    # Set an image in the selector plot
    selector.set_image(cuts[2], lut=lut)
    cutline = Cutline(selector)
    cutline.initialize()

    # A plane representing the cutline
    cut, coords = cutline.get_array_region(data, selector.image_item, 
                                           returnMappedCoords=True)
    cut_texture = pg.makeRGBA(cut, levels=levels, lut=lut)[0]
    cutplane = gl.GLImageItem(cut_texture, glOptions=gloption)

    # Scale and move it to origin in upright position
    # Upon initialization, this is like an xz plane
    cutplane.scale(xscale, zscale, 1)
    cutplane.rotate(90, 1, 0, 0)
    cutplane.translate(-1/2, 0, -1/2)
    transform0 = cutplane.transform()

    main.addItem(cutplane)

    # Conversion from ROI coordinates to Scene coordinates
    roi_coords = cutline.roi.getLocalHandlePositions()
    # also usefule for later
    original_roi_x0 = roi_coords[0][1].x()
    original_roi_x1 = roi_coords[1][1].x()
    # length in ROI coordinates
    length_in_roi = np.abs(original_roi_x1 - original_roi_x0)
    # length in data coordinates
    length_in_data = np.abs(coords[0,0] - coords[0,-1])
    # conversion in units of "roi/data"
    roi_data_conversion = length_in_roi/length_in_data
    # distance from left handle to M in data coords
    distance_p0_m = length_in_data/2
    print('Distance: ', distance_p0_m)

    def update_texture() :
        print('==')
        print('LocalHandles: ', cutline.roi.getLocalHandlePositions())
        print('Scene: ', cutline.roi.getSceneHandlePositions())
        print('++')
        transform = cutline.roi.getArraySlice(data, selector.image_item)[1]

        cut, coords = cutline.get_array_region(data, selector.image_item, 
                                               returnMappedCoords=True)
        texture = pg.makeRGBA(cut, levels=levels, lut=lut)[0]
        cutplane.setData(texture)

        ## Find the original center of mass (if no length changes would have been applied)
        # The current handle positions in data coordinates are in p0 and p1
        p0 = coords[[0, 1], [0, 0]]
        p1 = coords[[0, 1], [-1, -1]]
        # Find how much they have been stretched or compressed with respect to 
        # the original handles
        new_roi_coords = cutline.roi.getLocalHandlePositions()
        delta0 = (original_roi_x0 - new_roi_coords[0][1].x())/roi_data_conversion
        # Construct a unit vector pointing from P0 to P1
        diff = p1 - p0
        e_pp = diff / np.sqrt(diff.dot(diff))
        print('p0: ', p0)
        print('p1: ', p1)
        print('diff', diff)
        print('e_pp: ', e_pp)

        # Now the original midpoint is at p0 + e_pp*(distance_p0_m+delta0)
        print('delta0: ', delta0)
        M = p0
        tx, ty = M[0], M[1]
        print('tx, ty: {}, {}'.format(tx, ty))

        tx *= xscale
        ty *= yscale
        print('tx, ty: {}, {}'.format(tx, ty))

        # Rotate around origin
        try :
            alpha = np.arctan((p1[1]-p0[1]) / (p1[0]-p0[0]))
        except ZeroDivisionError :
            alpha = np.sign(p1[1]-p0[1]) * np.pi/2
        # Correct for special cases
        if p1[0] < p0[0] :
            alpha -= np.sign(p1[1]-p0[1]) * np.pi
        alpha_deg = alpha*180/np.pi
        print('alpha_deg: {}'.format(alpha_deg))

        nt = QtGui.QMatrix4x4()
        nt.translate(tx-1/2, ty-1/2, -1/2)
        nt.scale(xscale, yscale, 1)
        nt.rotate(alpha_deg, 0, 0, 1)
        nt.rotate(90, 1, 0, 0)
        nt.scale(1, zscale, 1)
        cutplane.setTransform(nt)

    cutline.sig_region_changed.connect(update_texture)

    # Draw a coordinate system
    axis = gl.GLAxisItem()
    main.addItem(axis)

    return window

def test_freeslice(qtbot) :
    """ Test creating the freeslice window. """
    window = make_freeslice()
    window.show()
    qtbot.add_widget(window)
    qtbot.wait(1000)

if __name__ == "__main__" :
    # Initialize the application
    app = QtGui.QApplication([])
    
    window = make_freeslice()
    window.show()

    app.exec_()
