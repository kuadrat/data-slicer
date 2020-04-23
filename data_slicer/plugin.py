class Plugin() :
    """ Base class for plugins. Other plugins should inherit this. """
    plugin_name = 'no name assigned'

    def __init__(self, main_window, data_handler) :
        self.main_window = main_window
        self.data_handler = data_handler
