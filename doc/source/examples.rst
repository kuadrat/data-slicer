Examples
========

A couple of simple examples can be run to showcase some of the widgets in the 
package.
These are found in the ``tests`` submodule and you can try them out using::

   python -m data-slicer.tests.XXX

where ``XXX`` is the name of the test to run (name of the file in the 
``tests`` submodule, without ``.py`` ending):

   - ``threedwidget``:
     A simple widget with xy, xz and yz planes that can be moved through the 
     data cube.

   - ``freeslice``:
     shows a widget where the data cube can be sliced along the xy plane but 
     also freely with a Cutline.

   - ``pit``:
     just starts PIT.

Check out the source files at ``/your/package/location/data_slicer/tests/`` 
or directly on the `github 
<https://github.com/kuadrat/data_slicer/tree/master/data_slicer/tests>`_ to 
see how these widgets can be used.

