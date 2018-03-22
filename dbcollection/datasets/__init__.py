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
    """ Base class for download/processing a dataset.

    Parameters
    ----------
    data_path : str
        Path to the data directory.
    cache_path : str
        Path to the cache file
    extract_data : bool, optional
        Extracts the downloaded files if they are compacted.
    verbose : bool
        Be verbose

    Attributes
    ----------
    data_path : str
        Path to the data directory.
    cache_path : str
        Path to the cache file
    extract_data : bool, optional
        Extracts the downloaded files if they are compacted.
    verbose : bool
        Be verbose
    urls : list
        List of URL links to download.
    keywords : list
        List of keywords.
    tasks : dict
        Dataset's tasks.
    default_task : str
        Default task name.

    """

    # download url
    urls = ()  # list of urls to download

    # some keywords. These are used to classify datasets for easier
    # categorization in the cache file.
    keywords = ()

    # init tasks
    tasks = {}  # dictionary of available tasks to process
    # Example: tasks = {'classification':Classification}
    default_task = ''  # Should define a default class!
    # Example: default_task='classification'

    def __init__(self, data_path, cache_path, extract_data=True, verbose=True):
        """Initialize class."""
        assert data_path
        assert cache_path
        self.data_path = data_path
        self.cache_path = cache_path
        self.extract_data = extract_data
        self.verbose = verbose

    def download(self):
        """
        Download and extract files to disk.

        Returns
        -------
        tuple
            A list of keywords.

        """
        # download + extract data and remove temporary files
        download_extract_all(self.urls, self.data_path, self.extract_data, self.verbose)

        return self.keywords

    def parse_task_name(self, task):
        """Parses the task string to look for key suffixes.

        Parameters
        ----------
        task : str
            Task name.

        Returns
        -------
        str
            Returns a task name without the '_s' suffix.

        """
        if task.endswith('_s'):
            return task[:-2], '_s'
        else:
            return task, None

    def get_task_constructor(self, task):
        """Returns the class constructor for the input task.

        Parameters
        ----------
        task : str
            Task name.

        Returns
        -------
        str
            Task name.
        str
            Task's ending suffix (if any).
        BaseTask
            Constructor to process the metadata of a task.

        """
        if task == '':
            task_, suffix = self.default_task, None
        elif task == 'default':
            task_, suffix = self.default_task, None
        else:
            task_, suffix = self.parse_task_name(task)
        return task_, suffix, self.tasks[task_]

    def process(self, task='default'):
        """Processes the metadata of a task.

        Parameters
        ----------
        task : str, optional
            Task name.

        Returns
        -------
        dict
            Returns a dictionary with the task name as key and the filename as value.

        """
        task_, suffix, task_constructor = self.get_task_constructor(task)
        if self.verbose:
            print('\nProcessing \'{}\' task:'.format(task_))
        task_loader = task_constructor(self.data_path, self.cache_path, suffix, self.verbose)
        task_filename = task_loader.run()
        if suffix:
            return {task_ + suffix: task_filename}
        else:
            return {task_: task_filename}


class BaseDatasetNew(object):
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


class BaseTaskNew(object):
    """Base class for processing the metadata of a task of a dataset.

    Parameters
    ----------
    data_path : str
        Path to the data directory.
    cache_path : str
        Path to the cache file
    verbose : bool, optional
        Displays text information to the screen (if true).

    Attributes
    ----------
    data_path : str
        Path to the data directory of the dataset.
    cache_path : str
        Path to store the HDF5 metadata file of a dataset in the cache directory.
    verbose : bool
        Displays text information to the screen (if true).
    filename_h5 : str
        Name of the HDF5 file.
    hdf5_filepath : str
        File name + path of the HDF5 metadata file in disk.

    """

    filename_h5 = ''  # name of the task file

    def __init__(self, data_path, cache_path, verbose=True):
        """Initialize class."""
        assert data_path, "Must insert a valid data path"
        assert cache_path, "Must insert a valid cache path"
        self.cache_path = cache_path
        self.data_path = data_path
        self.verbose = verbose
        self.hdf5_filepath = self.get_hdf5_save_filename()
        self.hdf5_manager = None

    def get_hdf5_save_filename(self):
        """Builds the HDF5 file name + path on disk."""
        return os.path.join(self.cache_path, self.filename_h5 + '.h5')

    def run(self):
        """Main Method. Runs the task metadata processing.

        It creates an HDF5 file in disk to store the resulting
        subgroups of the dataset's set partitions (e.g., train/val/test/etc.).
        Then, it loads the dataset's raw metadata from disk into memory as a
        generator, retrieves the data fields obtained in the processing stage
        and saves them into an HDF5 file in disk.

        Returns
        -------
        str
            File name + path of the task's HDF5 metadata file.
        """
        self.setup_manager_hdf5()
        data_generator = self.load_data()
        self.process_metadata(data_generator)
        self.save_data_to_disk()
        self.teardown_manager_hdf5()
        return self.hdf5_filepath

    def setup_manager_hdf5(self):
        """Sets up the metadata manager to store the processed data to disk."""
        if self.verbose:
            print('\n==> Storing metadata to file: {}'.format(self.hdf5_filepath))
        self.hdf5_manager = None

    def load_data(self):
        """Loads the dataset's (meta)data from disk (create a generator).

        Load data from annnotations and split it to corresponding
        sets (train, val, test, etc.)

        Returns
        -------
        generator
            A sequence of dictionary objects with a key-value pair
            with the name of the set split and the data.

        """
        pass  # stub

    def process_metadata(self, data_generator):
        """Processes the dataset's (meta)data and stores it into an HDF5 file."""
        for data in data_generator:
            for set_name in data:
                if self.verbose:
                    print('\nSaving set metadata: {}'.format(set_name))
                set_group = self.hdf5_create_group(set_name)
                self.set_data_fields_to_save(set_group, data[set_name], set_name)
                set_group_raw = self.hdf5_create_group(set_name + '/raw')
                self.save_raw_metadata_to_hdf5(set_group_raw, data[set_name], set_name)

    def hdf5_create_group(self, group_name):
        """Creates a group in the HDF5 file.

        Parameters
        ----------
        group_name : str
            Name of the group to be created in the HDF5 file.

        """
        pass

    def set_data_fields_to_save(self, hdf5_manager, data, set_name):
        """Sets up which data fields to save in the HDF5 metadata file for a given set.

        All fields set in this method are organized as a single big matrix.
        This results in much faster data retrieval than by transversing nested
        groups + datasets in an HDF5 file.

        Parameters
        ----------
        hdf5_handler : TODO
            hdf5 group object handler.
        data : dict
            Dictionary containing the data annotations of a set split.
        set_name : str
            Name of the set split.

        """
        pass  # stub

    def save_raw_metadata_to_hdf5(self, hdf5_manager, data, set_name):
        """Saves the dataset's metadata in its raw (original) format inside the HDF5 file.

        Most datasets are set as nested trees of files + directories.
        Here, the metadata of a dataset is stored in this fashion,
        closely following the tree structure of the data.

        Parameters
        ----------
        hdf5_handler : TODO
            hdf5 group object handler.
        data : dict
            Dictionary containing the data annotations of a set split.
        set_name : str
            Name of the set split.

        """
        pass  # stub

    def save_data_to_disk(self):
        pass

    def teardown_manager_hdf5(self):
        """Sets up the MetadataManager object to manage the metadata save process to disk."""
        self.hdf5_manager.close()
