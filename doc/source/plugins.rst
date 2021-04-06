.. _sec-plugin:

Plugins
=======

It is possible for people to write plugins that add additional functionality 
to PIT (see also :ref:`the plugin writing guide <sec-plugin-how-to>`).
A plugin for PIT is just a python module that connects to the backside of PIT.
This module should either be found by the python version you are running 
(i.e. you should be able to ``import`` it) or you can put it in your 
data-slicer :ref:`config directory <sec-config>`.

Loading plugins
---------------

If you have your plugin installed or ready in your config directory, you can 
load it from PIT by issuing::
   
   my_plugin = mw.load_plugin('PLUGIN_NAME')
   
Of course you can use any variable name in place of the example's 
``my_plugin``. ``PLUGIN_NAME`` should be the exact same thing you would 
write when you import the module using python's ``import`` statement.  

Autoloading plugins
-------------------

You can set it up such that your favourite plugins will always be loaded on 
startup of PIT.
See :ref:`here <sec-config-plugins>`.

.. _sec-plugin-list:

List of known plugins
---------------------

If you have created a PIT plugin, feel free to add it to the list below, 
either via pull request or through an e-mail 
(kevin.pasqual.kramer@protonmail.ch).

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Plugin Name (link) 
     - Description

   * - `ds-example-plugin <https://github.com/kuadrat/ds_example_plugin>`_
     - exists as a minimal example that can be used for guidance when 
       creating your own plugins. A step-by-step tutorial on how it was made 
       can be found :ref:`here <sec-plugin-how-to>`.

   * - `ds-arpes-plugin <https://github.com/kuadrat/ds_arpes_plugin>`_
     - tools for angle-resolved photoelectron spectroscopy (ARPES) data

