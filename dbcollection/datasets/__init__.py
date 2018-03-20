"""
This module contains scripts to download/process
all datasets available in dbcollection.

These scripts are self contained, meaning they can be imported
and used to manually setup a dataset.
"""


from __future__ import print_function
import os
import h5py

from dbcollection.utils.url import download_extract_all


class BaseDataset(object):
    """Base class for download/processing a dataset.

    Parameters
    ----------
    data_path : str
        Path to the data directory.
    cache_path : str
        Path to the cache file
    extract_data : bool, optional
        Extracts the downloaded files if they are compacted.
    verbose : bool, optional
         Displays text information to the screen (if true).

    Attributes
    ----------
    data_path : str
        Path to the data directory.
    cache_path : str
        Path to the cache file
    extract_data : bool
        Extracts the downloaded files if they are compacted.
    verbose : bool
        Displays text information to the screen (if true).
    urls : list
        List of URL paths to download.
    keywords : list
        List of keywords to classify datasets.
    tasks : dict
        Dataset's tasks for processing.
    default_task : str
        Default task name.

    """

    urls = ()  # list of urls to download
    keywords = ()  # List of keywords to classify/categorize datasets in the cache.
    tasks = {}  # dictionary of available tasks to process
                # Example: tasks = {'classification':Classification}
    default_task = ''  # Defines the default class!
                       # Example: default_task='classification'

    def __init__(self, data_path, cache_path, extract_data=True, verbose=True):
        """Initialize class."""
        assert data_path, "Must insert a valid data path"
        assert cache_path, "Must insert a valid cache path"
        self.data_path = data_path
        self.cache_path = cache_path
        self.extract_data = extract_data
        self.verbose = verbose

    def download(self):
        """Downloads and extract files to disk.

        Returns
        -------
        tuple
            A list of keywords.

        """
        download_extract_all(urls=self.urls,
                             dir_save=self.data_path,
                             extract_data=self.extract_data,
                             verbose=self.verbose)

    def process(self, task='default'):
        """Processes the metadata of a task.

        Parameters
        ----------
        task : str, optional
            Name of the task.

        Returns
        -------
        dict
            Returns a dictionary with the task name as key and the filename as value.

        """
        task_ = self.parse_task_name(task)
        if self.verbose:
            print("\nProcessing '{}' task:".format(task_))
        hdf5_filename = self.process_metadata(task_)
        return {task_: hdf5_filename}

    def parse_task_name(self, task):
        """Parses the task name to a valid name."""
        if task == '' or task == 'default':
            return self.default_task
        else:
            return task

    def process_metadata(self, task):
        """Processes the metadata for a task.

        Parameters
        ----------
        task : str
            Name of the task.

        Returns
        -------
        str
            File name + path of the resulting HDFR5 metadata file of the task.
        """
        constructor = self.get_task_constructor(task)
        processer = constructor(data_path=self.data_path,
                                cache_path=self.cache_path,
                                verbose=self.verbose)
        return processer.run()

    def get_task_constructor(self, task):
        """Returns the class constructor for the input task.

        Parameters
        ----------
        task : str
            Name of the task.

        Returns
        -------
        BaseTask
            Constructor to process the metadata of a task.

        """
        assert task
        return self.tasks[task]


class BaseTask(object):
    """Base class for processing a task of a dataset.

    Parameters
    ----------
    data_path : str
        Path to the data directory.
    cache_path : str
        Path to the cache file
    suffix : str, optional
        Suffix to select optional properties for a task.
    verbose : bool, optional
        Be verbose.

    Attributes
    ----------
    data_path : str
        Path to the data directory.
    cache_path : str
        Path to the cache file
    suffix : str, optional
        Suffix to select optional properties for a task.
    verbose : bool, optional
        Be verbose.
    filename_h5 : str
        hdf5 metadata file name.

    """

    # name of the task file
    filename_h5 = 'task'

    def __init__(self, data_path, cache_path, suffix=None, verbose=True):
        """Initialize class."""
        assert data_path
        assert cache_path
        self.cache_path = cache_path
        self.data_path = data_path
        self.suffix = suffix
        self.verbose = verbose

    def load_data(self):
        """
        Load data of the dataset (create a generator).

        Load data from annnotations and split it to corresponding
        sets (train, val, test, etc.)

        """
        pass  # stub

    def add_data_to_source(self, hdf5_handler, data, set_name=None):
        """
        Store data annotations in a nested tree fashion.

        It closely follows the tree structure of the data.

        Parameters
        ----------
        hdf5_handler : h5py._hl.group.Group
            hdf5 group object handler.
        data : list/dict
            List or dict containing the data annotations of a particular set or sets.
        set_name : str
            Set name.

        """
        pass  # stub

    def add_data_to_default(self, handler, data, set_name=None):
        """
        Add data of a set to the default group.

        For each field, the data is organized into a single big matrix.

        Parameters
        ----------
        hdf5_handler : h5py._hl.group.Group
            hdf5 group object handler.
        data : list/dict
            List or dict containing the data annotations of a particular set or sets.
        set_name : str
            Set name.

        """
        pass  # stub

    def process_metadata(self):
        """
        Process metadata and store it in a hdf5 file.
        """

        # create/open hdf5 file with subgroups for train/val/test
        if self.suffix:
            file_name = os.path.join(self.cache_path, self.filename_h5 + self.suffix + '.h5')
        else:
            file_name = os.path.join(self.cache_path, self.filename_h5 + '.h5')
        fileh5 = h5py.File(file_name, 'w', libver='latest')

        if self.verbose:
            print('\n==> Storing metadata to file: {}'.format(file_name))

        # setup data generator
        data_gen = self.load_data()

        for data in data_gen:
            for set_name in data:

                if self.verbose:
                    print('\nSaving set metadata: {}'.format(set_name))

                # add data to the **source** group
                if self.suffix is '_s':
                    sourceg = fileh5.create_group(set_name + '/source')
                    self.add_data_to_source(sourceg, data[set_name], set_name)

                # add data to the **default** group
                defaultg = fileh5.create_group(set_name)
                self.add_data_to_default(defaultg, data[set_name], set_name)

        # close file
        fileh5.close()

        # return information of the task + cache file
        return file_name

    def run(self):
        """Run task processing."""
        filename = self.process_metadata()
        return filename
