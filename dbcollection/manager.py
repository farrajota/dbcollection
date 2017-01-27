"""
dbcollection managing functions.
"""

from __future__ import print_function
import json
from .cache import CacheManager
from .loader import DatasetLoader
from . import dataset


# check if there's an entry in the cache file for the dataset
cache_manager = CacheManager()


def load(name, data_path=None, save_name=None, task='default', download=True, verbose=True, organize_list=None, select=None, filter=None):
    """loads dataset metadata file.

    Returns a loader with the necessary functions to manage the selected dataset.

    Parameters
    ----------
    name : str
        Name of the dataset.
    data_path : str
        Path to store the data (if the data doesn't exist and the download flag is equal True).
    save_name : bool
        Save the metadata file with a new name.
        (usefull to create custom versions of the original).
    task : str
        Specify a specific task to load.
	download : bool
        Downloads data from the host to disk (if true).
	verbose : bool
        Displays text information (if true).
	organize_list : dict
        Organizes the data w.r.t. to other fields. The data must be organized in a
        dictionary with the following format: {"new_field_name":"field_name"}
	select : dict
        Selects indexes from 'field_name' equal to the selected value(s)
        (removes objects ids without those 'field_name''s values)
	filter : dict
        Removes indexes from 'field_name' equal to the selected value(s)
        (removes objects ids with those 'field_name''s values)

    Returns
    -------
    DatasetLoader
       Returns a loader class.
    """

    # check if dataset exists in the cache file
    if cache_manager.exists(name, task):
        dataset_category = cache_manager.get_category(name)
    else:
        # get cache default save path
        cache_save_path = cache_manager.default_cache_dir

        # download dataset
        if download:
            dataset.download(name, data_path, verbose)

        # preprocess dataset
        cache_info, dataset_category = dataset.process(name, data_path, cache_save_path, verbose)

        # update dbcollection.json file with the new data
        cache_manager.update(name, dataset_category, dataset.data_path, dataset.cache_path, dataset.cache_info)

    # get cache path
    cache_path = cache_manager.get_cache_path(name, task)

    # get dataset storage path
    dset_paths = cache_manager.get_dataset_storage_paths(name)

    # Create a loader
    dataset_loader = DatasetLoader(name, dataset_category, task, dset_paths['data_path'], cache_path)

    # organize data into a list w.r.t. some field_name
    # do select/filter processing here
    # save dataset_loader with a different task name (use save_name)

    # return Loader
    return dataset_loader



def add(name, data_path, cache_path, category, task):
    """Add dataset to list.

    Adds a custom dataset to the list.

    Parameters
    ----------
    name : str
        Dataset name to add to the list.
	data_path : str
        Folder path of the dataset's data on disk.
	cache_path : str
        Cache's metadata storage path.
	category : str
        Name of the category (refactor this idea an save in a custom category).
	task : str
        Name of the new task.

    Returns
    -------
        None
    """
    pass


def delete(name):
    """Delete a dataset from disk (cache+data).

    Deletes the data+metadata of a dataset on disk (cache file included).

    Parameters
    ----------
    name : str
        Name of the dataset to delete the data from disk.

    Returns
    -------
        None
    """
    # check if dataset exists in the cache file
    if cache_manager.exists_dataset(name):
        cache_manager.delete_dataset(name, True)
    else:
        print('Dataset ' + name + ' does not exist.')
        #raise Exception('Dataset ' + name + ' does not exist.')


def config(name, fields, default_paths):
    """config cache file.

    Manually setup the configurations of the cache file dbcollection.json.

    Parameters
    ----------
    name : str
        Name of the dataset.
	fields : dict
        Specifies which fields and values to update the dbcollection cache file.
	default_paths : dict
        Updates the default cache/data paths.

    Returns
    -------
        None
    """
    pass


def download(name, data_path, verbose=True):
    """Download dataset.

    Download the data for one (or several) listed dataset(s).

    Parameters
    ----------
    name : str
        Name of the dataset to reset the cache.
    cache : bool
        Force the cache file of the preprocessed data to be deleted for the particular dataset.
	data : bool
        Force the dataset's data files to be deleted for the particular dataset.

    Returns
    -------
        None
    """
    # get cache default save path
    cache_save_path = cache_manager.default_cache_dir

    # download/preprocess dataset
    dataset.download(name, data_path, cache_save_path, verbose)



def reset(name):
    """Delete all metadata cache files and dir from disk/list.

    Resets the data of the dbcollection.json cache file for a specific dataset
    (it deletes the cache files for this dataset as well, if any).

    Parameters
    ----------
	name : str
        Name of the dataset to reset the cache.

    Returns
    -------
        None
    """
     # check if dataset exists in the cache file
    if cache_manager.exists_dataset(name):
        cache_manager.delete_dataset(name, False)
    else:
        print('Dataset ' + name + ' does not exist.')
        #raise Exception('Dataset ' + name + ' does not exist.')


def query(info, search):
    """Query the cache file.

    list all available datasets for download/preprocess. (tenho que pensar melhor sobre este)

    Parameters:
    -----------
    info : list
	search : dict

    Returns
    -------
        None
    """
    pass



def list(verbose=False):
    """List cache data.

    Prints the contents of the dbcollection.json cache file

    Parameters
    ----------
    verbose : bool
        If true, prints the full cache file to the screen.
        Else, prints only the categories + dataset names.

    Returns
    -------
        None
    """
    data_ = cache_manager.data
    if not verbose:
        cat_dataset_dict = {}
        for category in cache_manager.data['dataset'].keys():
            cat_dataset_dict[category] = {}
            for name in cache_manager.data['dataset'][category].keys():
                cat_dataset_dict[category][name] = cache_manager.data['dataset'][category][name]['cache_files']['default']
        data_['dataset'] = cat_dataset_dict

    print(json.dumps(data_, sort_keys=True, indent=4))


