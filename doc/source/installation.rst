Installation
============

The installation of `data_slicer` has been tested on Linux, macOS and Windows.

The easiest way to install the package is to use 
`pip <https://pip.pypa.io/en/stable/>`_. Just type the following on a command 
line::

   pip install data_slicer

If the above does not appear to work, it might help to try installation from 
a virtual environment. 

Anaconda
--------

Detailed instructions for Anaconda users follow:

1) Open "Anaconda Prompt" 

2) In order not to mess up your dependencies (footnote 1), create a virtual 
   environment with python version 3.7.5::

      $ conda create --name testenv python==3.7.5
      [some output]
      $ conda activate testenv
      (testenv) $

3) Inside your virtual environment, run the following commands to download and 
   install data_slicer with all its dependencies (the first one is just to 
   upgrade pip to the latest version)::
   
      (testenv) $ pip install --upgrade pip
      (testenv) $ pip install data_slicer
   
   This will create a lot of console output. If everything succeeded, you should 
   see something like ``Successfully installed data_slicer`` towards the end.

4) Test the installation by starting up PIT::

      (testenv) $ pit
   
   This should bring up a window with some example data.

