"""
Test the base classes for managing datasets and tasks.
"""


import os
import pytest
import numpy as np

from dbcollection.datasets import BaseDatasetNew, BaseTaskNew


@pytest.fixture()
def test_data():
    return {
        "data_path": '/path/to/data',
        "cache_path": '/path/to/cache',
        "extract_data": True,
        "verbose": True
    }


@pytest.fixture()
def mock_dataset_class(test_data):
    return BaseDatasetNew(
        data_path=test_data["data_path"],
        cache_path=test_data["cache_path"],
        extract_data=test_data["extract_data"],
        verbose=test_data["verbose"]
    )


class TestBaseDatasetNew:
    """Unit tests for the BaseDatasetNew class."""

    def test_init_with_all_input_args(self, mocker):
        data_path = '/path/to/data'
        cache_path = '/path/to/cache'
        extract_data=True
        verbose=True

        db_manager = BaseDatasetNew(
            data_path=data_path,
            cache_path=cache_path,
            extract_data=extract_data,
            verbose=verbose
        )

        assert db_manager.data_path == '/path/to/data'
        assert db_manager.cache_path == '/path/to/cache'
        assert db_manager.extract_data == True
        assert db_manager.verbose == True
        assert db_manager.urls == ()
        assert db_manager.keywords == ()
        assert db_manager.tasks == {}
        assert db_manager.default_task == ''

    def test_init_without_optional_input_args(self, mocker):
        data_path = '/path/to/data'
        cache_path = '/path/to/cache'

        db_manager = BaseDatasetNew(
            data_path=data_path,
            cache_path=cache_path
        )

        assert db_manager.data_path == '/path/to/data'
        assert db_manager.cache_path == '/path/to/cache'
        assert db_manager.extract_data == True
        assert db_manager.verbose == True
        assert db_manager.urls == ()
        assert db_manager.keywords == ()
        assert db_manager.tasks == {}
        assert db_manager.default_task == ''

    def test_init__raises_error_no_input_args(self, mocker):
        with pytest.raises(TypeError):
            BaseDatasetNew()

    def test_init__raises_error_too_many_input_args(self, mocker):
        with pytest.raises(TypeError):
            BaseDatasetNew('/path/to/data', '/path/to/cache', False, False, 'extra_field')

    def test_download(self, mocker, mock_dataset_class):
        mock_download_extract = mocker.patch("dbcollection.datasets.download_extract_all")

        mock_dataset_class.download()

        assert mock_download_extract.called_once_with(
            urls=mock_dataset_class.urls,
            dir_save=mock_dataset_class.data_path,
            extract_data=mock_dataset_class.extract_data,
            verbose=mock_dataset_class.verbose
        )

    def test_process(self, mocker, mock_dataset_class):
        mock_parse_task = mocker.patch.object(BaseDatasetNew, "parse_task_name", return_value='taskA')
        mock_process_metadata = mocker.patch.object(BaseDatasetNew, "process_metadata", return_value='/path/to/task/filename.h5')

        result = mock_dataset_class.process('taskA')

        assert mock_parse_task.called
        assert mock_process_metadata.called
        assert result == {'taskA': {"filename": '/path/to/task/filename.h5', "categories": ()}}

    def test_parse_task_name_with_valid_task_name(self, mocker, mock_dataset_class):
        task = 'taskA'

        result = mock_dataset_class.parse_task_name(task)

        assert result == 'taskA'

    def test_parse_task_name_with_empty_task_name(self, mocker, mock_dataset_class):
        task = ''

        mock_dataset_class.default_task = 'some_task'
        result = mock_dataset_class.parse_task_name(task)

        assert result == 'some_task'

    def test_parse_task_name_with_default_task_name(self, mocker, mock_dataset_class):
        task = 'default'

        mock_dataset_class.default_task = 'some_task'
        result = mock_dataset_class.parse_task_name(task)

        assert result == 'some_task'

    def test_process_metadata(self, mocker, mock_dataset_class):
        mock_get_constructor = mocker.patch.object(BaseDatasetNew, "get_task_constructor", return_value=mocker.MagicMock())

        mock_dataset_class.process_metadata('some_task')

        assert mock_get_constructor.called

    def test_get_task_constructor(self, mocker, mock_dataset_class):
        task = 'taskZ'

        mock_dataset_class.tasks = {task: 'some_data'}
        result = mock_dataset_class.get_task_constructor(task)

        assert result == 'some_data'


@pytest.fixture()
def mock_task_class(test_data):
    return BaseTaskNew(
        data_path=test_data["data_path"],
        cache_path=test_data["cache_path"],
        verbose=test_data["verbose"]
    )


class TestBaseTaskNew:
    """Unit tests for the BaseTaskNew class."""

    def test_init_with_all_input_args(self, mocker):
        mock_get_filename = mocker.patch.object(BaseTaskNew, "get_hdf5_save_filename", return_value='/path/to/hdf5/file.h5')
        data_path = '/path/to/data'
        cache_path = '/path/to/cache'
        verbose = True

        task_manager = BaseTaskNew(data_path=data_path,
                                cache_path=cache_path,
                                verbose=verbose)

        assert mock_get_filename.called
        assert task_manager.data_path == '/path/to/data'
        assert task_manager.cache_path == '/path/to/cache'
        assert task_manager.verbose == True
        assert task_manager.hdf5_filepath == '/path/to/hdf5/file.h5'
        assert task_manager.filename_h5 == ''
        assert task_manager.hdf5_manager == None

    def test_init_without_optional_input_args(self, mocker):
        mock_get_filename = mocker.patch.object(BaseTaskNew, "get_hdf5_save_filename", return_value='/path/to/hdf5/file.h5')
        data_path = '/path/to/data'
        cache_path = '/path/to/cache'

        task_manager = BaseTaskNew(data_path=data_path,
                                cache_path=cache_path)

        assert mock_get_filename.called
        assert task_manager.data_path == '/path/to/data'
        assert task_manager.cache_path == '/path/to/cache'
        assert task_manager.verbose == True
        assert task_manager.hdf5_filepath == '/path/to/hdf5/file.h5'
        assert task_manager.filename_h5 == ''
        assert task_manager.hdf5_manager == None

    def test_init__raises_error_no_input_args(self, mocker):
        with pytest.raises(TypeError):
            BaseTaskNew()

    def test_init__raises_error_too_many_input_args(self, mocker):
        with pytest.raises(TypeError):
            BaseTaskNew('/path/to/data', '/path/to/cache', False, 'extra_input')

    def test_get_hdf5_save_filename(self, mocker, mock_task_class):
        mock_task_class.filename_h5 = 'classification'

        filepath = mock_task_class.get_hdf5_save_filename()

        assert filepath == os.path.join('/path/to/cache', 'classification.h5')

    def test_run(self, mocker, mock_task_class):
        mock_setup_manager = mocker.patch.object(BaseTaskNew, "setup_hdf5_manager")
        mock_load_data = mocker.patch.object(BaseTaskNew, "load_data", return_value={})
        mock_process = mocker.patch.object(BaseTaskNew, "process_metadata")
        mock_teardown_manager = mocker.patch.object(BaseTaskNew, "teardown_hdf5_manager")

        filename = mock_task_class.run()

        assert mock_setup_manager.called
        assert mock_load_data.called
        assert mock_process.called
        assert mock_teardown_manager.called
        assert filename == mock_task_class.hdf5_filepath

    def test_load_data(self, mocker, mock_task_class):
        mock_task_class.load_data()

    def test_process_metadata(self, mocker, mock_task_class):
        mock_process_metadata = mocker.patch.object(BaseTaskNew, "process_set_metadata")

        def sample_generator():
            yield {'train': ['dummy', 'data']}
            yield {'test': ['dummy', 'data']}
        generator = sample_generator()

        mock_task_class.process_metadata(generator)

        assert mock_process_metadata.called

    def test_hdf5_create_group(self, mocker, mock_task_class):
        pass  # Todo

    def test_save_field_to_hdf5(self, mocker, mock_task_class):
        mock_add_field = mocker.Mock()
        mock_task_class.hdf5_manager = mock_add_field

        group = 'train'
        field = 'fieldA'
        data = np.array(range(10))
        mock_task_class.save_field_to_hdf5(group, field, data)

        mock_add_field.add_field_to_group.assert_called_once_with(
            group='train',
            field='fieldA',
            data=data
        )

    def test_save_field_to_hdf5_all_args(self, mocker, mock_task_class):
        mock_add_field = mocker.Mock()
        mock_task_class.hdf5_manager = mock_add_field

        data = np.array(range(10))
        mock_task_class.save_field_to_hdf5(
            set_name='train',
            field='fieldA',
            data=data,
            dtype=np.uint8,
            fillvalue=0,
            chunks=True,
            compression="gzip",
            compression_opts=4)

        mock_add_field.add_field_to_group.assert_called_once_with(
            group='train',
            field='fieldA',
            data=data,
            dtype=np.uint8,
            fillvalue=0,
            chunks=True,
            compression="gzip",
            compression_opts=4
        )

    def test_teardown_hdf5_manager(self, mocker, mock_task_class):
        mock_add_field = mocker.Mock()
        mock_task_class.hdf5_manager = mock_add_field

        mock_task_class.teardown_hdf5_manager()

        mock_add_field.close.assert_called_once_with()
