if __name__ == "__main__" :
    import logging

    from data_slicer import set_up_logging
    from data_slicer.utilities import TracedVariable

    tv = TracedVariable(value=5)

    tv.get_value()
    tv.set_value(8)
    tv.get_value()
