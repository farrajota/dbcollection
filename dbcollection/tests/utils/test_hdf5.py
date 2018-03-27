"""
Test the HDF5 metadata manager class.
"""


import os
import pytest

from dbcollection.utils.hdf5 import HDF5Manager


class TestHDF5Manager:
    """Unit tests for the HDF5Manager class."""

    def test_init_with_all_input_args(self, mocker):
        filename = '/some/path/filename.h5'

        hdf5_manager = HDF5Manager(filename)

        assert hdf5_manager.filename == filename

    def test_init__raises_error_no_input_args(self, mocker):
        with pytest.raises(TypeError):
            HDF5Manager()

    def test_init__raises_error_too_many_input_args(self, mocker):
        with pytest.raises(TypeError):
            HDF5Manager('/some/path/filename.h5', 'extra_field')
