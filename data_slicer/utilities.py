
import logging

import numpy as np
from pyqtgraph import Qt as qt

logger = logging.getLogger('ds.'+__name__)

#_Constants_____________________________________________________________________

CONFIG_DIR = '.data_slicer/'

#_Utilities_____________________________________________________________________

class TracedVariable(qt.QtCore.QObject) :
    """ A pyqt implementaion of tkinter's/Tcl's traced variables using Qt's 
    signaling mechanism.
    Basically this is just a wrapper around any python object which ensures 
    that pyQt signals are emitted whenever the object is accessed or changed.

    In order to use pyqt's signals, this has to be a subclass of :class: 
    `QObject <pyqtgraph.Qt.QtCore.QObject>`.
    
    =================  =========================================================
    _value             the python object represented by this TracedVariable 
                       instance. Should never be accessed directly but only 
                       through the getter and setter methods.
    sig_value_changed  :class: `Signal <pyqtgraph.Qt.QtCore.Signal>`; the signal 
                       that is emitted whenever :attr: self._value is changed.
    sig_value_read     :class: `Signal <pyqtgraph.Qt.QtCore.Signal>`; the signal 
                       that is emitted whenever :attr: self._value is read.
    sig_allowed_values_changed
                       :class: `Signal <pyqtgraph.Qt.QtCore.Signal>`; the signal 
                       that is emitted whenever :attr: self.allowed_values 
                       are set or unset.
    allowed_values     :class: `array <numpy.ndarray>`; a sorted list of all 
                       values that self._value can assume. If set, all tries 
                       to set the value will automatically set it to the 
                       closest allowed one.
    =================  =========================================================
    """
    sig_value_changed = qt.QtCore.Signal()
    sig_value_read = qt.QtCore.Signal()
    sig_allowed_values_changed = qt.QtCore.Signal()
    allowed_values = None

    def __init__(self, value=None, name=None) :
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
        logger.debug(('{} {}: Emitting sig_value_changed.').format(
            self.__class__.__name__, self.name))
        self.sig_value_changed.emit()

    def get_value(self) :
        """ Emit sig_value_changed and return the internal self._value. 
        NOTE: the signal is emitted here before the caller actually receives 
        the return value. This could lead to unexpected behaviour. """
        logger.debug('{} {}: Emitting sig_value_read.'.format( 
            self.__class__.__name__, self.name))
        self.sig_value_read.emit()
        return self._value

    def on_change(self, callback) :
        """ Convenience wrapper for :class: `Signal 
        <pyqtgraph.Qt.QtCore.Signal>`'s 'connect'. 
        """
        self.sig_value_changed.connect(callback)

    def on_read(self, callback) :
        """ Convenience wrapper for :class: `Signal 
        <pyqtgraph.Qt.QtCore.Signal>`'s 'connect'. 
        """
        self.sig_value_read.connect(callback)

    def set_allowed_values(self, values=None) :
        """ Define a set/range/list of values that are allowed for this 
        Variable. Once set, all future calls to set_value will automatically 
        try to pick the most reasonable of the allowed values to assign. 
        Emits :signal: `sig_allowed_values_changed`

        ====== =================================================================
        values iterable; The complete list of allowed (numerical) values. This
               is converted to a sorted np.array internally. If values is 
               `None`, all restrictions on allowed values will be lifted and 
               all values are allowed.
        ====== =================================================================
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

        logger.debug('{} {}: Emitting sig_allowed_values_changed.'.format(
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
    :param: `value`.

    Example
    -------
    >>> a = np.array([1, 0, 0, 2, 1])
    >>> indexof(0, a)
    1
    >>> indexof(0.9, a)
    0
    """
    return np.argmin(np.abs(array - value))

def make_slice(data, d, i, integrate=0, silent=False) :
    """ Create a slice out of the 3d data (l x m x n) along dimension d 
    (0,1,2) at index i. Optionally integrate around i.

    *Parameters*
    ============================================================================
    data       array-like; data of the shape (x, y, z)
    d          int, d in (0, 1, 2); dimension along which to slice
    i          int, 0 <= i < data.size[d]; The index at which to create the slice
    integrate  int, 0 <= integrate < |i - n|; the number of slices above 
               and below slice i over which to integrate
    silent     bool; toggle warning messages
    ============================================================================

    *Returns*
    ============================================================================
    res        np.array; Slice at index with dimensions shape[:d] + shape[d+1:]
               where shape = (x, y, z).
    ============================================================================
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

def roll_array(a, i) :
    """ Cycle the arrangement of the dimensions in an *N* dimensional array.
    For example, change an X-Y-Z arrangement to Y-Z-X.

    *Parameters*
    =  =========================================================================
    a  array of *N* dimensions, i.e. `len(a.shape) = N`.
    i  int; number of dimensions to roll
    =  =========================================================================

    *Returns*
    ===  =======================================================================
    res  array of *N* dimensions where the axes have been rearranged as 
         follows: 
             before: `shape(a) = (d[0], d[1], ..., d[N])`
             after:  `shape(res) = (d[(0+i)%N], d[(1+i)%N], ..., d[(N+i)%N])
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
    example in :func: `lineplot <>`.

    *Parameters*
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

    *Returns*
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

