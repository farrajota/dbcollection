.. _mnist_readme:

================================
MNIST Handwritten Digit Database
================================

The **MNIST** database of handwritten digits has a
training set of 60,000 examples, and a test set of 10,000 examples. It is a
subset of a larger set available from **MNIST**.
The digits have been size-normalized and centered in a fixed-size image.


Use cases
=========

Image classification.


Properties
==========

- ``name``: mnist
- ``keywords``: image_processing, classification
- ``dataset size``: 11,6 MB
- ``is downloadable``: **yes**
- ``tasks``: :ref:`classification (default) <mnist_readme_classification>`


Tasks
=====

.. _mnist_readme_classification:

classification (default)
------------------------

- :ref:`How to use <classification_how_to_use>`
- :ref:`Properties <classification_properties>`
- :ref:`HDF5 file structure <classification_hdf5_file_structure>`
- :ref:`Fields <classification_fields>`

.. _classification_how_to_use:

How to use
^^^^^^^^^^

.. code-block:: python

    >>> # import the package
    >>> import dbcollection as dbc
    >>>
    >>> # load the dataset
    >>> mnist = dbc.load('mnist', 'classification')
    >>> mnist
    DataLoader: "mnist" (classification task)


.. _classification_properties:

Properties
^^^^^^^^^^

- ``primary use``: image classification
- ``description``: Contains image tensors and label annotations for image classification.
- ``sets``: train, test
- ``metadata file size in disk``: 6,8 MB
- ``has annotations``: **yes**
    - ``which``:
        - labels for each image class/category.
- ``available fields``:
    - :ref:`classes <classification_fields_classes>`
    - :ref:`images <classification_fields_images>`
    - :ref:`labels <classification_fields_labels>`
    - :ref:`object_fields <classification_fields_object_fields>`
    - :ref:`object_ids <classification_fields_object_ids>`
    - :ref:`list_images_per_class <classification_fields_list_images_per_class>`

.. _classification_hdf5_file_structure:

HDF5 file structure
^^^^^^^^^^^^^^^^^^^

::

    /
    ├── train/
    │   ├── classes        # dtype=np.uint8, shape=(10,2)   (note: string in ASCII format)
    │   ├── images         # dtype=np.uint8, shape=(60000,28,28)
    │   ├── labels         # dtype=np.uint8, shape=(60000,)
    │   ├── object_fields  # dtype=np.uint8, shape=(2,7)    (note: string in ASCII format)
    │   ├── object_ids     # dtype=np.int32, shape=(60000,2)
    │   └── list_images_per_class   # dtype=np.int32, shape=(10,6742))
    │
    └── test/
        ├── classes        # dtype=np.uint8, shape=(10,2)  (note: string in ASCII format)
        ├── images         # dtype=np.uint8, shape=(10000,28,28)
        ├── labels         # dtype=np.uint8, shape=(10000,)
        ├── object_fields  # dtype=np.uint8, shape=(2,7)    (note: string in ASCII format)
        ├── object_ids     # dtype=np.int32, shape=(10000,2)
        └── list_images_per_class   # dtype=np.int32, shape=(10,1135))


.. _classification_fields:

Fields
^^^^^^

.. _classification_fields_classes:

- ``classes``: class names
    - ``available in``: train, test
    - ``dtype``: np.uint8
    - ``is padded``: True
    - ``fill value``: 0
    - ``note``: strings stored in ASCII format

.. _classification_fields_images:

- ``images``: images tensor
    - ``available in``: train, test
    - ``dtype``: np.uint8
    - ``is padded``: False
    - ``fill value``: -1

.. _classification_fields_labels:

- ``labels``: class ids
    - ``available in``: train, test
    - ``dtype``: np.uint8
    - ``is padded``: False
    - ``fill value``: -1

.. _classification_fields_object_fields:

- ``object_fields``: list of field names of the object id list
    - ``available in``: train, test
    - ``dtype``: np.uint8
    - ``is padded``: True
    - ``fill value``: 0
    - ``note``: strings stored in ASCII format
    - ``note``: key field (*field name* aggregator)

.. _classification_fields_object_ids:

- ``object_ids``: list of field ids
    - ``available in``: train, test
    - ``dtype``: np.int32
    - ``is padded``: False
    - ``fill value``: -1
    - ``note``: key field (*field id* aggregator)

.. _classification_fields_list_images_per_class:

- ``list_images_per_class``: list of image ids per class
    - ``available in``: train, test
    - ``dtype``: np.int32
    - ``is padded``: True
    - ``fill value``: -1
    - ``note``: pre-ordered list


Disclaimer
==========

All rights reserved to the original creators of **MNIST**.

For information about the dataset and its terms of use, please see this `link <http://yann.lecun.com/exdb/mnist/>`_.
