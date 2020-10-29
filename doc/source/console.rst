.. _sec-console:

Using the console
=================

An essential part of PIT is the console.
This is just a regular `ipython console <https://ipython.org/>`_ which allows 
you, in principle, to do anything you could imagine doing with python:
set and use variables, define and run functions, run scripts, use matplotlib 
to create plots, etc.
Check out the :ref:`ipython crash course <sec-ipython-crash-course>` if you 
are unfamiliar with ipython (or python).

Importantly, all the visible objects and the underlying data structures can 
be accessed through the console.
There are two objects through which this access is provided: ``pit`` and ``mw``.

``mw`` is short for *main window* and contains all the visible elements, e.g. 
the different plots (``mw.main_plot``, ``mw.cut_plot``, ``mw.x_plot``, 
``mw.y_plot``, etc.)
The colormap setting is also handled through ``mw``, through 
:func:`mw.set_cmap() <data_slicer.pit.MainWindow.set_cmap>`.

``pit`` is an instance of :class:`~data_slicer.pit.PITDataHandler` and is 
responsible for keeping all the visible and invisible data elements consistent.
Use it to load data in (:func:`pit.open() <data_slicer.pit.PITDataHandler>`), 
change the orientation in which we look at the data (:func:`pit.roll_axes() 
<data_slicer.pit.PITDataHandler.roll_axes`).
Here's an incomplete list of some of the more useful functions of the ``pit`` 
object:

   - **data access**

     Confer :ref:`sec-access` for details on how to access various data 
     elements.

   - :func:`pit.reset_data() <data_slicer.pit.PITDataHandler.reset_data>`

      Reset everything back to the state just after loading the data in.

   - :func:`pit.lineplot() <data_slicer.pit.PITDataHandler.lineplot>`

     Create a matplotlib figure that shows the data as a series of lines.

   - :func:`pit.plot_all_slices() 
     <data_slicer.pit.PITDataHandler.plot_all_slices>`

     Show equidistantly spaced slices along z in matplotlib figures.

   - :func:`pit.overlay_model() <data_slicer.pit.PITDataHandler.overlay_model>`
    
     Supply a function of the two variables (x and y axes of the *main plot* 
     and display it in the *main* and *cut plots*.

   - :func:`pit.remove_model() <data_slicer.pit.PITDataHandler.remove_model>`
     
     Remove the lines from above command.

