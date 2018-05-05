"""
Class to manage the dbcollection.json cache file.
"""


from __future__ import print_function
import os
import shutil
import json
import warnings
import pprint
from glob import glob

from dbcollection.utils import merge_dicts, print_text_box


class CacheManager:
    """Manage dbcollection configurations and stores them inside a cache file stored in disk.

    Attributes
    ----------
    cache_filename : str
        Cache file path + name.
    cache_dir : str
        Default directory to store all dataset's metadata files.
    download_dir : str
        Default save dir path for downloaded data.
    data : dict
        Cache contents.

    """

    def __init__(self):
        """Initializes the class."""
        self.manager = CacheDataManager()
        self.info = CacheManagerInfo(self.manager)
        self.dataset = CacheManagerDataset(self.manager)
        self.task = CacheManagerTask(self.manager)
        self.category = CacheManagerCategory(self.manager)

    def info_cache(self):
        """Prints the information of the cache."""
        self.info.info()
        self.dataset.info()
        self.category.info()


class CacheDataManager:
    """Cache's data write/read methods."""

    def __init__(self):
        """Initialize class."""
        self.cache_filename = self._get_cache_filename()
        self.data = self.read_data_cache()
        self._cache_dir = self._get_cache_dir()
        self.info = CacheManagerInfo(self.data["info"])

    def _get_cache_filename(self):
        """Return the cache file name + path."""
        home_dir = os.path.expanduser("~")
        filename = 'dbcollection.json'
        return os.path.join(home_dir, filename)

    def read_data_cache(self):
        """Loads data from the cache file.

        Returns
        -------
        dict
            Data containing information of all datasets and categories.

        """
        if os.path.exists(self.cache_filename):
            return self.read_data_cache_file()
        else:
            data = self._empty_data()
            self.write_data_cache(data)
            return data

    def read_data_cache_file(self):
        """Read the cache file data to memory.

        Returns
        -------
        dict
            Data structure of the cache (file).

        """
        with open(self.cache_filename, 'r') as json_data:
            return json.load(json_data)

    def _empty_data(self):
        """Returns an empty (dummy) template of the cache data structure."""
        return {
            "info": {
                "root_cache_dir": self._get_default_cache_dir(),
                "root_downloads_dir": self._get_default_downloads_dir(),
            },
            "dataset": {},
            "category": {}
        }

    def _get_default_cache_dir(self):
        """Returns the pre-defined path of the cache's root directory."""
        default_cache_dir = os.path.join(os.path.expanduser("~"), 'dbcollection')
        return default_cache_dir

    def _get_default_downloads_dir(self):
        """Returns the pre-defined path of the cache's downloads directory."""
        default_downloads_dir = os.path.join(self._get_default_cache_dir(), 'downloads')
        return default_downloads_dir

    def write_data_cache(self, data):
        """Writes data to the cache file.

        Parameters
        ----------
        name : str
            Name of the dataset.

        Raises
        ------
        IOError
            If the file cannot be opened.

        """
        assert data, 'Must input a non-empty dictionary.'
        with open(self.cache_filename, 'w') as file_cache:
            json.dump(data, file_cache, sort_keys=True, indent=4, ensure_ascii=False)
        self.data = data  # must assign the new data or risk problems

    def _set_cache_dir(self, path):
        """Set the root cache dir to store all metadata files"""
        assert path, 'Must input a directory path'
        self._cache_dir = path
        self.data['info']['root_cache_dir'] = self._cache_dir
        self.write_data_cache(self.data)

    def _get_cache_dir(self):
        """Get the root cache dir path."""
        return self.data['info']['root_cache_dir']

    cache_dir = property(_get_cache_dir, _set_cache_dir)

    def reset_cache_dir(self):
        """Reset the root cache dir path."""
        self._set_cache_dir(self._get_default_cache_dir())

    def _set_download_dir(self, path):
        """Set the root save dir path for downloaded data."""
        assert path, 'Must input a non-empty path.'
        self.data['info']['root_downloads_dir'] = path
        self.write_data_cache(self.data)

    def _get_download_dir(self):
        """Get the root save dir path."""
        return self.data['info']['root_downloads_dir']

    download_dir = property(_get_download_dir, _set_download_dir)

    def reset_download_dir(self):
        """Reset the root download dir path."""
        self._set_download_dir(self._get_default_downloads_dir())

    def reset_cache(self, force_reset=False):
        """Resets the cache file contents.

        Resets the cache file by removing all info about
        the datasets/categories/info from the cache file.
        Basically, it empties the cache contents.

        Parameters
        ----------
        force_reset : bool, optional
            Forces the cache to be reset (emptied) if True.

        Warning
        -------
        UserWarning
            If force_reset is False, display a warning to the user.

        """
        if force_reset:
            self.write_data_cache(self._empty_data())
        else:
            msg = 'All information about stored datasets will be lost if you proceed! ' + \
                  'Set \'force_reset=True\' to proceed with the reset of dbcollection.json.'
            warnings.warn(msg, UserWarning, stacklevel=2)

    def delete_cache(self, force_delete_file=False, force_delete_metadata=False):
        """Deletes the cache file and/or metadata dir from disk.

        Deletes the dbcollection.json file from disk if enabled.
        By default this option is disabled and a warning is displayed
        instead. Only by selecting the 'force_delete_file' option will
        the cache file be deleted.

        Also, there is an option to delete the cache's metadata files
        by selecting the 'force_delete_metadata'. This will remove the
        every dataset's metadata dir and its contents, but it will not
        delete the downloads directory.

        Parameters
        ----------
        force_delete_file : bool, optional
            Forces the cache file to be deleted if True.
        force_delete_metadata : bool, optional
            Forces the cache metadata to be deleted if True.

        Warning
        -------
        UserWarning
            If force_delete_file is False, display a warning to the user.

        """
        self._delete_cache_file(force_delete_file)
        if force_delete_metadata:
            self._delete_cache_metadata(force_delete_file)

    def _delete_cache_file(self, force_delete_file):
        """Deletes the cache file from disk."""
        if force_delete_file:
            if os.path.exists(self.cache_filename):
                os.remove(self.cache_filename)
        else:
            msg = 'All information about stored datasets will be lost if you proceed! ' + \
                  'Set \'force_delete_file=True\' to proceed with the deletion of ' + \
                  'dbcollection.json.'
            warnings.warn(msg, UserWarning, stacklevel=2)

    def _delete_cache_metadata(self, force_delete_file):
        """Deletes the cache metadata files from disk."""
        if force_delete_file:
            self._delete_dirs_datasets_in_cache_dir_except_downloads()
        else:
            msg = 'All metadata files of all datasets will be lost if you proceed! ' + \
                'Set both \'force_delete_file=True\' and \'force_delete_metadata=True\' ' + \
                'to proceed with the deletion of dbcollection.json and all metadata files.'
            warnings.warn(msg, UserWarning, stacklevel=2)

    def _delete_dirs_datasets_in_cache_dir_except_downloads(self):
        """Deletes all directories from the root cache dir except the downloads dir."""
        dirs = glob("{}/*/".format(self.cache_dir))
        try:
            dirs.remove(self.download_dir)
        except ValueError:
            pass
        for dir_path in dirs:
            shutil.rmtree(dir_path)

    def add_data(self, name, data_dir, tasks):
        """Adds a new dataset to the cache.

        Parameters
        ----------
        name : str
            Name of the dataset.
        data_dir : str
            Path of the dataset's data files.
        tasks : dict
            List of tasks.

        """
        assert name, "Must input a valid dataset name."
        assert data_dir, "Must input a valid data directory."
        assert tasks is not None, "Must input a valid tasks."

        new_data = {
            "data_dir": data_dir,
            "keywords": self._get_keywords_from_tasks(tasks),
            "tasks": tasks
        }
        self.data["dataset"][name] = new_data
        self.update_categories()
        self.write_data_cache(self.data)

    def _get_keywords_from_tasks(self, tasks):
        """Fetch a list of categories from a tasks' dictionary."""
        keywords = []
        for task in tasks:
            keywords.extend(tasks[task]["categories"])
        return tuple(sorted(set(keywords)))

    def update_categories(self):
        """Updates the category list of all categories."""
        categories = {}
        datasets = self.data['dataset']
        used_categories = self._get_list_categories_used(datasets)
        for category in used_categories:
            categories.update({
                category: self._get_datasets_tasks_by_category(datasets, category)
            })
        self.data["category"] = categories

    def _get_list_categories_used(self, datasets):
        """Returns a list of all categories available in the datasets data."""
        categories_used = []
        for dataset in datasets:
            categories_used.extend(datasets[dataset]['keywords'])
        return list(sorted(set(categories_used)))

    def _get_datasets_tasks_by_category(self, datasets, category):
        """Returns a list of all datasets and tasks that have the category name."""
        list_datasets_tasks = {}
        for dataset in datasets:
            list_datasets_tasks.update({
                dataset: self._get_tasks_by_category(datasets[dataset]["tasks"], category)
            })
        return list_datasets_tasks

    def _get_tasks_by_category(self, tasks, category):
        """Returns a list of tasks that contains the category name."""
        matching_tasks = []
        for task in tasks:
            if category in tasks[task]["categories"]:
                matching_tasks.append(task)
        return sorted(matching_tasks)

    def get_data(self, name):
        """Retrieves the data of a dataset from the cache.

        Parameters
        ----------
        name : str
            Name of the dataset.

        Returns
        -------
        dict
            Information about the dataset.

        """
        assert name, "Must input a valid dataset name."
        try:
            return self.data["dataset"][name]
        except KeyError:
            raise KeyError("The dataset \'{}\' does not exist in the cache.".format(name))

    def update_data(self, name, cache_dir=None, data_dir=None, tasks=None):
        """Updates the data of a dataset in the cache.

        Parameters
        ----------
        name : str
            Name of the dataset.
        cache_dir : str, optional
            Path of the dataset's metadata directory.
        data_dir : str, optional
            Path of the dataset's data files.
        tasks : dict, optional
            List of tasks.

        """
        assert name, "Must input a valid dataset name."
        assert name in self.data["dataset"], "The dataset \'{}\' does not exist in the cache." \
                                             .format(name)
        if cache_dir:
            self.data["dataset"][name]["cache_dir"] = cache_dir
        if data_dir:
            self.data["dataset"][name]["data_dir"] = data_dir
        if tasks:
            self.data["dataset"][name]["tasks"] = tasks
            self.data["dataset"][name]["keywords"] = self._get_keywords_from_tasks(tasks)
        if cache_dir or data_dir or tasks:
            self.update_categories()
            self.write_data_cache(self.data)

    def delete_data(self, name):
        """Deletes a dataset from the cache data.

        Parameters
        ----------
        name : str
            Name of the dataset.

        """
        assert name, "Must input a valid dataset name."
        try:
            self.data["dataset"].pop(name)
            self.update_categories()
            self.write_data_cache(self.data)
        except KeyError:
            raise KeyError("The dataset \'{}\' does not exist in the cache.".format(name))

    def reload_cache(self):
        """Reloads the cache data contents by reading the cache file from disk."""
        self.data = self.read_data_cache()


class CacheManagerDataset:
    """Manage the cache's dataset configurations."""

    def __init__(self, manager):
        """Initialize class."""
        assert manager, "Must input a valid cache manager."
        self.manager = manager

    def add(self, name, data_dir, tasks):
        """Adds a new dataset to the cache.

        Parameters
        ----------
        name : str
            Name of the dataset.
        data_dir : str
            Path of the dataset's data files.
        tasks : dict
            List of tasks.

        """
        assert name, "Must input a valid dataset name."
        assert data_dir, "Must input a valid directory (data_dir)."
        assert tasks is not None, "Must input a valid tasks."

        self.manager.add_data(name, data_dir, tasks)

    def get(self, name):
        """Retrieves the data of a dataset from the cache.

        Parameters
        ----------
        name : str
            Name of the dataset.

        Returns
        -------
        dict
            Information about the dataset.

        """
        assert name, "Must input a valid dataset name."
        return self.manager.get_data(name)

    def update(self, name, cache_dir=None, data_dir=None, tasks=None):
        """Updates the data of a dataset in the cache.

        Parameters
        ----------
        name : str
            Name of the dataset.
        cache_dir : str, optional
            Path of the dataset's metadata directory.
        data_dir : str, optional
            Path of the dataset's data files.
        tasks : dict, optional
            List of tasks.

        """
        assert name, "Must input a valid dataset name."
        self.manager.update_data(name, cache_dir, data_dir, tasks)

    def delete(self, name):
        """Deletes a dataset from the cache data.

        Parameters
        ----------
        name : str
            Name of the dataset.

        """
        assert name, "Must input a valid dataset name."
        self.manager.delete_data(name)

    def exists(self, name):
        """Checks if a dataset name exists in the cache..

        Parameters
        ----------
        name : str
            Name of the dataset.

        Returns
        -------
        bool
            Returns True if the name exists in the dataset names.
            Otherwise, returns False.

        """
        assert name, "Must input a valid dataset name."
        return name in self.manager.data["dataset"]

    def list(self):
        """Returns a list of all dataset names.

        Returns
        -------
        list
            Names of datasets.

        """
        return list(sorted(self.manager.data["dataset"].keys()))

    def info(self, datasets=(), tasks=()):
        """Prints the dataset information contained in the cache.

        If a list of dataset or task names is specified, only the
        information matching any strings in those lists will be
        displayed.

        Parameters
        ----------
        datasets : str/list/tuple, optional
            List of dataset names.
        tasks : str/list/tuple, optional
            List of task names.

        """
        pp = pprint.PrettyPrinter(indent=4)
        print_text_box('Dataset')
        if any(datasets) or any(tasks):
            data = self._get_select_tasks_and_datasets_data(datasets, tasks)
        else:
            data = self._get_dataset_data()
        pp.pprint(data)
        print('')

    def _get_select_tasks_and_datasets_data(self, datasets=(), tasks=()):
        data = {}
        if any(datasets):
            data = self._get_data_selected_datasets(datasets)
        if any(tasks):
            filtered = self._get_data_selected_tasks(tasks)
            data = dict(merge_dicts(data, filtered))
        return data

    def _get_data_selected_datasets(self, datasets):
        data = {}
        cache_dbs = self._get_dataset_data()
        for dataset in datasets:
            for key in cache_dbs:
                if dataset.lower() in key.lower():
                    data.update({key: cache_dbs[key]})
        return data

    def _get_dataset_data(self):
        return self.manager.data['dataset']

    def _get_data_selected_tasks(self, tasks):
        data = {}
        cache_dbs = self._get_dataset_data()
        for task in tasks:
            for dataset in cache_dbs:
                for key in cache_dbs[dataset]['tasks']:
                    if task.lower() in key.lower():
                        data.update({dataset: {"tasks": {key: cache_dbs[dataset]['tasks'][key]}}})
        return data


class CacheManagerTask:
    """Manage the cache's dataset task configurations."""

    def __init__(self, manager):
        """Initialize class."""
        assert manager, "Must input a valid cache manager."
        self.manager = manager

    def add(self, name, task, filename, categories=()):
        """Adds a new task to a dataset in cache.

        Parameters
        ----------
        name : str
            Name of the dataset.
        task : str
            Name of the new dataset.
        filename : str
            Path of the task's metadata HDF5 file.
        categories : list/tuple, optional
            List of category keywords.

        """
        assert name, "Must input a valid dataset name."
        assert task, "Must input a valid task name."
        assert filename, "Must input a valid file path."
        self._assert_dataset_exists_in_cache(name)
        self._assert_task_not_exists_in_dataset_in_cache(name, task)

        self._add_new_task(name, task, filename, categories)

        self._update_cache_data()

    def _assert_dataset_exists_in_cache(self, name):
        try:
            self.manager.data["dataset"][name]
        except KeyError:
            raise KeyError("Invalid dataset name. The dataset \'{}\' does not exist in cache."
                           .format(name))

    def _assert_task_not_exists_in_dataset_in_cache(self, name, task):
        assert task not in self.manager.data["dataset"][name]["tasks"], \
            "The task \'{}\' already exist for the dataset \'{}\'.".format(task, name)

    def _add_new_task(self, name, task, filename, categories):
        self.manager.data["dataset"][name]["tasks"].update({
            task: {
                "filename": filename,
                "categories": sorted(list(categories))
            }
        })

    def _update_cache_data(self):
        self.manager.update_categories()
        self.manager.write_data_cache(self.manager.data)

    def get(self, name, task):
        """Retrieves the metadata of the task of a dataset.

        Parameters
        ----------
        name : str
            Name of the dataset.
        task : str
            Name of the task.

        Returns
        -------
        dict
            Information about the dataset.

        """
        assert name, "Must input a valid dataset name."
        assert task, "Must input a valid task name."
        self._assert_dataset_exists_in_cache(name)
        self._assert_task_exists_in_dataset_in_cache(name, task)
        return self.manager.data["dataset"][name]["tasks"][task]

    def _assert_task_exists_in_dataset_in_cache(self, name, task):
        try:
            self.manager.data["dataset"][name]["tasks"][task]
        except KeyError:
            raise KeyError("Invalid task name. The task \'{}\' does not exist for the dataset"
                           " \'{}\'.".format(task, name))

    def update(self, name, task, filename=None, categories=None):
        """Updates the metadata of a task for a dataset.

        Parameters
        ----------
        name : str
            Name of the dataset.
        task : str
            Name of the task.
        filename : str, optional
            Path of the task's metadata HDF5 file.
        categories : list/tuple, optional
            List of category keywords.

        """
        assert name, "Must input a valid dataset name."
        assert task, "Must input a valid task name."
        self._assert_dataset_exists_in_cache(name)
        self._assert_task_exists_in_dataset_in_cache(name, task)

        self._update_task_filename(name, task, filename)
        self._update_task_categories(name, task, categories)

        self._update_cache_data()

    def _update_task_filename(self, name, task, filename):
        if filename is not None:
            self.manager.data["dataset"][name]["tasks"][task]["filename"] = filename

    def _update_task_categories(self, name, task, categories):
        if categories is not None:
            ordered_categories = sorted(list(categories))
            self.manager.data["dataset"][name]["tasks"][task]["categories"] = ordered_categories

    def delete(self, name, task):
        """Deletes a task of a dataset.

        Parameters
        ----------
        name : str
            Name of the dataset.
        task : str
            Name of the task.

        """
        assert name, "Must input a valid dataset name."
        assert task, "Must input a valid task name."
        self._assert_dataset_exists_in_cache(name)
        self._assert_task_exists_in_dataset_in_cache(name, task)

        self.manager.data["dataset"][name]["tasks"].pop(task)

        self._update_cache_data()

    def list(self, name=None):
        """Returns a list of all dataset names.

        Parameters
        ----------
        name : str, optional
            Name of the dataset.

        Returns
        -------
        list
            Names of tasks. If a dataset name is used,
            it lists only the task names for that specific
            dataset.

        """
        if name is not None:
            tasks = self._list_all_tasks_from_single_dataset(name)
        else:
            tasks = self._list_all_tasks_from_all_datasets()
        return tasks

    def _list_all_tasks_from_single_dataset(self, name):
        self._assert_dataset_exists_in_cache(name)
        tasks = self.manager.data["dataset"][name]["tasks"].keys()
        tasks = sorted(list(tasks))
        return tasks

    def _list_all_tasks_from_all_datasets(self):
        datasets = self.manager.data["dataset"]
        tasks = [task for dataset in datasets for task in datasets[dataset]["tasks"]]
        tasks = sorted(list(set(tasks)))
        return tasks

    def exists(self, task, name=None):
        """Checks if a task name exists in the cache.

        Also, if a dataset name is specified, it checks
        if the task name exists for that particular
        dataset only.

        Parameters
        ----------
        task : str
            Name of the task.
        name : str, optional
            Name of the dataset.

        Returns
        -------
        bool
            Returns True if the task exists in the cache
            or in a dataset. Otherwise, returns False.

        """
        assert task, "Must input a valid task name."
        if name is not None:
            return self._is_task_in_dataset(name, task)
        else:
            return self._is_task_in_any_dataset(task)

    def _is_task_in_dataset(self, name, task):
        self._assert_dataset_exists_in_cache(name)
        tasks = self.list(name)
        return task in tasks

    def _is_task_in_any_dataset(self, task):
        tasks = self.list()
        return task in tasks

    def info(self, name=None):
        """Prints the dataset information contained in the cache.

        Parameters
        ----------
        name : str, optional
            Name of the dataset.

        """
        if name is not None:
            self._print_info_of_all_tasks_of_single_dataset(name)
        else:
            self._print_info_of_all_tasks_of_all_datasets()

    def _print_info_of_all_tasks_of_single_dataset(self, name):
        self._assert_dataset_exists_in_cache(name)
        tasks = self.list(name)
        text_box_msg = 'Tasks ({})'.format(name)
        self._print_text_box_data_to_screen(text_box_msg, tasks)

    def _print_text_box_data_to_screen(self, msg, data):
        pp = pprint.PrettyPrinter(indent=4)
        print_text_box(msg)
        pp.pprint(data)
        print('')

    def _print_info_of_all_tasks_of_all_datasets(self):
        tasks = self._get_all_tasks_with_datasets_per_task()
        text_box_msg = 'Tasks (all datasets)'
        self._print_text_box_data_to_screen(text_box_msg, tasks)

    def _get_all_tasks_with_datasets_per_task(self):
        tasks = self._get_all_tasks_plus_datasets()
        return self._parse_sorted_list_of_unique_datasets(tasks)

    def _get_all_tasks_plus_datasets(self):
        tasks = {}
        datasets = self.manager.data["dataset"]
        for dataset in datasets:
            for task in datasets[dataset]["tasks"]:
                if task in tasks:
                    tasks[task].append(dataset)
                else:
                    tasks[task] = [dataset]
        return tasks

    def _parse_sorted_list_of_unique_datasets(self, tasks):
        for task in tasks:
            tasks[task] = sorted(list(set(tasks[task])))
        return tasks


class CacheManagerCategory:
    """Manage the cache's category configurations."""

    def __init__(self, manager):
        """Initialize class."""
        assert manager, "Must input a valid cache manager."
        self.manager = manager

    def get(self, category):
        """Retrieves the data of a category from the cache.

        Parameters
        ----------
        category : str
            Name of the category.

        Returns
        -------
        dict
            Information about the category.

        """
        assert category, "Must input a valid category name."
        try:
            return self.manager.data["category"][category]
        except KeyError:
            raise KeyError("The category \'{}\' does not exist in cache.".format(category))

    def get_by_dataset(self, name):
        """Retrieves all categories and tasks that contain the dataset name.

        Parameters
        ----------
        name : str
            Name of the dataset.

        Returns
        -------
        dict
            Information about the categories containing
            the dataset name.

        """
        assert name, "Must input a valid dataset name."
        matching_categories = {}
        categories = self.manager.data["category"]
        for category in categories:
            matching_category = self._get_category_with_matching_dataset_name(name, category)
            matching_categories.update(matching_category)
        return matching_categories

    def _get_category_with_matching_dataset_name(self, name, category):
        matching_category = {}
        categories = self.manager.data["category"]
        if name in categories[category]:
            matching_category.update({
                category: {
                    name: categories[category][name]
                }
            })
        return matching_category

    def get_by_task(self, task):
        """Retrieves all categories and task that contain the task name.

        Parameters
        ----------
        task : str
            Name of the task.

        Returns
        -------
        dict
            Information about the categories containing
            the task name.

        """
        assert task, "Must input a valid task name."
        matching_categories = {}
        categories = self.manager.data["category"]
        for category in categories:
            matching_category = self._get_matching_categories_by_task(category, task)
            if any(matching_category):
                matching_categories.update({category: matching_category})
        return matching_categories

    def _get_matching_categories_by_task(self, category, task):
        categories = self.manager.data["category"]
        matching_category = {}
        for name in categories[category]:
            if task in categories[category][name]:
                matching_category.update({name: [task]})
        return matching_category

    def exists(self, category):
        """Checks if a category exists in cache.

        Parameters
        ----------
        category : str
            Name of the category.

        Returns
        -------
        bool
            True if the category name exists.
            Otherwise, returns False.

        """
        assert category, "Must input a valid category name."
        return category in self.manager.data["category"]

    def exists_task(self, task):
        """Checks if a task exists in any category in cache.

        Parameters
        ----------
        task : str
            Name of the task.

        Returns
        -------
        bool
            True if the task exists for at least one category.
            Otherwise, returns False.

        """
        assert task, "Must input a valid task name."
        return any(self.get_by_task(task))

    def exists_dataset(self, dataset):
        """Checks if a dataset exists in any category in cache.

        Parameters
        ----------
        dataset : str
            Name of the dataset.

        Returns
        -------
        bool
            True if the dataset exists for at least one category.
            Otherwise, returns False.

        """
        assert dataset, "Must input a valid dataset name."
        return any(self.get_by_dataset(dataset))

    def list(self):
        """Returns a list of all category names.

        Returns
        -------
        list
            Names of categories.

        """
        return list(sorted(self.manager.data["category"].keys()))

    def info(self, categories=()):
        """Prints the cache and download data dir paths of the cache."""
        pp = pprint.PrettyPrinter(indent=4)
        print_text_box('Category')
        data = self.manager.data["category"]
        if any(categories):
            data = self._get_filtered_category_data(data, categories)
        pp.pprint(data)
        print('')

    def _get_filtered_category_data(self, data, categories):
        assert categories
        if isinstance(categories, str):
            categories_ = [categories.lower()]
        else:
            categories_ = [category.lower() for category in categories]
        categories_cache_key = [category for category in data if category.lower() in categories_]
        filtered_data = {}
        if any(categories_cache_key):
            for key in categories_cache_key:
                filtered_data[key] = data[key]
        return filtered_data


class CacheManagerInfo:
    """Manage the cache's information configurations."""

    def __init__(self, manager):
        """Initialize class."""
        assert manager, "Must input a valid cache manager."
        self.manager = manager

    def _set_cache_dir(self, path):
        """Set the root cache dir to store all metadata files"""
        assert path, 'Must input a directory path'
        self.manager.cache_dir = path

    def _get_cache_dir(self):
        """Get the root cache dir path."""
        return self.manager.cache_dir

    cache_dir = property(_get_cache_dir, _set_cache_dir)

    def reset_cache_dir(self):
        """Reset the root cache dir path."""
        self.manager.reset_cache_dir()

    def _set_download_dir(self, path):
        """Set the root save dir path for downloaded data."""
        assert path, 'Must input a non-empty path.'
        self.manager.download_dir = path

    def _get_download_dir(self):
        """Get the root save dir path."""
        return self.manager.download_dir

    download_dir = property(_get_download_dir, _set_download_dir)

    def reset_download_dir(self):
        """Reset the root download dir path."""
        self.manager.reset_download_dir()

    def reset(self):
        """Resets the cache and download dirs to default."""
        self.reset_cache_dir()
        self.reset_download_dir()

    def info(self):
        """Prints the cache and download data dir paths of the cache."""
        pp = pprint.PrettyPrinter(indent=4)
        print_text_box('Info')
        pp.pprint(self.manager.data["info"])
        print('')
