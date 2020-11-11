"""
Convert some of the nicer matplotlib and kustom colormaps to pyqtgraph 
colormaps.
"""
import copy
import os
import pathlib
import pickle
import pkg_resources
import warnings

import numpy as np
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.pyplot import colormaps
from pyqtgraph import ColorMap

from data_slicer.utilities import CACHED_CMAPS_FILENAME, CONFIG_DIR

class ds_cmap(ColorMap) :
    """ Simple subclass of :class:`pyqtgraph.ColorMap`. Adds vmax, 
    powerlaw normalization and a convenience function to change alpha.
    """
    def __init__(self, pos, color, gamma=1, **kwargs) :
        super().__init__(pos, color, **kwargs)

        # Initialize instance variables
        self.alpha = 0.5
        self.vmax = 1
        self.gamma = 1

        # Retain a copy of the originally given positions
        self.original_pos = self.pos.copy()
        # Apply the powerlaw-norm
        self.set_gamma(gamma)

    def apply_transformations(self) :
        """ Recalculate the positions where the colormapping is defined by 
        applying (in sequence) alpha, then a linear map to the range 
        [0, vmax] and finally the powerlaw scaling: ``pos' = pos**gamma``.
        """
        # Reset the cache in pyqtgraph.Colormap
        self.stopsCache = dict()

        # Apply alpha
        self.color[:,-1] = 255*self.alpha

        # Linearly transform color values to the new range
        old_max = self.original_pos.max()
        old_min = self.original_pos.min()
        new_max = old_max * self.vmax
        m = (new_max - old_min) / (old_max - old_min)
        self.pos = m * (self.original_pos - old_max) + new_max

        # Apply a powerlaw norm to the positions
        self.pos = self.pos**(1/self.gamma)

    def set_gamma(self, gamma=1) :
        """ Set the exponent for the power-law norm that maps the colors to 
        values. I.e. the values where the colours are defined are mapped like 
        ``y=x**gamma``.
        """
        self.gamma = gamma
        self.apply_transformations()

    def set_alpha(self, alpha) :
        """ Set the value of alpha for the whole colormap to *alpha* where 
        *alpha* can be a float or an array of length ``len(self.color)``.
        """
        self.alpha = alpha
        self.apply_transformations()

    def set_vmax(self, vmax=1) :
        """ Set the relative (to the maximum of the data) maximum of the 
        colorscale. 
        """
        self.vmax = vmax
        self.apply_transformations()

def convert_matplotlib_to_pyqtgraph(matplotlib_cmap, alpha=0.5) :
    """ Take a matplotlib colormap and convert it to a pyqtgraph ColorMap.

    **Parameters**

    ===============  ===========================================================
    matplotlib_cmap  either a str representing the name of a matplotlib 
                     colormap or a 
                     :class:`<matplotlib.colors.LinearSegmentedColormap>` or 
                     :class:`<matplotlib.colors.ListedColormap>` instance.
    alpha            float or array of same length as there are defined 
                     colors in the matplotlib cmap; the alpha (transparency) 
                     value to be assigned to the whole cmap. matplotlib cmaps 
                     default to 1.
    ===============  ===========================================================

    **Returns**

    ===============  ===========================================================
    pyqtgraph_cmap   :class:`pyqtgraph.ColorMap`
    ===============  ===========================================================
    """
    # Get the colormap object if a colormap name is given 
    if isinstance(matplotlib_cmap, str) :
        matplotlib_cmap = cm.get_cmap(matplotlib_cmap)
    # Number of entries in the matplotlib colormap
    N = matplotlib_cmap.N
    # Create the mapping values in the interval [0, 1]
    values = np.linspace(0, 1, N)
    # Extract RGBA values from the matplotlib cmap
    indices = np.arange(N)
    rgba = matplotlib_cmap(indices)
    # Apply alpha
    rgba[:,-1] = alpha
    # Convert to range 0-255
    rgba *= 255

    return ds_cmap(values, rgba)

def convert_ds_to_matplotlib(data_slicer_cmap, cmap_name='converted_cmap') :
    """ Create a matplotlib colormap from a :class:`ds_cmap 
    <data_slicer.cmaps.ds_cmap>` instance.

    **Parameters**

    ================  ==========================================================
    data_slicer_cmap  :class:`ds_cmap <data_slicer.cmaps.ds_cmap>`
    cmap_name         str; optional name for the created cmap.
    ================  ==========================================================

    **Returns**

    ===============  ===========================================================
    matplotlib_cmap  :class:`<matplotlib.colors.LinearSegmentedColormap>`
    ===============  ===========================================================
    """
    # Reset the transformations - matplotlib can take care of them itself
    data_slicer_cmap.set_gamma(1)
    data_slicer_cmap.set_vmax(1)
    # Convert the colors from the range [0-255] to [0-1]
    colors = data_slicer_cmap.color / 255
    N = len(colors)
    # Create the matplotlib colormap
    matplotlib_cmap = LinearSegmentedColormap.from_list(cmap_name,
                                                        colors, N)
    return matplotlib_cmap

def load_custom_cmap(filename) :
    """ Create a :class:`ds_cmap <data_slicer.cmaps.ds_cmap>` instance from 
    data stored in a file with three columns, red, green and blue - either in 
    integer form from 0-255 or as floats from 0.0 to 1.0 (ignores fourth 
    alpha column).
    """
    data = np.loadtxt(filename)[:,:3]
    data /= data.max() 
    # Convert to range [0-255] for pyqtgraph 0.0.11
    data *= 255
    N = len(data)
    # Append a column of 1's
    cmap = np.hstack([data, np.ones(N).reshape((N, 1))])
    pos = np.linspace(0, 1, N)
    return ds_cmap(pos, cmap)

# Load the cmaps dictionary
data_path = pkg_resources.resource_filename('data_slicer', 'data/')
try :
    with open(data_path + CACHED_CMAPS_FILENAME, 'rb') as f :
        cmaps = pickle.load(f)
except AttributeError :
    cmaps = dict()
#cmaps = dict()

# Add user supplied colormaps
def load_user_cmaps(cmaps) :
    """ Append user supplied colormaps to the dictionary *cmaps*. """
    config_path = pathlib.Path.home() / CONFIG_DIR / 'cmaps/'
    try :
        files = os.listdir(config_path)
    except FileNotFoundError :
        files = []

    for cmap in files :
        name, suffix = cmap.split('.')
        # Only load files with the .cmap suffix
        if suffix != 'cmap' :
            continue
        cmap_object = load_custom_cmap(config_path / cmap)
        cmaps.update({name: cmap_object})
        # Also add the inverse cmap
        inverse = ds_cmap(cmap_object.pos, cmap_object.color[::-1])
        cmaps.update({name + '_r': inverse})

# +-------------------+ #
# | Prepare colormaps | # ======================================================
# +-------------------+ #

if __name__ == '__main__' :
    from datetime import datetime
    print('Caching colormaps...')
    n = datetime.now

    cmaps = dict()
    # Convert all matplotlib colormaps to pyqtgraph ones and make them available 
    # in the dict cmaps
    start = n()
    for name in colormaps() :
        cmap = cm.get_cmap(name)
        cmaps.update({name: convert_matplotlib_to_pyqtgraph(cmap)})
    print('mpl: ', n()-start)

    # Add additional colormaps from package
    data_path = pkg_resources.resource_filename('data_slicer', 'data/')
    try :
        datafiles = os.listdir(data_path)
    except FileNotFoundError :
        warnings.warn('Package colormaps were not found.')
        datafiles = []

    for cmap in datafiles :
        name, suffix = cmap.split('.')
        # Only load files with the .cmap suffix
        if suffix != 'cmap' :
            continue
        cmap_object = load_custom_cmap(data_path + cmap)
        cmaps.update({name: cmap_object})
        # Also add the inverse cmap
        inverse = ds_cmap(cmap_object.pos, cmap_object.color[::-1])
        cmaps.update({name + '_r': inverse})
    print('data/: ', n()-start)

    # Store the cmaps dict
    with open(data_path + CACHED_CMAPS_FILENAME, 'wb') as f :
        pickle.dump(cmaps, f)

