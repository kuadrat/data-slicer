Accessing presented data
========================

Here follows a short overview on how to access some of the more useful data 
items represented in the different plots.
Please refer to the :ref:`graphical overview <sec-quickstart>` to understand 
which plot is being talked about.

.. note::
   Notice that accessing data in this way will *not* allow you to manipulate 
   the currently displayed data, i.e. you get a copy of whatever is currently 
   displayed and changes to this copy will not be reflected visually.  
   Only changes to the core data object (which is accessible through 
   ``pit.get_data()`` and settable through ``pit.set_data(...)``) and usage 
   of respective builtin functions (and likely functions from plugins) will be 
   visible.


Main and Cut Plot
-----------------

The currently displayed data of the *main plot* and *cut plot* can be 
accessed respectively by::

   pit.get_main_data()
   pit.get_cut_data()

or alternatively::

   mw.main_plot.image_data
   mw.cut_plot.image_data

Profiles
--------

The *horizontal* and *vertical profiles* as well as the *integrated 
intensity* profile can be accessed by::

   pit.get_hprofile()
   pit.get_vprofile()
   pit.get_iprofile()

.
