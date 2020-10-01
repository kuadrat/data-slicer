Quick start
===========

If you want to dive right in, just type ``pit`` from a command line.
The example data is loaded and you can familiarize yourself with the layout 
and the most basic functionality.

.. figure:: ../../screenshots/pit_overview.png
   :scale: 50 %
   :alt: Image not found.

   The main window of PIT.
   
   =  ==========================================================================
   a  main data plot
   b  cut plot
   c  vertical profile
   d  integrated z plot
   e  horizontal profile
   f  colorscale sliders
   g  interactive ipython console
   =  ==========================================================================

Main data plot and slice selection
----------------------------------

If you imagine your 3D dataset as a cube (*data cube*), the *main data plot* 
**(a)** would initially represent what you would see when looking at the cube 
from the top.
The horizontal **x** axis corresponds to the first dimension of your data 
cube, while the vertical **y** axis corresponds to the second.
The *integrated z plot* **(d)** shows the sum of each xy slice along the 
third **z** dimension.
You can drag the yellow slider to select a different slice to be displayed in 
the *main data plot*.
Additionally, using the **up** and **down arrow keys** (after having clicked in 
the *integrated z plot*) allows you to in- or decrease the integration range 
for the slice.
**Left** and **right arrow keys** move the slider step by step.


Creating arbitrary cuts
-----------------------

The yellow line inside the *main data plot* is called the *cutline*.
It is draggable as a whole and at the handles.
This is the knife that cuts through our data cube and the *cut plot* **(b)** 
shows what we see when we cut the data cube along the cutline.
Hitting the **r key** will re-initialize the cutline alternatingly at an 
angle of 0 or 90 degrees.
This is also useful if you happen to "lose" the cutline.

The *horizontal* and *vertical profiles* **(c)** and **(e)** just display the 
line profiles of the data shown in the *cut plot* along the cursor.


Colorscale sliders and the ipython console
------------------------------------------

The *colorscale sliders* **(f)** enable you to quickly change the min and max 
values of the colorscale as well as the exponent of the powerlaw 
normalization (*gamma*).

To change to used colormap, the *ipython console* **(g)** has to be used:
Type the command ``mw.set_cmap('CMAP_NAME')``.

