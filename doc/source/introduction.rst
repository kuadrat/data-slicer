Introduction
============

The ``data-slicer`` package provides tools for quick visualization of 3 
dimensional datasets.
These tools are not intended to enable the creation of publication quality 
renderings, but rather to allow users to quickly inspect datasets in order to 
get an overview of the data and to quickly visualize the result of analytical 
operations on the data under study.
Examples where this package has been and could be employed included, but are 
not limited to:

   - medical or biological imaging techniques.

   - synchrotron based scattering and spectroscopic experiments, where 
     deciding on the course of the time-limited experiment often requires 
     preliminary analysis.

   - visualizing satellite imagery or georeferenced data.

Basically, ``data-slicer`` can be employed in all scientific, engineering, 
medical, artistic or other data driven disciplines where the use case of 

inspecting and slicing data (hyper)cubes arises.

At its core, the package contains the Python Image Tool, PIT for short, a 
simple but fast GUI to efficiently look at 3D data, slice it in various ways 
and employ data processings from the command line of an ``ipython`` console. 
While being set up to work in a general manner, specific processing and 
analysis routines for different fields can be integrated into PIT by means of 
a simple :ref:`plugin mechanism <sec-plugin>`.

Besides PIT, other widgets for 3D visualization are also available.
Thus, the package is intended to provide user bases in different fields with 
a means of easily creating customized tools for their data inspection and 
analysis routines.

