from inspect import signature
from types import FunctionType

import numpy as np
from pyqtgraph import IsocurveItem

import data_slicer.utilities as util

class ModelError(Exception) :
    """ Base class for :class:`Model <data_slicer.model.Model>` related 
    errors. 
    """
    pass

class UndefinedModelError(ModelError) :
    """ Error raised when an operation would require the *model* attribute of 
    :class: `Model <data_slicer.model.Model>` but it is not found.
    """
    pass

class UndefinedAxisError(ModelError) :
    """ Error raised when an operation would require all the axes in the 
    *axes* attribute of :class: `Model <data_slicer.model.Model>` but at least
    one of them is not found.
    """
    pass

class Model() :
    """
    General object that allows calculating a model over some input axes. It 
    also provides functionalities to extract different slices from the 
    calculated data.
    """
    MIN_AXIS_LENGTH = 100

    def __init__(self, model=None) :
        """ 
        **Parameters**

        =====  =================================================================
        model  callable; a python function representing the model.
        =====  =================================================================

        .. seealso::
            :meth:`set_model <data_slicer.model.Model.set_model>`
        """
        self.data = None

        if model is not None :
            self.set_model(model)
        else :
            self.model = None

    def __repr__(self) :
        base = '<Model: {}>'
        try :
            self._check_if_model_defined()
        except UndefinedModelError :
            return base.format('undefined')
        inner = 'n_args={}, n_kwargs={}'.format(self.n_args, self.n_kwargs)
        return base.format(inner)

    def set_model(self, model) :
        """ Specify the function that represents the model. This should be a 
        function with the call signature::

            model(axis1, axis2, ..., axisN, kwarg1=kwarg1_default, ..., 
                  kwargN=kwargN_default, **kwargs)
        
        I.e. all the positional arguments (*axis1* to *axisN*) correspond to 
        the required input variables. The keyword arguments (*kwarg1* to 
        *kwargN*) as well as further unspecified *kwargs* can be used for the 
        model parameters.

        Information about the number of arguments is obtained through 
        introspection.

        **Parameters**

        =====  =================================================================
        model  callable; a python function representing the model.
        =====  =================================================================
        """
        # Check if a function was supplied
        if not isinstance(model, FunctionType) :
            raise TypeError('*model* has to be a function.')
        self.model = model

        # Get information about the supplied function
        sig = signature(model)
        # Count the number of different arguments
        n_args = 0
        n_kwargs = 0
        has_var_kwargs = False
        for name in sig.parameters :
            param = sig.parameters[name]
            kind = param.kind
            if kind == param.POSITIONAL_OR_KEYWORD : n_args += 1
            elif kind == param.KEYWORD_ONLY : n_kwargs += 1
            elif kind == param.VAR_KEYWORD : has_var_kwargs = True
        self.n_args = n_args
        self.n_kwargs = n_kwargs
        self.has_var_kwargs = has_var_kwargs
        # Prepare a container for the axes
        self.axes = n_args * [None]

    def _check_if_model_defined(self) :
        """ Raise an appropriate error if no model function is found. """
        if self.model is None :
            raise UndefinedModelError('No model has been defined. Use the '
                                      'set_model() attribute.')

    def _check_if_axes_defined(self) :
        """ Raise an appropriate error if at least one of the necessary axes 
        has not been properliy defined. 
        """
        need_to_raise = False
        if 'axes' in self.__dict__ :
            for axis in self.axes :
                if axis is None : need_to_raise = True
        else :
            need_to_raise = True
        if need_to_raise :
            message = ('At least one out of {} axes has not been defined. '
                       'Use the set_axis() attribute.')
            raise UndefinedAxisError(message.format(self.n_args))

    def set_axes(self, axes) :
        """ Set all axes (inputs for the model). The axes supplied here can 
        either be 1 dimensional array-like objects representing the actual 
        values at which the model should be evaluated or simply the start and 
        stop values for the range in which the model will be evaluated.
        If the length of any axis is smaller than Model.MIN_AXIS_LENGTH or if 
        just start and stop values are given, linearly space values between 
        start and stop will be given.
        
        **Parameters**

        ====  ==================================================================
        axes  list of len(self.n_args); an error will be thrown if the number 
              of supplied axes does not match what is necessary for self.model.
        ====  ==================================================================

        .. seealso::
            :meth:`set_axis <data_slicer.model.Model.set_axis>` to set just 
            one specific axis.
        """
        if len(axes) != self.n_args :
            message = ('The number of supplied axes ({}) does not match the '
                       'number of required axes ({}).')
            raise ValueError(message.format(len(axes), self.n_args))
        for i, axis in enumerate(axes) :
            self.set_axis(axis, dim=i)

    def set_axis(self, axis, dim=0) :
        """ Set the axis (input to the model) at position *dim*. See 
        documentation of :meth:`set_axes <data_slicer.model.Model.set_axes>` 
        for more details.
        
        **Parameters**

        ====  ==================================================================
        axis  1d array-like; the values at which the model should be 
              evaluated along this dimension. If the length is smaller than 
              Model.MIN_AXIS_LENGTH, linearly spaced values between the first 
              and last value in *axis* will be created. 
        ====  ==================================================================

        ..  seealso::
            :meth:`set_axes <data_slicer.model.Model.set_axes>` to set all 
            axes at once.
        """
        self._check_if_model_defined()
        if len(axis) < self.MIN_AXIS_LENGTH :
            axis = np.linspace(axis[0], axis[-1], self.MIN_AXIS_LENGTH)

        self.axes[dim] = axis

    def get_axes_dims(self) :
        """ Return the length of all axes that are defined. """
        # If a model is defined, the axes will at least have been initialized
        self._check_if_model_defined()
        lengths = []
        for axis in self.axes :
            if axis is None :
                lengths.append(None)
            else :
                lengths.append(len(axis))
        return lengths
        
    def calculate_model_data(self, axes=None, **kwargs) :
        """
        Evaluate the given model function :meth:`model 
        <data_slicer.model.Model.model>` at every point in the hypervolume 
        defined by the *axes*. This means that every possible combination of 
        coordinates of all *axes* is created, and the model evaluated at 
        every such point.

        **Parameters**

        ======  ================================================================
        axes    if specified, this is passed on to :meth:`set_axes 
                <data_slicer.model.Model.set_axes>`. Otherwise the previously 
                set axes will be used.
        kwargs  all keyword arguments are passed to the model function.
        ======  ================================================================
        """
        self._check_if_model_defined()
        if axes is None :
            self._check_if_axes_defined()
        else :
            self.set_axes(axes)

        self.meshes = np.meshgrid(*self.axes)
        data = self.model(*self.meshes, **kwargs)
        self.data = data
        return data

    def make_slice(self, dim, index, integrate=0, silent=False) :
        """ Return a slice out of the model data. If the data has not yet 
        been calculated, try to do it first.
        This wraps :func:`make_slice <data_slicer.utilities.make_slice>`.
        Confer respective documentation for information on the arguments.
        """
        try :
            data = self.data
        except AttributeError :
            data = self.calculate_model_data()
        return util.make_slice(data, dim, index, integrate, silent)

    def get_isocurve(self, level, pen=dict(color='r', width=2), **kwargs) :
        """ 
        .. warning::
            Only possible for 2D models (i.e. self.n_args==2).

        Return an isocurve (:class:`IsocurveItem 
        <pyqtgraph.graphicsItems.IsocurveItem>` of the model data at the 
        selected *level*.

        This uses pyqtgraph's icocurve function, which is based on the 
        marching squares algorithm.

        **Parameters**

        =====  =================================================================
        level  float; value at which the isocurve is generated.
        pen    arguments for the visual properties of the isocurve. Can be 
               anything which is valid for :func:`mkPen <pyqtgraph.mkPen>`.
        =====  =================================================================

        **Returns**

        ============  ==========================================================
        isocurveItem  :class:`IsocurveItem 
                      <pyqtgraph.graphicsItems.IsocurveItem>`
        ============  ==========================================================
        """
        # Check for correct dimensionality
        self._check_if_model_defined()
        if self.n_args != 2 :
            raise ModelError('Isocurves can only be generated for 2D models, '
                             'but n_args is {}'.format(self.n_args))

        # Check if data has been calculated
        if self.data is None :
            self.calculate_model_data()
        return IsocurveItem(data=self.data, level=level, pen=pen, **kwargs)

    def get_values_around(self, value, eps) :
        """ 
        .. warning::
            unfinished
        """
        mask = np.where(np.abs(self.data - value) < eps)
        points = self.data[mask]
        return [mesh[mask] for mesh in self.meshes], points

# Testing
if __name__ == '__main__' :
    my_model = Model()
    func1 = lambda x,y : x**2 + y**2
    my_model.set_model(func1)
    my_model.set_axes([[0, 100], [0, 150]])
    data = my_model.calculate_model_data()
    meshes, points = my_model.get_values_around(50, 1)


