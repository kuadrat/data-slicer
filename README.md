# Data slicer

The `data-slicer` package offers fast tools for inspection, visualization, 
slicing and analysis of 3(+) dimensional datasets at a general level.
It also provides a framework and building blocks for users to easily create 
more specialized and customized tools for their individual use cases.

![](https://raw.githubusercontent.com/kuadrat/data_slicer/master/screenshots/pit_demo.gif)

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

## Contributing

If you are familiar with the workflow on github, feel free to go ahead and create a pull
request or open an issue.
If you are unsure of what that means but are willing to contribute, contact Kevin Kramer
via email: kevin.pasqual.kramer@protonmail.ch

### Plugins

If you have created a PIT plugin, feel free to add it to the list below, 
either via pull request or through an email (see above).

| Plugin Name (link) | Description | 
| ------------------ | ----------- |
| [ds-arpes-plugin](https://www.pluralsight.com/guides/working-tables-github-markdown) | tools for angle-resolved photoelectron spectroscopy (ARPES) | 

