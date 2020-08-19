help_message = ''' 
Use python`s built-in help function to get help on this plugin`s functions, 
e.g.::

    help(<plugin_name>.<function_name>)

'''
class Plugin() :
    """ Base class for plugins. Other plugins should inherit this. """
    name = 'no plugin name assigned'
    shortname = None

    def __init__(self, main_window, data_handler) :
        # Connect the plugin to PIT
        self.main_window = main_window
        self.data_handler = data_handler

    def help(self) :
        """ Print a list of available functions and a help message to 
        standard output. 
        """
        # Create a list of this plugin's functions
        all_attributes = self.__dir__()
        functions = []
        for attribute in all_attributes :
            # Skip "hidden" attributes
            if attribute.startswith('_') : continue
            # Skip non-functions
            if not isinstance(self.__getattribute__(attribute), 
                              type(self.help)) : continue
            # Append to list of functions
            functions.append(attribute)
            
        print('Available functions:')
        for function in functions : print('   ', function)

        print(help_message)

