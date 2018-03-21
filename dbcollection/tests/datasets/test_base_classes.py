"""
Test the base classes for managing datasets and tasks.
"""


import pytest

from dbcollection.datasets import BaseDataset, BaseTask


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
    return BaseDataset(
        data_path=test_data["data_path"],
        cache_path=test_data["cache_path"],
        extract_data=test_data["extract_data"],
        verbose=test_data["verbose"]
    )


class TestBaseDataset:
    """Unit tests for the BaseDataset class."""

    def test_init_with_all_input_args(self, mocker):
        data_path = '/path/to/data'
        cache_path = '/path/to/cache'
        extract_data=True
        verbose=True

        db_manager = BaseDataset(data_path=data_path,
                                 cache_path=cache_path,
                                 extract_data=extract_data,
                                 verbose=verbose)

        assert db_manager.data_path == '/path/to/data'
        assert db_manager.cache_path == '/path/to/cache'
        assert db_manager.extract_data == True
        assert db_manager.verbose == True
        assert db_manager.urls == ()
        assert db_manager.keywords == ()
        assert db_manager.tasks == {}
        assert db_manager.default_task == ''

    def test_init_withouth_optional_input_args(self, mocker):
        data_path = '/path/to/data'
        cache_path = '/path/to/cache'

        db_manager = BaseDataset(data_path=data_path,
                                 cache_path=cache_path)

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
            BaseDataset()

    def test_init__raises_error_too_many_input_args(self, mocker):
        with pytest.raises(TypeError):
            BaseDataset('/path/to/data', '/path/to/cache', False, False, 'extra_field')

    def test_download(self, mocker, mock_dataset_class):
        mock_download_extract = mocker.patch("dbcollection.datasets.download_extract_all")

        mock_dataset_class.download()

        assert mock_download_extract.called

    def test_process(self, mocker, mock_dataset_class):
        mock_parse_task = mocker.patch.object(BaseDataset, "parse_task_name", return_value='taskA')
        mock_process_metadata = mocker.patch.object(BaseDataset, "process_metadata", return_value='/path/to/task/filename.h5')

        result = mock_dataset_class.process('taskA')

        assert mock_parse_task.called
        assert mock_process_metadata.called
        assert result == {'taskA': '/path/to/task/filename.h5'}

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
        mock_get_constructor = mocker.patch.object(BaseDataset, "get_task_constructor", return_value=mocker.MagicMock())

        mock_dataset_class.process_metadata('some_task')

        assert mock_get_constructor.called

    def test_get_task_constructor(self, mocker, mock_dataset_class):
        task = 'taskZ'

        mock_dataset_class.tasks = {task: 'some_data'}
        result = mock_dataset_class.get_task_constructor(task)

        assert result == 'some_data'


class TestBaseTask:
    """Unit tests for the BaseTask class."""

    def test_init_with_all_input_args(self, mocker):
        pass

    def test_init_withouth_optional_input_args(self, mocker):
        pass

    def test_init__raises_error_no_input_args(self, mocker):
        pass

    def test_init__raises_error_too_many_input_args(self, mocker):
        pass
