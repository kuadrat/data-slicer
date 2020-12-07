---
title: Visualization of Multi-Dimensional Data -- The data-slicer package
bibliography: paper.bib
tags:
  - python
  - visualization
authors:
  - name: Kevin Kramer
    orcid:
    affiliation: 1
  - name: Johan Chang
    affiliation: 1
affiliations:
  - name: Physik Institut, Universität Zürich, Winterthurerstrasse 190, CH-8057 Zürich, Switzerland
    index: 1
---

# Statement of Need

From prehistoric cave-wall paintings to the invention of print and most 
recently electronic hard-disks, human data storage capacity has evolved 
tremendously.
Information/data is of great value and hence associated with innovation and 
technological progress.
This is especially true in analytical disciplines i.e. all sciences ranging 
from physics to psychology and medicine.
In observational sciences, most measurement techniques undergo steady 
improvements in acquisition time and resolution.
As a result the sheer data throughput is continually increasing.
More data is always welcome.
However, in many disciples human digestion of this large amount of data has 
now become the bottleneck.
It is often said that a picture is worth more than 1000 words.
This saying reflects that our visual information intake is highly developed.
Fast visualization is therefore important for quick digestion of large 
datasets.

![Evolution of data acquisition in the field of spectroscopy. 
  (a,b) Angular photoemission electron spectroscopy 
  (ARPES) [@wells92evidence,@shai13quasiparticle], 
  (c,d) tunnelling spectroscopy (STS) [@giaever62tunneling,@zhang19machine] 
  and (e,f) inelastic neutron scattering 
  (INS) [@woods60lattice,@Wan_2020,Bastien] 
  spectroscopy techniques all started with single spectrum collection 
  (top row). 
  Modern spectroscopic and scattering techniques, however, involve 
  multidimensional data acquisition (bottom row). 
  \label{fig1}
](fig1.pdf)

# Summary

data-slicer is a python package that contains several functions and classes which 
provide modular Qt [@company00qt,@00riverbank] widgets, tools and 
utilities for the visualization of three-dimensional (3D) datasets.
These building blocks can be combined freely to create new applications.
Some of these building blocks are used within the package to form a 
graphical user interface (GUI) for 3D data visualization and manipulation: 
the Python Image Tool (PIT).

## PIT
PIT consists of a number of dynamic plot figures which allow browsing through 
3D data by quickly selecting slices of variable thickness from the data cube 
and further cutting them up arbitrarily.
Besides the different plot windows, there are two core features of PIT that 
should be explicitly mentioned.
The first is the ability to create slices of the 3D data cube along arbitrary 
angles quickly.
This is facilitated on the GUI side through a simple draggable line to select 
the slice direction and behind the scenes by the use of optimized functions 
which enable the superior speed of this operation.
The second feature worth mentioning is the inclusion of an ipython console 
which is aware of the loaded data as well as of all GUI elements.
The console immediately enables users to run any analysis routine suitable to 
their respective needs.
This includes running python commands live, in a workflow familiar to 
pylab or Jupyter [@00jupyter] notebook users but 
also loading or directly running scripts into or from the console, using 
ipython's line magic functions \texttt{\%load} and \texttt{\%run} respectively.
Effectively, this design is central in empowering users to do anything they 
want --- as long as it is possible to accomplish with python.

## Plugins
It is clear that it can get complicated and tedious to run certain types of 
data processing or analysis from the ipython console, as described in the 
previous paragraph.
For such cases, PIT provides an additional level of customizability and 
control through its plugin system.
Plugins are regular python packages that can be loaded from within PIT and 
enhance it with new functionality.
A plugin can interact with all elements in PIT via the same interfaces as can 
be done through the built-in ipython console.
Creating a plugin therefore requires little programming skills and no further 
knowledge of the inner workings of PIT.
In this manner, different communities of users can create and share their 
field-specific plugins which allow them to customize PIT to their needs.

As an example, we mention the ds-arpes-plugin, which provides 
basic functionalities for loading of ARPES datasets and handles for typical 
analysis functions, customized and taylored to be used from within PIT.

## Modularity and widgets

PIT is constructed in a modular fashion, constituting of different widgets 
that have been combined together to make a useful, ready to use tool.
However, different applications may require slightly different 
functionalities, and the setup in PIT may not be optimal.
The data-slicer package makes all the used widgets in PIT and some additional ones 
independently available to the user.
These widgets can be arbitrarily combined to create customized applications 
in a relatively simple manner.

In summary, the data-slicer package solves the problem of scope discussed in 
section 
\ref{sec:intro} by offering a variety of methods for users of varying 
backgrounds to get exactly the tools they need.
On the first and most general level, PIT offers a ready-to-use GUI for quick 
3D data visualization without any need of programmatic user input.
Users can satisfy their more specific needs either through use of the console 
or by implementing a plugin, which can both be accomplished with little 
programming knowledge.
On the last, most specific level users can use and arrange the building 
blocks contained in the package to create completely new applications or 
embed PIT or other parts of the data-slicer package into an existing application.

# Acknowledgements

We are thankful for fruitful discussions with and inputs from Titus Neupert, 
Claude Monney, Daniel Mazzone, Nicholas Plumb, Wojciech Pude\l{}ko as well as 
for the testing efforts of Qisi Wang, Julia Küspert and Karin von Arx.

Kevin Kramer and Johan Chang acknowledge support by the Swiss National 
Science Foundation.

# References
