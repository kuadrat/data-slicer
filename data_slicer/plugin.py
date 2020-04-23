class Plugin() :
    """ Base class for plugins. Other plugins should inherit this. """
    name = 'no name assigned'
    shortname = None

    def __init__(self, main_window, data_handler) :
        self.main_window = main_window
        self.data_handler = data_handler
