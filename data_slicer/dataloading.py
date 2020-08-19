"""
Tools for putting different data formats into suitable numpy arrays.
"""
import os
import pickle
from argparse import Namespace
from warnings import catch_warnings

import numpy as np

class Dataloader() :
    """ 
    Base dataloader class (interface) from which others inherit some 
    methods (specifically the ``__repr__()`` function). 
    """
    name = 'Base'

    def __init__(self, *args, **kwargs) :
        pass

    def __repr__(self, *args, **kwargs) :
        return '<class Dataloader_{}>'.format(self.name)

    def print_m(self, *messages) :
        """ Print message to console, adding the dataloader name. """
        s = '[Dataloader {}]'.format(self.name)
        print(s, *messages)
    
    def load_data(self, *args, **kwargs) :
        """ Method stub to be overwritten by subclasses. Return data in the 
        form of an argparse.Namespace object *D* with the following structure: 

        ======  ============================================================
        D.data  np.array containing the data.
        D.axes  list of length len(D.data.shape). Contains a 1d np.array 
                representing each axis (or *None*)
        ======  ============================================================
        """
        raise NotImplementedError(('{} is an abstract base class. Use an '
                                   'appropriate subclass instead.').format(
                                   type(self)))

class Dataloader_Pickle(Dataloader) :
    """ Confer documentation of 
    :func:`~data_slicer.dataloading.Dataloader_Pickle.load_data()`. 
    """
    name = 'Pickle'

    def load_data(self, filename) :
        """ Load data that has been saved using python's `pickle` module. 
        The data is assumed to be either just a naked array, a dictionary 
        containing the keys *data* and *axes* or an argparse.Namespace 
        instance, containing these same keys.
        """
        # Open the file and get a handle for it
        with open(filename, 'rb') as f :
            filedata = pickle.load(f)
        
        if isinstance(filedata, type(np.array([]))) :
            axes = 3*[None]
            data = filedata
        elif isinstance(filedata, type(dict())) :
            data = filedata['data']
            axes = [filedata[i+'axis'] for i in 'xyz']
        elif isinstance(filedata, type(Namespace())) :
            # Nothing to do
            return filedata
        else :
            raise(TypeError('Filetype not understood.'))
        
        # Convert to Namespace
        D = Namespace(data=data, axes=axes)
        return D

class Dataloader_3dtxt(Dataloader) :
    """ Confer documentation of 
    :func:`~data_slicer.dataloading.Dataloader_3dtxt.load_data()`. 
    """
    name = '3d txt'

    def load_data(self, filename) :
        """ Load data of shape (nx, ny, nz) that is stored in a .txt file in 
        the format::

            #Z      Y       X       I(X, Y, Z)
            z0      y0      x0      I(0, 0, 0)
            z1      y0      x0      I(0, 0, 1)
            z2      y0      x0      I(0, 0, 2)
            z3      y0      x0      I(0, 0, 3)
            ...
            z(nz-1) y0      x0      I(0, 0, nz-1)
            z(nz)   y0      x0      I(0, 0, nz)
            z0      y1      x0      I(0, 1, 0)
            z1      y1      x0      I(0, 1, 1)
            z2      y1      x0      I(0, 1, 2)
            ...
            z(nz-1) y1      x0      I(0, 1, nz-1)
            z(nz)   y1      x0      I(0, 1, nz)
            ...
            ...
            z0      y(ny)   x0      I(0, ny, 0)
            z1      y(ny)   x0      I(0, ny, 1)
            ...
            z(nz)   y(ny)   x0      I(0, ny, nz)
            z0      y0      x1      I(1, 0, 0)
            z1      y0      x1      I(1, 0, 1)
            ...
            ...
            z(nz)   y(ny)   x(nx)   I(nz, ny, nx)

        """
        data = np.loadtxt(filename)

        # Get the length of the x, y and z axes by counting the number of 
        # unique elements. Then construct the axes.
        z_elements = set(data[:,0])
        nz = len(list(z_elements))
        # Pick the first *nz* elements
        zaxis = data[:nz,0]

        y_elements = set(data[:,1])
        ny = len(list(y_elements))
        # Pick every nz'th element, but only up to ny*nz
        yaxis = data[:ny*nz:nz,1]

        x_elements = set(data[:,2])
        nx = len(list(x_elements))
        # Pick every ny*nz'th element
        xaxis = data[::ny*nz,2]
 
        res = data[:,3].reshape(nx, ny, nz)

        # Return an argparse.Namespace
        D = Namespace(data=res, axes=[xaxis, yaxis, zaxis])
        return D

registered_loaders = [Dataloader_Pickle, Dataloader_3dtxt]

# Function to try all dataloaders in all_dls
def load_data(filename, exclude=None, suppress_warnings=False) :
    """ Try to load some dataset 'filename' by iterating through `all_dls` 
    and appliyng the respective dataloader's load_data method. If it works: 
    great. If not, try with the next dataloader. 
    Collects and prints all raised exceptions in case that no dataloader 
    succeeded.
    """ 
    # Sanity check: does the given path even exist in the filesystem?
    if not os.path.exists(filename) :
        raise FileNotFoundError(filename) 

    # If only a single string is given as exclude, pack it into a list
    if exclude is not None and type(exclude)==str :
        exclude = [exclude]
    
    # Keep track of all exceptions in case no loader succeeds
    exceptions = dict()

    # Suppress warnings
    with catch_warnings() :
        if suppress_warnings :
            simplefilter('ignore')
        for dataloader in registered_loaders :
            # Instantiate a dataloader object
            dl = dataloader()

            # Skip to the next if this dl is excluded (continue brings us 
            # back to the top of the loop, starting with the next element)
            if exclude is not None and dl.name in exclude : 
                continue

            # Try loading the data
            try :
                namespace = dl.load_data(filename)
            except Exception as e :
                # Temporarily store the exception
                exceptions.update({dl : e})
                # Try the next dl
                continue

            # Reaching this point must mean we succeeded. Print warnings from 
            # this dataloader, if any occurred
            print('Loaded data with {}.'.format(dl))
            try :
                print(dl, ': ', exceptions[dl])
            except KeyError :
                pass
            
            return namespace

    # Reaching this point means something went wrong. Print all exceptions.
    for dl in exceptions :
        print(dl)
        e = exceptions[dl]
        print('Exception {}: {}'.format(type(e), e))

    raise Exception('Could not load data {}.'.format(filename))

# Convenience for creating txt files
def three_d_to_txt(outfilename, data, axes=3*[None], force=False) :
    """ Create a txt file that can be read by 
    :class:`~data_slicer.dataloading.Dataloader_txt`.

    **Parameters**

    ===========  ==============================================================
    outfilename  str; filename and/or path to the file to write into.
    data         np.array; 3d array of the data.
    axes         list; [xaxis, yaxis, zaxis]. Any of these can be *None*, in 
                 which case incremental integers will be used.
    force        boolean; Whether or not to overwrite an existing file. If 
                 *False* and a file of *outfilename* exists, an Exception is 
                 raised.
    ===========  ==============================================================
    """
    x, y, z = data.shape
    # Set all undefined axes to pixels
    for i,ax in enumerate(axes) :
        if ax is None :
            axes[i] = range(data.shape[i])

    # Choose the opening mode
    if force :
        mode = 'w'
    else :
        mode = 'x'

    # Write the file
    with open(outfilename, mode) as f :
        # Prepare the format string
        fmt = 4*'{:>15} '
        fmt += '\n'
        # Write a header line
        f.write('#' + fmt.format('z', 'y', 'x', 'data'))
        # Append a space for alignment
        fmt = ' ' + fmt
        for i in range(x) :
            for j in range(y) :
                for k in range(z) :
                    line = fmt.format(axes[2][k], axes[1][j], axes[0][i], 
                                      data[i,j,k])
                    f.write(line)

if __name__=="__main__" :
    a = np.array([[[0, 0, 0], [1, 2, 3]], [[1, 1, 1], [11, 22, 33]]])
    foofile = 'foofoo.txt'
    three_d_to_txt(foofile, a, axes=[[11, 12], [21, 22], [31, 32, 33]], 
                   force=True)
    b = load_data(foofile)
    print(a)
    print(b.data)
    print(b.axes)

