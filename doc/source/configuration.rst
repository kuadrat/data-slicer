.. _sec-config:

The config directory
====================

You can customize a few things about PIT on your system by editing its
configuration directory.
You can find the location of this directory by issuing::

   pit.get_config_dir()

.. _sec-config-plugins:

Plugins
-------

Any python module that you put in the ``plugins/`` subdirectory will be found 
by PIT even if it is not part of the system PYTHONPATH.

Additionally, if you create a simple txt file called ``autoload.txt`` in 
which you list plugins (one per line), PIT will attempt to load all of them 
on startup.
