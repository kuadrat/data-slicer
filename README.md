![](https://raw.githubusercontent.com/kuadrat/data_slicer/master/img/02_Data_Slicer_Logo.png)

# Data slicer 
The `data-slicer` package offers fast tools for inspection, visualization, 
slicing and analysis of 3(+) dimensional datasets at a general level.
It also provides a framework and building blocks for users to easily create 
more specialized and customized tools for their individual use cases.

![](https://raw.githubusercontent.com/kuadrat/data_slicer/master/img/pit_demo.gif)

`data-slicer` was originally developed to deal with the high data throughput of 
modern measurement instruments, where quick visualizations and preliminary 
analyses are necessary to guide the direction of a measurement session.
However, the package is designed to be agnostic of the concrete use-case and 
all scientific, engineering, medical, artistic or other data driven 
disciplines where inspection and slicing of (hyper)cubes is required could 
potentially benefit from `data-slicer`.

## Documentation

This README just gives a minimal overview.
For more information, guides, examples and more, visit the documentation which is hosted 
by the friendly people over at ReadTheDocs.org:
https://data-slicer.readthedocs.io/en/latest/

## Installation

`data-slicer` should run on all platforms that support python and has been 
shown to run on Windows, macOS ans Linux.

The package can be installed from [PyPI](https://pypi.org/project/data-slicer/) 
using `pip install data_slicer`.
It is recommended to do this from within some sort of virtual environment.
Visit the documentation for more detailed instructions:
https://data-slicer.readthedocs.io/en/latest/installation.html

### Dependencies

This software is built upon on a number of other open-source frameworks.
The complete list of packages can be found in the file `requirements.txt`.
Most notably, this includes [matplotlib](https://matplotlib.org/), 
[numpy](https://numpy.org/) and 
[pyqtgraph](https://pyqtgraph.readthedocs.io/en/latest/).

## Citing

If you use `data-slicer` in your work, please credit it by citing the following publication:

[![DOI](https://joss.theoj.org/papers/10.21105/joss.02969/status.svg)](https://doi.org/10.21105/joss.02969)

Kramer et al., (2021). Visualization of Multi-Dimensional Data -- The data-slicer Package. Journal of Open Source Software, 6(60), 2969, https://doi.org/10.21105/joss.02969

## Contributing

You are welcome to help making this software package more useful!
You can do this by giving feedback, reporting bugs, issuing feature requests 
or fixing bugs and adding new features yourself. 
Furthermore, you can create and share your own plugins (refer to the 
[documentation](https://data-slicer.readthedocs.io/en/latest/)).

### Feedback, bugs and feature requests

The most straightforward and organized way to help improve this software is 
by opening an **issue** on [the github 
repository](https://github.com/kuadrat/data-slicer/issues).
To do this, navigate to the **Issues** tab and click **New issue**.
Please try to describe the bug you encountered or the new feature you would 
like to see as detailed as possible.
If you have several bugs/ideas please open a separate issue for each of them 
in order to keep the discussions focused.

If you have anything to tell me that does not seem to warrant opening an 
issue or you simply prefer to contact me directly you can do this via e-mail:
kevin.pasqual.kramer@protonmail.ch

### Contributing code

If you have fixed a bug or created a new feature in the source code yourself, 
it can be merged into this project.
Code contributions will be acknowledged in this README or, if the number of 
contributors grows too large, in a separate file.
If you are familiar with the workflow on github, please go ahead and create a 
pull request.
If you are unsure you can always contact me via e-mail (see above).

### Plugins

If you have created a PIT plugin, feel free to add it to the list below, 
either via pull request or through an e-mail (see above).
Also check the 
[documentation](https://data-slicer.readthedocs.io/en/latest/contributing.html) 
for a guide on how to create a plugin.

| Plugin Name (link) | Description | 
| ------------------ | ----------- |
| [ds-example-plugin](https://github.com/kuadrat/ds-example-plugin) | exists as a minimal example that can be used for guidance when creating your own plugins. A step-by-step tutorial on how it was made can be found in [the documentation](https://data-slicer.readthedocs.io/en/latest/contributing.html) |
| [ds-arpes-plugin](https://github.com/kuadrat/ds_arpes_plugin) | tools for angle-resolved photoelectron spectroscopy (ARPES) | 

