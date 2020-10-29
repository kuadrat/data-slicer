.. _sec-ipython-crash-course:

ipython crash course
====================

For a full tutorial on ipython, visit its `offcial documentation 
<https://ipython.readthedocs.io/en/stable/interactive/index.html>`_.
The pages here are just to point out the most useful features.

Basically, ipython is an improved python interpreter.
Just like in the usual python interpreter, you can execute any python code 
you want.
Code you enter can even span multiple lines, allowing you to define functions 
or classes::

   In [1]: print('Hello World.')
   Hello World.

   In [2]: def my_function(a) :
      ...:     return a**2
      ...:     

   In [3]: my_function(2)
   Out[3]: 4

One of the most useful features of ipython is the tab-completion: pressing 
Tab while writing some code in ipython will make the interpreter try to guess 
what you want to type and complete it.
If it isn't sure, it will present you with a list of options that can be 
scrolled through using Tab or the arrow keys.
Try the following as an example (everything after the ``#`` should not be 
typed, but understood as a comment)::

   In [1]: my_long_variable = 3.14

   In [2]: my # press Tab now and it will complete to `my_long_variable`
   Out[2]: 3.14

   In [3]: my_other_long_variable = 2.72
   
   In [4]: my # press Tab now and you will be presented with a list 
              # containing `my_long_variable` and `my_other_long_variable`

This is not just convenient to save some typing, but even more importantly, 
it helps you check what options you have.
In PIT, you might forget the names of different functions.
In such a situation you could use Tab to get a list of all functions on the 
fly::

   In [1]: pit. # press Tab and you will get a list of all functions the 
                # ``pit`` object offers

You are able to do that with any python object, and even with filenames (e.g. 
when you're doing a ``pit.open('...')``).

Another useful features are the ipython *magic* commands::

   In [1]: %run my_script.py # This runs the file `my_script.py`, if it is in 
                             # the current working directory. All the 
                             # variables and objects created in that script 
                             # will afterwards be available to you in the 
                             # ipython session
   Out[1]: ...

   In [2]: %load my_script.py # This will load the contents of `my_script.py` 
                              # into the interpreter, as if you had typed it 
                              # in by hand. This would allow you to review 
                              # and makes changes to the code before running them.

Do not forget the existence of python's built in ``help()`` function, to 
quickly get reminded of how a function should be used without having to search online.

This should sum up the most useful features for the purposes of using PIT.
Again, for more details on ipython, visit `the offcial documentation 
<https://ipython.readthedocs.io/en/stable/interactive/index.html>`_.

