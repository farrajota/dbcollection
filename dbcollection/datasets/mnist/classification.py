"""
MNIST classification process functions.
"""


from __future__ import print_function, division
import os
import numpy as np

from dbcollection.datasets import BaseTaskNew
from dbcollection.utils.string_ascii import convert_str_to_ascii as str2ascii
from dbcollection.utils.pad import pad_list


class Classification(BaseTaskNew):
    """MNIST Classification preprocessing functions."""

    # metadata filename
    filename_h5 = 'classification'

    classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    def load_data(self):
        """
        Load the data from the files.
        """
        yield {"train": self.load_data_train()}
        yield {"test": self.load_data_test()}

    def load_data_train(self):
        """
        Fetch train data.
        """
        train_images, train_labels, size_train = self.get_train_data()

        train_data = train_images.reshape(size_train, 28, 28)
        train_object_list = np.array([[i, train_labels[i]] for i in range(size_train)])
        classes = str2ascii(self.classes)

        return {
            "classes": classes,
            "images": train_data,
            "labels": train_labels,
            "object_fields": str2ascii(['images', 'labels']),
            "object_ids": train_object_list,
            "list_images_per_class": self.get_list_images_per_class(train_labels)
        }

    def get_train_data(self):
        """Loads the data of the train set."""
        fname_train_imgs = os.path.join(self.data_path, 'train-images.idx3-ubyte')
        fname_train_lbls = os.path.join(self.data_path, 'train-labels.idx1-ubyte')
        train_images = self.load_images_numpy(fname_train_imgs)
        train_labels = self.load_labels_numpy(fname_train_lbls)
        size_train = 60000
        return train_images, train_labels, size_train

    def get_list_images_per_class(self, set_labels):
        """Builds a list of images per class."""
        images_per_class = []
        labels = np.unique(set_labels)
        for label in labels:
            images_idx = np.where(set_labels == label)[0].tolist()
            images_per_class.append(images_idx)
        return np.array(pad_list(images_per_class, 1), dtype=np.int32)

    def load_images_numpy(self, fname):
        """Load images from file as numpy array."""
        with open(fname, 'rb') as f:
            annotations = f.read(16)
            data = np.fromfile(f, dtype=np.int8)
        return data

    def load_labels_numpy(self, fname):
        """Load labels from file as numpy array."""
        with open(fname, 'rb') as f:
            annotations = f.read(8)
            data = np.fromfile(f, dtype=np.int8)
        return data

    def load_data_test(self):
        """
        Fetch test data.
        """
        test_images, test_labels, size_test = self.get_test_data()

        test_data = test_images.reshape(size_test, 28, 28)
        test_object_list = np.array([[i, test_labels[i]] for i in range(size_test)])
        classes = str2ascii(self.classes)

        return {
            "classes": classes,
            "images": test_data,
            "labels": test_labels,
            "object_fields": str2ascii(['images', 'labels']),
            "object_ids": test_object_list,
            "list_images_per_class": self.get_list_images_per_class(test_labels)
        }

    def get_test_data(self):
        """Loads the data of the test set."""
        fname_test_imgs = os.path.join(self.data_path, 't10k-images.idx3-ubyte')
        fname_test_lbls = os.path.join(self.data_path, 't10k-labels.idx1-ubyte')
        test_images = self.load_images_numpy(fname_test_imgs)
        test_labels = self.load_labels_numpy(fname_test_lbls)
        size_test = 10000
        return test_images, test_labels, size_test

    def process_set_metadata(self, data, set_name):
        """
        Saves the metadata of a set.
        """
        self.save_field_to_hdf5(set_name, 'classes', data["classes"],
                                dtype=np.uint8, fillvalue=0)
        self.save_field_to_hdf5(set_name, 'images', data["images"],
                                dtype=np.uint8, fillvalue=-1)
        self.save_field_to_hdf5(set_name, 'labels', data["labels"],
                                dtype=np.uint8, fillvalue=0)
        self.save_field_to_hdf5(set_name, 'object_fields', data["object_fields"],
                                dtype=np.uint8, fillvalue=0)
        self.save_field_to_hdf5(set_name, 'object_ids', data["object_ids"],
                                dtype=np.int32, fillvalue=-1)
        self.save_field_to_hdf5(set_name, 'list_images_per_class', data["list_images_per_class"],
                                dtype=np.int32, fillvalue=-1)
