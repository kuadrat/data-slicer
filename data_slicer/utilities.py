
import logging
import warnings

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import PowerNorm
from matplotlib.figure import Figure
from matplotlib.patheffects import withStroke
from pyqtgraph import Qt as qt

logger = logging.getLogger('ds.'+__name__)
# The logging level for signals
SIGNALS = 5

#_Constants_____________________________________________________________________

CACHED_CMAPS_FILENAME = 'cmaps.p'
CONFIG_DIR = '.data_slicer/'

#_Utilities_____________________________________________________________________

class TracedVariable(qt.QtCore.QObject) :
    """ A pyqt implementaion of tkinter's/Tcl's traced variables using Qt's 
    signaling mechanism.
    Basically this is just a wrapper around any python object which ensures 
    that pyQt signals are emitted whenever the object is accessed or changed.

    In order to use pyqt's signals, this has to be a subclass of 
    :class:`QObject <pyqtgraph.Qt.QtCore.QObject>`.
    
    **Attributes**

    ==========================  ================================================
    _value                      the python object represented by this 
                                TracedVariable instance. Should never be 
                                accessed directly but only through the getter 
                                and setter methods.
    sig_value_changed           :class:`Signal <pyqtgraph.Qt.QtCore.Signal>`; 
                                the signal that is emitted whenever 
                                ``self._value`` is changed.
    sig_value_read              :class:`Signal <pyqtgraph.Qt.QtCore.Signal>`; 
                                the signal that is emitted whenever 
                                ``self._value`` is read.
    sig_allowed_values_changed  :class:`Signal <pyqtgraph.Qt.QtCore.Signal>`; 
                                the signal that is emitted whenever 
                                ``self.allowed_values`` are set or unset.
    allowed_values              :class:`array <numpy.ndarray>`; a sorted 
                                list of all values that self._value can 
                                assume. If set, all tries to set the value 
                                will automatically set it to the closest 
                                allowed one.
    ==========================  ================================================
    """
    sig_value_changed = qt.QtCore.Signal()
    sig_value_read = qt.QtCore.Signal()
    sig_allowed_values_changed = qt.QtCore.Signal()

    def __init__(self, value=None, name=None) :
        # Initialize instance variables
        self.allowed_values = None

        # Have to call superclass init for signals to work
        super().__init__()

        self._value = value
        if name is not None :
            self.name = name
        else :
            self.name = 'Unnamed'

    def __repr__(self) :
        return '<TracedVariable({}, {})>'.format(self.name, self._value)

    def set_value(self, value=None) :
        """ Emit sig_value_changed and set the internal self._value. """
        # Choose the closest allowed value
        if self.allowed_values is not None :
            value = self.find_closest_allowed(value)
        self._value = value
        logger.log(SIGNALS, '{} {}: Emitting sig_value_changed.'.format(
                   self.__class__.__name__, self.name))
        self.sig_value_changed.emit()

    def get_value(self) :
        """ Emit sig_value_changed and return the internal self._value. 

        .. warning:: 
            the signal is emitted here before the caller actually receives 
            the return value. This could lead to unexpected behaviour. 
        """
        logger.log(SIGNALS, '{} {}: Emitting sig_value_read.'.format( 
                   self.__class__.__name__, self.name))
        self.sig_value_read.emit()
        return self._value

    def on_change(self, callback) :
        """ Convenience wrapper for :class:`Signal 
        <pyqtgraph.Qt.QtCore.Signal>`'s 'connect'. 
        """
        self.sig_value_changed.connect(callback)

    def on_read(self, callback) :
        """ Convenience wrapper for :class:`Signal 
        <pyqtgraph.Qt.QtCore.Signal>`'s 'connect'. 
        """
        self.sig_value_read.connect(callback)

    def set_allowed_values(self, values=None) :
        """ Define a set/range/list of values that are allowed for this 
        Variable. Once set, all future calls to set_value will automatically 
        try to pick the most reasonable of the allowed values to assign. 

        Emits :signal:`sig_allowed_values_changed`

        **Parameters**

        ======  =================================================================
        values  iterable; The complete list of allowed (numerical) values. This
                is converted to a sorted np.array internally. If values is 
                `None`, all restrictions on allowed values will be lifted and 
                all values are allowed.
        ======  =================================================================
        """
        if values is None :
            # Reset the allowed values, i.e. all values are allowed
            self.allowed_values = None
            self.min_allowed = None
            self.max_allowed = None
        else :
            # Convert to sorted numpy array
            try :
                values = np.array(values)
            except TypeError :
                message = 'Could not convert allowed values to np.array.'
                raise TypeError(message)

            # Sort the array for easier indexing later on
            values.sort()
            self.allowed_values = values

            # Store the max and min allowed values (necessary?)
            self.min_allowed = values[0]
            self.max_allowed = values[-1]

        logger.log(SIGNALS, 
                   '{} {}: Emitting sig_allowed_values_changed.'.format(
                   self.__class__.__name__, self.name))

        # Update the current value to within the allowed range
        self.set_value(self._value)
        self.sig_allowed_values_changed.emit()

    def find_closest_allowed(self, value) :
        """ Return the value of the element in self.allowed_values (if set) 
        that is closest to `value`. 
        """
        if self.allowed_values is None :
            return value
        else :
            ind = np.abs( self.allowed_values-value ).argmin()
            return self.allowed_values[ind]

#_Functions_____________________________________________________________________

def indexof(value, array) :
    """ 
    Return the first index of the value in the array closest to the given 
    `value`.

    Example::

        >>> a = np.array([1, 0, 0, 2, 1])
        >>> indexof(0, a)
        1
        >>> indexof(0.9, a)
        0
    """
    return np.argmin(np.abs(array - value))

def pop_kwarg(name, kwargs, default=1) :
    """ Check if a keyword *name* appears in the dictionary *kwargs*. If yes, 
    remove it from the dictionary, returning its value. If no, return the 
    value specified by *default*.
    """
    if name in kwargs :
        return kwargs.pop(name)
    else :
        return default

def make_slice_3d(data, d, i, integrate=0, silent=False) :
    """ 
    :deprecated: 

    .. warning::
        Use :func:`make_slice <data_slicer.utilities.make_slice>`
        instead. (though this ~might~ be slightly faster for 3d datasets)

    Create a slice out of the 3d data (l x m x n) along dimension d 
    (0,1,2) at index i. Optionally integrate around i.

    **Parameters**

    =========  =================================================================
    data       array-like; data of the shape (x, y, z)
    d          int, d in (0, 1, 2); dimension along which to slice
    i          int, 0 <= i < data.size[d]; The index at which to create the slice
    integrate  int, ``0 <= integrate < |i - n|``; the number of slices above 
               and below slice i over which to integrate
    silent     bool; toggle warning messages
    =========  =================================================================

    **Returns**

    ===  =======================================================================
    res  np.array; Slice at index with dimensions ``shape[:d] + shape[d+1:]`` 
         where shape = (x, y, z).
    ===  =======================================================================
    """
    # Get the relevant dimensions
    shape = data.shape
    try :
        n_slices = shape[d]
    except IndexError :
        print('d ({}) can only be 0, 1 or 2 and data must be 3D.'.format(d))
        return

    # Set the integration indices and adjust them if they go out of scope
    start = i - integrate
    stop = i + integrate + 1
    if start < 0 :
        if not silent :
            warnings.warn(
            'i - integrate ({}) < 0, setting start=0'.format(start))       
        start = 0
    if stop > n_slices :
        if not silent :
            warning = ('i + integrate ({}) > n_slices ({}), setting '
                       'stop=n_slices').format(stop, n_slices)       
            warnings.warn(warning)
        stop = n_slices

    # Initialize data container and fill it with data from selected slices
    if d == 0 :
        sliced = data[start:stop,:,:].sum(d)
    elif d == 1 :
        sliced = data[:,start:stop,:].sum(d)
    elif d == 2 :
        sliced = data[:,:,start:stop].sum(d)

    return sliced

def make_slice(data, dim, index, integrate=0, silent=False) :
    """
    Take a slice out of an N dimensional dataset *data* at *index* along 
    dimension *dim*. Optionally integrate by +- *integrate* channels around 
    *index*.
    If *data* has shape::

        (n0, n1, ..., n(dim-1), n(dim), n(dim+1), ..., n(N-1))

    the result will be of dimension N-1 and have shape::

        (n0, n1, ..., n(dim-1), n(dim+1), ..., n(N-1))

    or in other words::

        shape(result) = shape(data)[:dim] + shape(data)[dim+1:]

    .

    **Parameters**

    =========  =================================================================
    data       array-like; N dimensional dataset.
    dim        int, 0 <= d < N; dimension along which to slice.
    index      int, 0 <= index < data.size[d]; The index at which to create 
               the slice.
    integrate  int, ``0 <= integrate < |index|``; the number of slices above 
               and below slice *index* over which to integrate. A warning is 
               issued if the integration range would exceed the data (can be 
               turned off with *silent*).
    silent     bool; toggle warning messages.
    =========  =================================================================

    **Returns**

    ===  =======================================================================
    res  np.array; slice at *index* alond *dim* with dimensions shape[:d] + 
         shape[d+1:].
    ===  =======================================================================
    """
    # Find the dimensionality and the number of slices along the specified 
    # dimension.
    shape = data.shape
    ndim = len(shape)
    try :
        n_slices = shape[dim]
    except IndexError :
        message = ('*dim* ({}) needs to be smaller than the dimension of '
                   '*data* ({})').format(dim, ndim)
        raise IndexError(message)

    # Set the integration indices and adjust them if they go out of scope
    start = index - integrate
    stop = index + integrate + 1
    if start < 0 :
        if not silent :
            warnings.warn(
            'i - integrate ({}) < 0, setting start=0'.format(start))       
        start = 0
    if stop > n_slices :
        if not silent :
            warning = ('i + integrate ({}) > n_slices ({}), setting '
                       'stop=n_slices').format(stop, n_slices)       
            warnings.warn(warning)
        stop = n_slices
    
    # Roll the original data such that the specified dimension comes first
    i_original = np.arange(ndim)
    i_rolled = np.roll(i_original, dim)
    data = np.moveaxis(data, i_original, i_rolled)
    # Take the slice
    sliced = data[start:stop].sum(0)
    # Bring back to more intuitive form. For that we have to remove the now 
    # lost dimension from the index arrays and shift all indices.
    i_original = np.concatenate((i_original[:dim], i_original[dim+1:]))
    i_original[i_original>dim] -= 1
    i_rolled = np.roll(i_original, dim)
    return np.moveaxis(sliced, i_rolled, i_original)

def roll_array(a, i) :
    """ Cycle the arrangement of the dimensions in an *N* dimensional array.
    For example, change an X-Y-Z arrangement to Y-Z-X.

    **Parameters**

    =  =========================================================================
    a  array of *N* dimensions, i.e. `len(a.shape) = N`.
    i  int; number of dimensions to roll
    =  =========================================================================

    **Returns**

    ===  =======================================================================
    res  array of *N* dimensions where the axes have been rearranged as 
         follows::

             before: `shape(a) = (d[0], d[1], ..., d[N])`
             after:  `shape(res) = (d[(0+i)%N], d[(1+i)%N], ..., d[(N+i)%N])`
    ===  =======================================================================
    """
    # Create indices and rolled indices
    N = len(a.shape)
    indices = np.arange(N)
    rolled_indices = np.roll(indices, i)

    # Move the axes in the array accordingly
    res = np.moveaxis(a, indices, rolled_indices)
    return res

def get_lines(data, n, dim=0, i0=0, i1=-1, offset=0.2, integrate='max', 
              **kwargs) :
    """
    Extract *n* evenly spaced rows/columns from data along dimension *dim* 
    between indices *i0* and *i1*. The extracted lines are normalized and offset
    such that they can be nicely plotted close by each other - as is done, for
    example in :func:`lineplot <data_slicer.pit.PITDataHandler.lineplot>`.

    **Parameters**

    =========  =================================================================
    data       2d np.array; the data from which to extract lines.
    n          int; the number of lines to extract.
    dim        int; either 0 or 1, specifying the dimension along which to 
               extract lines.
    i0         int; starting index in *data* along *dim*.
    i1         int; ending index in *data* along *dim*.
    offset     float; how much to vertically translate each successive line.
    integrate  int or other; specifies how many channels around each line 
               index should be integrated over. If anything but a small 
               enough integer is given, defaults to the maximally available 
               integration range.
    kwargs     any other passed keyword arguments are discarded.
    =========  =================================================================

    **Returns**

    =======  ===================================================================
    lines    list of 1d np.arrays; the extracted lines.
    indices  list of int; the indices at which the lines were extracted.
    =======  ===================================================================
    """
    # Sanity check
    shape = data.shape
    try :
        assert len(shape) == 2
    except AssertionError :
        message = '*data* should be a 2d np.array. Found: {} dimensions.'
        message = message.format(len(shape))
        raise TypeError(message)

    # Normalize data and transpose if necessary
    if dim == 1 :
        data = data.T
    norm = np.max(data[i0:i1])
    data /= norm

    # Calculate the indices at which to extract lines.
    # First the raw step size *delta*
    if i1 == -1 : i1 = shape[dim]-1
    delta = (i1 - i0)/n
    # The maximum number of channels we can integrate around each index is 
    # delta/2
    max_integrate = int(delta/2)
    # Adjust the user supplied *integrate* value, if necessary
    if type(integrate) != int or integrate > max_integrate :
        integrate = max_integrate
    # Construct equidistantly spaced center indices, leaving space above and 
    # below for the integration.
    indices = [int(round(i)) for i in 
               np.linspace(i0+integrate+1, i1-integrate, n)]

    # Extract the lines
    lines = []
    sumnorm = 2*integrate + 1
    for i in range(n) :
        start = indices[i] - integrate
        stop = indices[i] + integrate + 1
        line = np.sum(data[start:stop], 0)/sumnorm + i*offset
        lines.append(line)
    return lines, indices

def plot_cuts(data, dim=0, integrate=0, zs=None, labels=None, max_ppf=16, 
              max_nfigs=4, **kwargs) :
    """ Plot all (or only the ones specified by `zs`) cuts along dimension `dim` 
    on separate subplots onto matplotlib figures.

    **Parameters**

    =========  =================================================================
    data       3D np.array with shape (z,y,x); the data cube.
    dim        int; one of (0,1,2). Dimension along which to take the cuts.
    integrate  int or 'full'; number of slices to integrate around each 
               extracted cut. If 'full', take the maximum number possible, 
               depending whether the number of cuts is reduced due to 
               otherwise exceeding *max_nfigs*. 'full' does not work if *zs* 
               are given.
    zs         1D np.array; selection of indices along dimension `dim`. Only 
               the given indices will be plotted.
    labels     1D array/list of length z. Optional labels to assign to the 
               different cuts
    max_ppf    int; maximum number of plots per figure.
    max_nfigs  int; maximum number of figures that are created. If more would 
               be necessary to display all plots, a warning is issued and 
               only every N'th plot is created, where N is chosen such that 
               the whole 'range' of plots is represented on the figures. 
    kwargs     dict; keyword arguments passed on to :func:`pcolormesh 
               <matplotlib.axes._subplots.AxesSubplot.pcolormesh>`. 
               Additionally, the kwarg `gamma` for power-law color mapping 
               is accepted.
    =========  =================================================================
    """
    # Create a list of all indices in case no list (`zs`) is given
    if zs is None :
        zs = np.arange(data.shape[dim])
    elif integrate == 'full' :
        warnings.warn('*full* option does not work when *zs* are specified.')
        integrate = 0

    # The total number of plots and figures to be created
    n_plots = len(zs)
    n_figs = int( np.ceil(n_plots/max_ppf) )
    nth = 1
    if n_figs > max_nfigs :
        # Only plot every nth plot
        nth = round(n_plots/(max_ppf*max_nfigs))
        # Get the right English suffix depending on the value of nth
        if nth <= 3 :
            suffix = ['st', 'nd', 'rd'][nth-1]
        else :
            suffix = 'th'
        warnings.warn((
        'Number of necessary figures n_figs ({0}) > max_nfigs ({1}).' +
        'Setting n_figs to {1} and only plotting every {2}`{3} cut.').format( 
            n_figs, max_nfigs, nth, suffix))
        n_figs = max_nfigs
        n_plots = max_ppf*n_figs

    # Figure out how much we should integrate
    if integrate == 'full' or integrate > nth/2 :
        integrate = int(nth/2)

    # If we have just one figure, make the subplots as big as possible by 
    # setting the number of subplots per row (ppr) to a reasonable value
    if n_figs == 1 :
        ppr = int( np.ceil(np.sqrt(n_plots)) )
    else :
        ppr = int( np.ceil(np.sqrt(max_ppf)) )

    # Depending on the dimension we need to extract the cuts differently. 
    # Account for this by moving the axes
    x = np.arange(len(data.shape))
    data = np.moveaxis(data, x, np.roll(x, dim))

    # Extract kwargs used for the PowerNorm
    gamma = pop_kwarg('gamma', kwargs, 1)
    vmin = pop_kwarg('vmin', kwargs, None)
    vmax = pop_kwarg('vmax', kwargs, None)

    # Define the beginnings of the plot in figure units
    margins = dict(left=0, right=1, bottom=0, top=1)

    figures = []
    for i in range(n_figs) :
        # Create the figure with pyplot 
        fig = plt.figure()
        start = i*ppr*ppr
        stop = (i+1)*ppr*ppr
        # Iterate over the cuts that go on this figure
        for j,z in enumerate(zs[start:stop]) :
            # Try to extract the cut and create the axes 
            cut_index = z*nth
            if cut_index < data.shape[0] :
                cut = make_slice(data, 0, cut_index, integrate)
            else :
                continue
            # Transpose to counter matplotlib's transposition
            cut = cut.T
            ax = fig.add_subplot(ppr, ppr, j+1)
            ax.pcolormesh(cut, 
                          norm=PowerNorm(gamma=gamma, vmin=vmin, vmax=vmax), 
                          **kwargs)
            ax.set_xticks([])
            ax.set_yticks([])
            if labels is not None :
                labeltext = str(labels[cut_index])
            else :
                labeltext = str(cut_index)
            label = ax.text(0, 0, labeltext, size=10)
            label.set_path_effects([withStroke(linewidth=2, foreground='w', 
                                               alpha=0.5)])

        fig.subplots_adjust(hspace=0.01, wspace=0.01, **margins)
        figures.append(fig)

    return figures

def get_contours(data, x=None, y=None, levels=0) :
    """ Use matplotlib`s contour function to get contour lines where the 2 
    dimensional dataset *data* intersects *levels*. 

    **Parameters**

    ======  ====================================================================
    data    2d-array; shape (nx, ny)
    x       array-like; can be a linear array of shape (nx) or a meshgrid of 
            shape (nx, ny)
    y       array-like; can be a linear array of shape (ny) or a meshgrid of 
            shape (nx, ny)
    levels  float or list of float; the levels at which to extract the 
            contour lines. Due to a matplotlib limitation, these numbers have 
            to be in ascending order.
    ======  ====================================================================

    **Returns**

    ========  ==================================================================
    contours  list of 2d-arrays; each array of shape (2, N) contains the x and
              y coordinates of a contour line.
    ========  ==================================================================
    """
    # Handle input
    data = np.asarray(data)
    shape = data.shape
    if len(shape) != 2 :
        raise ValueError('*data* should be a 2-d array. '
                         'shape(data)={}'.format(shape))
    # Default to index arrays
    if x is None or y is None :
        x = np.arange(shape[0])
        y = np.arange(shape[1])
    else :
        x = np.asarray(x)
        y = np.asarray(y)
    # Make meshgrid and sanity check for shapes
    if len(x.shape) == 1 and len(y.shape) == 1 :
        X, Y = np.meshgrid(x, y)
    elif len(x.shape) == 2 and len(y.shape) == 2 :
        X, Y = x, y
    else :
        raise ValueError('*x* and *y* should have the same shape. '
                         'x.shape={}, y.shape={}'.format(x.shape, y.shape))
    if isinstance(levels, int) : levels = [levels]

    # Create invisible figure and axes to get access to the contour function
    ghost_fig = Figure()
    ghost_ax = ghost_fig.add_subplot(111)

    # Use contour to do the work
    collections = ghost_ax.contour(X, Y, data, levels=levels).collections
    contours = []
    for collection in collections :
        verts = collection.get_paths()[0].vertices
        contours.append(np.array([verts[:,0], verts[:,1]]))

    # Clean up
    ghost_fig.clear()
    del ghost_fig

    return contours

if __name__ == '__main__' :
    N = 100
    x = np.arange(N)
    y = np.arange(N)
    X, Y = np.meshgrid(x, y)
    data = (X-N/2)**2 + (Y-N/2)**2
    contours = get_contours(data, levels=[100, 200, 300, 400])

    plt.pcolormesh(X, Y, data)

    for contour in contours :
        plt.plot(contour[0], contour[1])
    plt.show()
