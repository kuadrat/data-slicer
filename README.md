# Data slicer

A 3D data visualization tool.

![](https://raw.githubusercontent.com/kuadrat/arpys/master/screenshots/pit_demo.gif)

## Installation

The package can be installed from pypi using `pip install data_slicer`.
It is recommended to do this from within some sort of virtual environment.

Detailed instructions for Anaconda users follow:

1) Open "Anaconda Prompt" 

2) In order not to mess up your dependencies (footnote 1), create a virtual 
environment with python version 3.7.5
```
$ conda create --name testenv python==3.7.5
[some output]
$ conda activate testenv
(testenv) $
```

3) Inside your virtual environment, run the following command to download and 
install data_slicer with all its dependencies:
```
(testenv) $ pip install data_slicer
```
This will create a lot of console output. If everything succeeded, you should 
see something like `Successfully installed data_slicer` towards the end.

4) Test the installation by running a test script:
```
(testenv) $ python -m data_slicer.tests.cool_test
```
This should bring up a window with some example data.


## Documentatio

The documentation is hosted by the friendly people over at ReadTheDocs.org:
https://data-slicer.readthedocs.io/en/latest/

## Footnotes

(footnote 1) You most likely have many different python packages installed on 
your systems, like matplotlib, numpy, scipy, etc. These all have a specific 
version. Certain packages, however, depend on specific versions of other 
packages and may not work if you have the wrong version installed. Obviously, 
with many packages, this bears the potential of becoming very messy and 
complicated. That's the main reason virtual environments have been created. 
The idea is, to create an isolated environment of you python install, 
completely separate from your system installation or other virtual 
environments. The new environment comes without any additional packages 
(usually). So if you were to list your installed packages of your system 
install with the command `pip freeze` like this:
```
$ pip freeze
matplotlib==2.2.4
numpy==1.13.1
[...]
```
it would look like this, once you are "in" a newly created environment:
```
(env) $ pip freeze
[nothing]
```
.
Everything you install into this virtual environment only lives there, 
keeping your system installation "clean".
It is also possible to have varying python versions and more things, but 
that's the gist of it.


