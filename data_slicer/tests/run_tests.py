if __name__ == "__main__" :
    import pytest
    import pkg_resources

    test_path = pkg_resources.resource_filename('data_slicer', 'tests/')
    pytest.main([test_path])

