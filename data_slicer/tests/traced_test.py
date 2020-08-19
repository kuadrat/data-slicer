if __name__ == "__main__" :
    import logging

    from data_slicer.utilities import TracedVariable

    from data_slicer import set_up_logging

    print('Initializing TracedVariable')
    tv1 = TracedVariable(5, name='tv1')

    print('Setting value')
    tv1.set_value(3)

    print('Reading value')
    foo = tv1.get_value()

    print('Initializing second TracedVariable')
    tv2 = TracedVariable(5, name='tv2')

    print('Setting value')
    tv2.set_value(3)

    print('Reading value')
    foo = tv2.get_value()
