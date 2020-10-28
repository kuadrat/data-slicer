.. _sec-config:

The config directory
====================

You can customize a few things about PIT on your system by editing its
configuration directory.
You can find the location of this directory by issuing::

   pit.get_config_dir()

Colormaps
---------

In the ``cmaps`` subdirectory under your config dierectory (you can create it 
if it does not exist) you can put custom colormaps that will then be 
available to PIT.
Colormaps should be simple text files with three columns, representing RGB 
values (the scale doesn't matter), so it could look like this::

    0 0 0
    200 0 0
    400 0 0
    800 0 10
    [...]

The filename (everything before the first ``.`` that appears in the filename) 
will be the name under which you can find and load that colormap from within 
PIT.

.. _sec-config-plugins:

Plugins
-------

Any python module that you put in the ``plugins/`` subdirectory will be found 
by PIT even if it is not part of the system PYTHONPATH.

Additionally, if you create a simple txt file called ``autoload.txt`` in 
which you list plugins (one per line), PIT will attempt to load all of them 
on startup.
