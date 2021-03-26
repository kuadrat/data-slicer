.. _sec-widgets:

Widgets
=======

The widgets shipped with ``data-slicer`` can be re-combined to create new 
applications.
In order to do this, a certain level of familiarity with widget-based GUI 
creation is required and some knowledge or experience with `Qt 
<https://www.qt.io/>`_ or `PyQt <https://wiki.python.org/moin/PyQt>`_ is 
recommended.
Nevertheless, even without said experience, the `step-by-step 
<sec-widget-tutorial>`_ tutorial below may help you figure out how to do such 
things.

List of available widgets
-------------------------

.. list-table:: 
   :header-rows: 0
   :widths: 40 60

   * - :class:`data_slicer.imageplot.ImagePlot`
     - A pseudocolor plot of a 2D dataset, similar to :class:`matplotlib 
       pcolormesh <matplotlib.pyplot.pcolormesh>`.

   * - :class:`data_slicer.imageplot.CrosshairImagePlot`
     - An :class:`~data_slicer.imageplot.ImagePlot` with a draggable crosshair.

   * - :class:`data_slicer.imageplot.CursorPlot`
     - A regular data plot with a draggable line (cursor).

   * - :class:`data_slicer.imageplot.Scalebar`
     - A draggable scalebar. 

   * - :class:`data_slicer.cutline.Cutline`
     - A line that can be dragged on both ends and added to a
       :class:`pyqtgraph.PlotWidget` to create arbitrary cuts.  

   * - :class:`data_slicer.pit.MainWindow`
     - The full main window of PIT, itself consisting of widgets from this 
       list.  

   * - :class:`data_slicer.widgets.ColorSliders`
     - Gamma and vmax color sliders. Essentially just a pair of 
       :class:`~data_slicer.imageplot.Scalebar` objects.

   * - :class:`data_slicer.widgets.ThreeDWidget`
     - A widget that allows showing xy-slices out of a 3D dataset as a plane in 
       3D.

   * - :class:`data_slicer.widgets.ThreeDSliceWidget`
     - Subclass of :class:`~data_slicer.widgets.ThreeDWidget` that shows the 
       xz- and yz-planes in addition to the xy plane.

   * - :class:`data_slicer.widgets.FreeSliceWidget`
     - Subclass of :class:`~data_slicer.widgets.ThreeDWidget` that makes use 
       of a :class:`~data_slicer.cutline.Cutline` on an 
       :class:`~data_slicer.imageplot.ImagePlot` to allow creating arbitrary 
       slice-planes.

.. _sec-widget-tutorial:

Example
-------

In the following we will go through the creation of a simple App that uses a 
:class:`~data_slicer.widgets.ThreeDSliceWidget` to display some data that can 
be loaded when clicking a **Load** button.

Step 1: Just a plain ThreeDSliceWidget
......................................

First, we take a look at what we would need to do in order to just create a 
:class:`~data_slicer.widgets.ThreeDSliceWidget` without anything else.

.. literalinclude:: ../examples/example_step1.py
   :linenos:

This should create a window with a 
:class:`~data_slicer.widgets.ThreeDSliceWidget` - but there is no data 
present inside the widget yet.

Step 2: Adding a Load button
............................

In order to add a button, we need to change the structure of our application 
a little bit.
Since we need to be able to let Qt know where our different GUI elements 
should appear, we are going to work with a :class:`~Qt.QtGui.QGridLayout`.
We then add a :class:`~Qt.QtGui.QPushButton` and the 
:class:`~data_slcier.widgets.ThreeDSliceWidget` from before to the layout.
In the following code snippets, all new lines are preceded by a comment ``# 
NEW``.

.. literalinclude:: ../examples/example_step2.py
   :linenos:

We now have a button above the :class:`~data_slcier.widgets.ThreeDSliceWidget`!
However, clicking the button does not do anything yet... Let's change that in 
the next step.

Step 3: Making the button do something
......................................

We can define what happens when the button is clicked by *connecting* a 
function to it::

   load_button.clicked.connect(my_function)

For ``my_function`` we could put any ``python`` callable, for example::

   def my_function() :
      print('Button clicked!;)

Try defining ``my_function`` like this **before** connecting it to the button 
and running the example again.
You should now get the message ``Button clicked!`` on the console  whenever 
you click the button.

This is not yet what we want though.
We would like the click on the **Load** button to open a file selection 
dialog from which we can navigate to a data file, select it and that is then 
going to be loaded into the :class:`~data_slicer.widgets.ThreeDSliceWidget`.
This can be achieved with the following function::

   def load_data() :
       # Open the file selection dialog and store the selected file as *fname*
       fname = QtGui.QFileDialog.getOpenFileName(layout_widget, 'Select file')
       print(fname[0])
       
       # Load the selected data into the ThreeDSliceWidget
       D = dataloading.load_data(fname[0])
       widget.set_data(D.data)

Don't forget to ``from data_slicer import dataloading`` at the start of the 
file and to connect this function to our **Load** button.

The full example code at this stage should look like this:

.. literalinclude:: ../examples/example_step3.py
   :linenos:

Conclusion
..........

While we have seen how to use the provided widgets in other contexts to 
create new applications, it is obvious that a lot could be improved and 
tinkered with in our little example.
One could include some :class:`~data_slicer.widgets.ColorSliders` and link 
them up to the :class:`~data_slicer.widgets.ThreeDSliceWidget` s colormap to 
adjust the colors.
Or one could implement a different way of loading the data that is not 
limited to the formats supported by :mod:`data_slicer.dataloading`, add 
error handling when specifying unsupported formats, add more widgets that 
show the data from different viewpoints, and so much more (don't even get me 
started on brushing up the layout and *look and feel*).

For further inspiration it is recommended to check out the source coudes of 
the tests, located under the ``tests`` directory in your ``data_slicer`` 
installation or on `the github 
<https://github.com/kuadrat/data-slicer/tree/master/data_slicer/tests>`_.
Additionally, a lot can be achieved when combining functionalities from 
`pyqtgraph <https://pyqtgraph.readthedocs.io/en/latest/>`_.
Check out the rich set of examples they provide by::

   python -m pyqtgraph.examples
