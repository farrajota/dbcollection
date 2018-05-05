"""
Test the HDF5 metadata manager class.
"""


import os
import numpy as np
import pytest

from dbcollection.utils.hdf5 import HDF5Manager


@pytest.fixture()
def test_data():
    return {
        "filename": '/path/to/filename.h5'
    }


@pytest.fixture()
def mock_hdf5manager(mocker, test_data):
    mocker.patch.object(HDF5Manager, "open_file", return_value={'test_group': 'dummy_data'})
    return HDF5Manager(
        filename=test_data["filename"]
    )


class TestHDF5Manager:
    """Unit tests for the HDF5Manager class."""

    def test_init_with_all_input_args(self, mocker):
        mock_open = mocker.patch.object(HDF5Manager, "open_file", return_value={})
        filename = '/some/path/filename.h5'

        hdf5_manager = HDF5Manager(filename=filename)

        assert mock_open.called
        assert hdf5_manager.filename == filename

    def test_init__raises_error_no_input_args(self, mocker):
        with pytest.raises(TypeError):
            HDF5Manager()

    def test_init__raises_error_too_many_input_args(self, mocker):
        with pytest.raises(TypeError):
            HDF5Manager('/some/path/filename.h5', 'extra_field')

    def test_exists_group_and_group_exists(self, mocker, mock_hdf5manager):
        group = 'test_group'

        result = mock_hdf5manager.exists_group(group)

        assert result == True

    def test_exists_group_and_group_does_not_exist(self, mocker, mock_hdf5manager):
        group = 'invalid_group'

        result = mock_hdf5manager.exists_group(group)

        assert result == False

    def test_exists_group__raises_error_no_input_args(self, mocker, mock_hdf5manager):
        with pytest.raises(TypeError):
            mock_hdf5manager.exists_group()

    def test_add_field_to_group(self, mocker, mock_hdf5manager):
        mock_group = mocker.patch.object(HDF5Manager, "get_group", return_value=mocker.MagicMock())

        mock_hdf5manager.add_field_to_group(
            group='train',
            field='classes',
            data=np.random.rand(5,5),
            dtype=np.uint8,
            fillvalue=0,
            chunks=True,
            compression='gzip',
            compression_opts=4
        )

        assert mock_group.called

    def test_add_field_to_group__raises_error_no_input_args(self, mocker, mock_hdf5manager):
        with pytest.raises(TypeError):
            mock_hdf5manager.add_field_to_group()
