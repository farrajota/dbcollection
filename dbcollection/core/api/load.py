"""
Load API class.
"""


from __future__ import print_function

from dbcollection.core.manager import CacheManager
from dbcollection.core.loader import DataLoader

from .download import download
from .process import process

from .metadata import MetadataConstructor


def load(name, task='default', data_dir='', verbose=True):
    """Returns a metadata loader of a dataset.

    Returns a loader with the necessary functions to manage the selected dataset.

    Parameters
    ----------
    name : str
        Name of the dataset.
    task : str, optional
        Name of the task to load.
    data_dir : str, optional
        Directory path to store the downloaded data.
    verbose : bool, optional
        Displays text information (if true).

    Returns
    -------
    DataLoader
       Data loader class.

    Raises
    ------
    Exception
        If dataset is not available for loading.

    Examples
    --------
    Load the MNIST dataset.

    >>> import dbcollection as dbc
    >>> mnist = dbc.load('mnist')
    >>> print('Dataset name: ', mnist.db_name)
    Dataset name:  mnist

    """
    assert name, 'Must input a valid dataset name: {}'.format(name)

    loader = LoadAPI(name=name,
                     task=task,
                     data_dir=data_dir,
                     verbose=verbose)

    data_loader = loader.run()

    return data_loader


class LoadAPI(object):
    """Dataset load API class.

    This class contains methods to correctly load
    a dataset's metadata as a data loader object.

    Parameters
    ----------
    name : str
        Name of the dataset.
    task : str
        Name of the task to load.
    data_dir : str
        Directory path to store the downloaded data.
    verbose : bool
        Displays text information (if true).

    Attributes
    ----------
    name : str
        Name of the dataset.
    task : str
        Name of the task to load.
    data_dir : str
        Directory path to store the downloaded data.
    verbose : bool
        Displays text information (if true).
    cache_manager : CacheManager
        Cache manager object.
    available_datasets_list : list
        List of available datast names for download.

    """

    def __init__(self, name, task, data_dir, verbose):
        """Initialize class."""
        assert isinstance(name, str), 'Must input a valid dataset name.'
        assert isinstance(task, str), 'Must input a valid task name.'
        assert isinstance(data_dir, str), 'Must input a valid directory.'
        assert isinstance(verbose, bool), "Must input a valid boolean for verbose."

        self.name = name
        self.data_dir = data_dir
        self.verbose = verbose
        self.cache_manager = self.get_cache_manager()
        self.task = self.parse_task_name(task)

    def get_cache_manager(self):
        return CacheManager()

    def parse_task_name(self, task):
        """Validate the task name."""
        db_metadata = self.get_dataset_metadata_obj(self.name)
        return db_metadata.parse_task_name(task)

    def get_dataset_metadata_obj(self, name):
        return MetadataConstructor(name)

    def run(self):
        """Main method."""
        if not self.dataset_data_exists_in_cache():
            if self.verbose:
                print('==> Dataset \'{}\' not found in cache.'.format(self.name))
                print('Proceeding to download the data files...')
            self.download_dataset_data()

        if not self.dataset_task_metadata_exists_in_cache():
            if self.verbose:
                print('==> Processed metadata not found for dataset \'{}\', task \'{}\'.'
                      .format(self.name, self.task))
                print('Proceeding to process the metadata for this task...')
            self.process_dataset_task_metadata()

        if self.verbose:
            print('==> Load the dataset\'s metadata.')
        dataset_loader = self.get_data_loader()

        if self.verbose:
            print('==> Dataset loading complete.')

        return dataset_loader

    def dataset_data_exists_in_cache(self):
        return self.cache_manager.dataset.exists(self.name)

    def download_dataset_data(self):
        self.download_dataset()
        self.reload_cache()

    def download_dataset(self):
        """Download the dataset to disk."""
        download(name=self.name,
                 data_dir=self.data_dir,
                 extract_data=True,
                 verbose=self.verbose)

    def reload_cache(self):
        self.cache_manager.manager.reload_cache()

    def dataset_task_metadata_exists_in_cache(self):
        return self.cache_manager.task.exists(task=self.task, name=self.name)

    def process_dataset_task_metadata(self):
        self.process_dataset()
        self.reload_cache()

    def process_dataset(self):
        """Process the dataset's metadata."""
        process(name=self.name,
                task=self.task,
                verbose=self.verbose)

    def get_data_loader(self):
        """Return a DataLoader object."""
        data_dir_path = self.get_data_dir_path_from_cache()
        hdf5_filepath = self.get_hdf5_file_path_from_cache()
        data_loader = self.get_loader_obj(data_dir_path, hdf5_filepath)
        return data_loader

    def get_data_dir_path_from_cache(self):
        dataset_metadata = self.get_dataset_metadata(self.name)
        return dataset_metadata["data_dir"]

    def get_dataset_metadata(self, name):
        return self.cache_manager.dataset.get(name)

    def get_hdf5_file_path_from_cache(self):
        task_metadata = self.get_task_metadata(self.name, self.task)
        return task_metadata["filename"]

    def get_task_metadata(self, name, task):
        return self.cache_manager.task.get(name, task)

    def get_loader_obj(self, data_dir, hdf5_filepath):
        return DataLoader(name=self.name,
                          task=self.task,
                          data_dir=data_dir,
                          hdf5_filepath=hdf5_filepath)
