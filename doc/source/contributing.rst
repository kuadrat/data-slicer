.. _sec-contributing:

Contributing
============

Thank you for helping to make this software package more useful!
There are several ways in which you can contribute: giving feedback, 
reporting bugs, issuing feature requests or fixing bugs and adding new 
features yourself. 
Furthermore, you can create and share your own :ref:`plugins <sec-plugin>`.

Feedback, bugs and feature requests
-----------------------------------

The most straightforward and organized way to help improve this software is 
by opening an **issue** on `the github 
repository <https://github.com/kuadrat/data-slicer/issues>`_.
To do this, navigate to the **Issues** tab and click **New issue**.
Please try to describe the bug you encountered or the new feature you would 
like to see as detailed as possible.
If you have several bugs/ideas please open a separate issue for each of them 
in order to keep the discussions focused.

If you have anything to tell me that does not seem to warrant opening an 
issue or you simply prefer to contact me directly you can do this via e-mail:
kevin.pasqual.kramer@protonmail.ch

Contributing code
-----------------

If you have fixed a bug or created a new feature in the source code yourself, 
it can be merged into this project.
Code contributions will be acknowledged in the README or, if the number of 
contributors grows too large, in a separate file.
If you are familiar with the workflow on github, please go ahead and create a 
pull request.
If you are unsure you can always contact me via e-mail (see above).

Plugins
-------

If you have created a PIT plugin, feel free to add it to the list on the 
:ref:`plugins page <sec-plugin>`, either via pull request or through an 
e-mail (see above).

.. _sec-plugin-how-to:

Creating a plugin
.................

Creating a plugin is not difficult, but there are a few details that one 
needs to get right in order for things to work.
The package `ds-example-plugin <https://github.com/kuadrat/ds-example-plugin>`_
was made to serve as an example to showcase how a plugin can be created.
This section gives a step-by-step guide on how ``ds-example-plugin`` was 
built and should allow you to figure out how to create your own plugins by 
analogy.
It is helpful to be familiar with the concept of object oriented 
programming (working with classes and inheritance), but not mandatory.

Before we start, let's have a look at what the example plugin does.
You can either install it using ``pip install ds-example-plugin`` or download 
the source code from github and save it (or a link to it) in the ``plugins`` 
subdirectory of your :ref:`config directory <sec-config>`.
Once downloaded and installed, start PIT and load the plugin::

   [1] example = mw.load_plugin('ds_example_plugin')
   Importing plugin ds_example_plugin (Example plugin).
   
Running ``example.help()`` then gives us a list of available functions. 
There are just two (besides the ``help`` function).
Let's try them both::

   [2] example.example_function()
   This message is sent to you by the Example plugin.

   [3] example.blur()

The first one doesn't do anything but print some text to the console.
The second one blurs the data.
It can also be called with a numeric argument to specify the *amount* of 
blurring.
Since the blurring is applied directly to the data, it can only be undone by 
using ``pit.reset_data()``.

That's really all this plugin does.
Now let's see how it is implemented.
In the following, we refer to the source code files that are found `on the 
github <https://github.com/kuadrat/ds-example-plugin>`_.

Step 1: Writing the Plugin class
********************************

The file ``ds_example_plugin.py`` contains the core of our plugin.
Essentially, we define a ``class`` that inherits from 
:class:`data_slicer.plugin.Plugin`::

   from data_slicer import plugin

   class Example_Plugin(plugin.Plugin) :
      [...]

The ``__init__()`` method of this class **must** call the superclass' 
``__init__()`` through the line::

   def __init__(self, *args, **kwargs) :
      [...]
      super().__init__(*args, **kwargs)
      [...]

It is recommended that you give your plugin a ``name`` and ``shortname`` by 
setting the respective attributes in the ``__init__()`` function::

   def __init__(self, *args, **kwargs) :
      [...]
      self.name = 'Example plugin'
      self.shortname = 'example'

Of course you can add any kind of code you need to in the ``__init__()`` 
function.
But to summarize, the bare requirements that absolutely need to be fulfilled 
for a plugin to work are:

   1. Inheriting from :class:`data_slicer.plugin.Plugin`.

   2. Calling the superclass' constructor with ``super().__init__(...)``

Step 2: Adding functionality to the plugin class
************************************************

We can now add functions to this class.
As a first example, let's have a look at ``example_function``::

   def example_function(self) :
      """ [...] """
      print([...])

The function is defined like any python function, but as a class function it 
**must** contain the argument ``self``.

The *doc string* (everything that appears between the ``"""`` directly after 
the function name) will be visible to the user when they use the built-in 
``help()`` function, so it's a good idea to explain as clearly as possible 
what the function does and how to use it properly.

As we have seen, this function is later available to the user through 
``example.example_function()`` and it will also be listed by ``example.help()``.

However, this ``example_function()`` doesn't actually do anything useful and 
related to PIT, so let's have a look at ``blur()`` instead, where we see how 
PIT's data and other elements can be accessed::

   # Add to the imports on top
   from scipy.ndimage import gaussian_filter

   [...]

   # Inside the class definition
      def blur(self, sigma=1) :
         """ [...] """
         data = self.data_handler.get_data()
         self.data_handler.set_data(gaussian_filter(data, sigma))

We see again how the argument ``self`` needs to appear first.
After it, arbitrary positional and keyword argument can follow, as usual with 
python functions.

In the first line of the function definition we see that we can get access to 
the data through ``self.data_handler.get_data()``.
``data_handler`` is available to us thanks to inheriting from 
:class:`data_slicer.plugin.Plugin` and is the same as ``pit`` which is 
available from the ipython console, i.e. it is a 
:class:`data_slicer.pit.PITDataHandler` object.
Similarly, within our class definition we also have access to a 
:class:`data_slicer.pit.MainWindow` object through ``self.main_window``.
It is through these two objects that we can access all the data and visual 
elements of PIT.
Check out their respective documentations to see what functions they provide, 
but the ones that are likely most useful are 
:meth:`self.data_handler.get_data() <data_slicer.pit.PITDataHandler.get_data>`,
:meth:`self.data_handler.set_data() <data_slicer.pit.PITDataHandler.set_data>`
and :meth:`self.data_handler.overlay_model() 
<data_slicer.pit.PITDataHandler.overlay_model>`.

So to summarize step 2, we can add arbitrary functionality to our plugin by 
defining functions.
By means of ``self.data_handler`` and ``self.main_window`` we get access to 
elements of PIT, meaning we can read and change them.
Every function we define will be directly available to the user and gets 
automatically listed by the plugin's ``help()`` function.

Step 3: Creating the module structure
*************************************

PIT loads plugins by using python's ``import`` capabilities to import the 
plugin class we created in steps 1 and 2.
For this to work, python needs to recognize our code as a module.
To be recognized as a module, we simply need to have a file called 
``__init__.py`` in the same directory as our code.
For python it is enough for this file to exist, even if it is empty.
However, if you look at the ``__init__.py`` in the code of 
``ds-example-plugin`` you'll find that it does contain one line of code::

   from ds_example_plugin.ds_example_plugin import Example_Plugin as main

This line is necessary for PIT's plugin mechanism to work.
It simply imports the class we defined in steps 1 and 2 under the alias 
``main``.

Let's have a closer look at the structure of this line, which can be stripped 
down to consist of four parts::

   from <1>.<2> import <3> as <4>

When loading the plugin, PIT will look for a class called ``main`` and 
instantiate it - this means that when you write your plugin, the last word in 
this line (``<4>``) always has to be ``main``.

Part ``<3>`` must match the name of the class from earlier and part ``<2>`` 
is the exact name of the file (minus the ``.py`` suffix) that contains said 
class definition.
Finally, part ``<1>`` is the exact name of the directory that contains both 
the ``__init__.py`` file and the file ``<2>``.
``<1>`` is also the name that will have to be used to load the plugin from 
within PIT with ``mw.load_plugin(<1>)``.
``<1>`` and ``<2>`` don't necessarily have to be the same, but it is quite 
customary to use the same name here.

In summary, in this step we created the file ``__init__.py`` that contains 
just a very specific line of code.

Final step: make the plugin available
*************************************

In order for PIT to find your plugin, it has to

   - either be detectable by python

   - or be placed in your :ref:`config directory <sec-config>`.

To be detectable by python, you have to place the directory containing the 
plugin file and the ``__init__.py`` file (directory with name ``<1>`` from 
above) somewhere in your PYTHONPATH.
If you're just using a plugin for personal use, it is probably easiest to 
simply place it in your config directory.
Don't forget that you have the option of letting PIT :ref:`automatically load 
plugins <sec-config-plugins>`, using the ``autoload.txt`` file.

If you want to share your plugin with other people, it is enough to make the 
source code available by any means.
Other users can then just download the code and place it in their config 
directories to make use of the plugin.
However, if you know how to properly package a python module, you could do 
that and make it available on PyPI, such that users can simply install the 
plugin by getting it with ``pip``.
This would have the advantage that it will make it easier for users to get 
updated versions of the plugin.
A tutorial on packaging would, however, go beyond the scope of this tutorial.

Don't forget to contact me if you have created and shared a plugin, such that 
I can add it to the :ref:`list of available plugins <sec-plugin-list>`!

