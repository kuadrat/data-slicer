.. _sec-data_format:

Data formats and data loading
=============================

The existing dataloaders found in the :mod:`dataloading module 
<data_slicer.dataloading>` can handle two types of input data formats:

1. A binary file that has been created using python's ``pickle`` module.
   The pickled object can be either a ``numpy`` array, or a dictionary or 
   :class:`argparse.Namespace` containing the keys *data* and *axes*, as 
   described in :class:`~data_slicer.dataloading.Dataloader_Pickle`.

2. A plain text file containing values for x, y, z and the actual data in 
   four columns as described in the documentation of 
   :class:`~data_slicer.dataloading.Dataloader_3dtxt`.
   Notice that there is an utility function 
   (:func:`~data_slicer.dataloading.three_d_to_txt`) that can help you 
   create such a text file in the correct format from existing data.

In the following we give an example tutorial for both cases.


Binary pickle files
-------------------

Step 1: Load the data into python
.................................

We will assume our starting point to be a 3D data file of any format.
It could be an `Igor file <https://www.wavemetrics.com/igor-8-highlights>`_, 
an `HDF5 file <https://www.hdfgroup.org/solutions/hdf5>`_, a `matlab 
file <https://www.mathworks.com/products/matlab.html>`_, a plain text file but 
in a different format than what is required by 
:class:`~data_slicer.dataloading.Dataloader_3dtxt` or anything else.
In any case, you will have to find a way of loading that dataset into 
python first
(For the examples listed above, the packages `igor 
<https://pypi.org/project/igor/>`_, `h5py <https://github.com/h5py/h5py>`_, 
`scipy 
<https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.loadmat.html>`_ 
or `numpy 
<https://numpy.org/doc/stable/reference/generated/numpy.loadtxt.html>`_ could 
be used, respectively).

In order to make the example more concrete and to allow for a step-by-step 
code-along experience, we will explain here how we prepared the MRI brain scan 
data that can be loaded by issuing ``mw.brain()`` on ``PIT``'s console.
But again, how exactly this step is handled depends on your starting point.
The result of Step 1 should always be the same, though: Your data should be 
accessible as a numpy array in python.

OK, now let's get started with the concrete example.
We find and download our brain scan data of a meditating person 
`here <https://openneuro.org/crn/datasets/ds000108/snapshots/00002/files/sub-01:anat:sub-01_T1w.nii.gz)>`_ [#]_.

Once downloaded, we need a way of opening it.
A quick `Ecoisa search <www.ecosia.org>`_ leads us to the library `NiBabel 
<https://nipy.org/nibabel/gettingstarted.html>`_, which seems to be able to 
open ``.nii`` files.
Thus, we install that library (depending on your system and setup there may 
be different ways of doing this)::

   pip install nibabel

Now, following the instructions on the NiBabel webpage, we load the image 
data as a numpy array::

   python
   >>> import nibabel as nib
   >>> img = nib.load('sub-01_T1w.nii.gz')
   >>> my_data = img.get_fdata()

.. note::
   You need to be in the directory where you placed the downloaded file (here 
   ``sub-01_T1w.nii.gz``) in order for this to work.

.. note::
   Just to point it out once more, the details of this first step depend very 
   much on your use case. It also does not matter whether you work in the 
   live python interpreter like in the example or whether you wrap it all in 
   a script.
   You're fine as long as you have a way of getting your data into the form 
   of a numpy array.

Step 2: Optionally change data arrangement
..........................................

Now that we have our data in a numpy array, we are free to swap axes, cut off 
undesired parts or apply any processing we like to it.
This, again, depends completely on your use case.
Since in the example here we just want to *see* the data, we have nothing to 
do.  

In case you find yourself wanting to do some rearrangements, here are a few 
functions that might be of interest: :func:`numpy.moveaxis`, 
:func:`numpy.transpose` and 
all basic :class:`numpy.ndarray` operations, like `slicing and indexing 
<https://numpy.org/devdocs/reference/arrays.indexing.html#arrays-indexing>`_.

Step 3: Optionally create axis information
..........................................

Skipping this step means that the data we end up loading into ``PIT`` will 
have axes that simply count the number of pixels (voxels) from 0 upwards.
But we can assign more meaningful units to our axes, like in our 
example we could assign length units to the *x*, *y* and *z* axes.
To do this, we have to create one 1D array for each axis and collect them in 
a list.

In our example, we found by inspecting the original data that 1 pixel 
corresponds to 0.85 mm along the x and y directions and 1.5 mm along the z 
direction.
To create some reasonable axes, we could therefore do the following::

   >>> import numpy as np
   >>> nx, ny, nz = my_data.shape
   >>> x_axis = np.arange(0, nx*0.85, 0.85)
   >>> y_axis = np.arange(0, ny*0.85, 0.85)
   >>> z_axis = np.arange(0, nz*1.5, 1.5)
   >>> my_axes = [x_axis, y_axis, z_axis]

The three axes should of course have the lengths corresponding to the data 
dimensions.

.. 
   Usually your data will be a function of some variables, e.g. our brain 
   scan data is intensity as function of space coordinate :math:`I(x, y, z)`.
   Other things would be imaginable, for example pressure in the `xy` plane as a 
   function of time `t` :math:`p(x, y, t)` or intensity as a function of 
   momentum and energy :math:`I(k_x, k_y, E)`, etc.
   In our example with the brain, we are in the first mentioned situation 
   (:math:`I(x, y, z)`).

Step 4: Pickle it!
..................

Finally we can store our data in a format that can be efficiently read by 
``PIT``.
Here, we have different options, depending on whether or not we want to 
provide axes information (step 3).
In all three cases we make use of the convenience function 
:func:`~data_slicer.dataloading.dump`, which uses the ``pickle`` module to 
store any python object::

   >>> from data_slicer.dataloading import dump

Option 1: no axes information
*****************************

This is the easiest, you can just do::

   >>> dump(my_data, 'brain.p')

This will create the file ``brain.p`` in your current working directory.
If a file of that name already exists, it will ask you for confirmation.
(Obviously you can pick a filename of your choice. It doesn't even have to 
end in ``.p``.)

Option 2: with axes information in a dictionary
***********************************************

In order to also store the axis information we created in step 3, we just 
construct a :class:`dictionary <dict>` and pickle it::

   >>> D = dict(data=my_data, axes=my_axes)
   >>> dump(D, 'brain.p')

In this case it is important that the argument names ``data`` and ``axes`` 
are exactly like that. Other names will not work.

Option 3: with axes information in a Namespace
**********************************************

This option is given for convenience and out of consistency with the 
:class:`data_slicer.dataloading.Dataloader` objects.
Whether you use options 2 or 3 is entirely up to your personal preference and 
shouldn't make any difference.
The idea is exactly the same, except that we create a 
:class:`argparse.Namespace` instead of a dictionary::

   >>> from argparse import Namespace
   >>> D = Namespace(data=my_data, axes=my_axes)
   >>> dump(D, 'brain.p')

Conclusion
..........

And that's it. We have now successfully converted a datafile into a 
``PIT``-readable format.
Of course, if you have to do this kind of operation often, it would be a good 
idea to write a little script that does these steps for you.
If you're feeling confident, you could even create a :ref:`plugin 
<sec-plugin>` for the filetype(s) you need to use and make it available to 
other people.
Or, if you're lucky, somebody else has already done this and you can just use 
that plugin.

Plain text files
----------------

Working with plain text (ASCII) files is significantly slower and requires 
more disk space than other file formats, but it can be useful to have the 
data in a human-readable form.
In order to create an plain text file in the correct format from some 
existing data, you will have to go through steps 1 to 3 exactly as in the 
description above.
The only thing that changes is the final step, step 4.

Step 4 for plain text files
...........................

In this case, we can just use the function 
:func:`data_slicer.dataloading.three_d_to_txt`::

   >>> from data_slicer.dataloading import three_d_to_txt
   >>> three_d_to_txt('brain.txt', my_data, axes=my_axes)

If you've skipped step 3, you can just leave out the ``axes`` argument.
In case you're typing along this tutorial, you will notice that the creation 
of this ``txt`` takes much longer than in the binary case - up to several 
minutes even.

.. rubric:: Footnotes

.. [#] This data set is taken from the OpenNeuro database.
       Openneuro Accession Number: ds000108
       Authored by: Wager, T.D., Davidson, M.L., Hughes, B.L., Lindquist, 
       M.A., Ochsner, K.N. (2008). Prefrontal-subcortical pathways mediating 
       successful emotion regulation. Neuron, 59(6):1037-50. 
       doi: ``10.1016/j.neuron.2008.09.006``

