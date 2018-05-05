"""
hdf5 utility functions.
"""


import h5py
import numpy as np


def hdf5_write_data(h5_handler, field_name, data, dtype=None, chunks=True,
                    compression="gzip", compression_opts=4, fillvalue=-1):
    """Write/store data into a hdf5 file.

    Parameters
    ----------
    h5_handler : h5py._hl.group.Group
        Handler for an HDF5 group object.
    field_name : str
        Field name.
    data : np.ndarray
        Data array.
    dtype : np.dtype, optional
        Data type.
    chunks : bool, optional
        Store data as chunks if True.
    compression : str, optional
        Compression algorithm type.
    compression_opts : int, optional
        Compression option (range: [1,10])
    fillvalue : int/float, optional
        Value to pad the data.

    Returns
    -------
    h5py._hl.dataset.Dataset
        Handler for an HDF5 dataset object.
    """
    assert h5_handler, "Must input a hdf5 file handler"
    assert field_name, 'Must input a field name.'
    assert isinstance(data, np.ndarray), 'Data must be a numpy array.'

    if dtype is None:
        dtype = data.dtype

    h5_field = h5_handler.create_dataset(name=field_name,
                                         data=data,
                                         shape=data.shape,
                                         dtype=dtype,
                                         chunks=chunks,
                                         compression=compression,
                                         compression_opts=compression_opts,
                                         fillvalue=fillvalue)
    return h5_field


class HDF5Manager(object):
    """HDF5 metadata file manager.

    Parameters
    ----------
    filename : str
        File name + path of the HDF5 file.

    Arguments
    ---------
    filename : str
        File name + path of the HDF5 file.

    """
    def __init__(self, filename):
        assert filename, "Must insert a valid file name."
        self.filename = filename
        self.file = self.open_file(filename)

    def open_file(self, filename):
        """Opens/creates an HDF5 file in disk."""
        assert filename
        return h5py.File(filename, 'w', libver='latest')

    def close(self):
        self.file.close()

    def exists_group(self, group):
        """Checks if a group exists in the file."""
        assert group, "Must input a valid group name."
        return group in self.file

    def create_group(self, name):
        """Creates a group in the file."""
        assert name, "Must input a name for the group."
        return self.file.create_group(name)

    def add_field_to_group(self, group, field, data, dtype=None, fillvalue=-1, chunks=True,
                           compression="gzip", compression_opts=4):
        """Writes the data of a field into an HDF5 file.

        Parameters
        ----------
        group : str
            Name of the group.
        field : str
            Name of the field (h5 dataset).
        data : np.ndarray
            Data array.
        dtype : np.dtype, optional
            Data type.
        chunks : bool, optional
            Stores the data as chunks if True.
        compression : str, optional
            Compression algorithm type.
        compression_opts : int, optional
            Compression option (range: [1,10])
        fillvalue : int/float, optional
            Value to pad the data array.

        Returns
        -------
        h5py._hl.dataset.Dataset
            Object handler of the created HDF5 dataset.

        """
        assert group, "Must input a valid group name."
        assert field, "Must input a valid field name."
        assert isinstance(data, np.ndarray), "Must input a valid numpy data array."
        assert dtype, "Must input a valid numpy data type."
        assert fillvalue is not None, "Must input a valid fill value to pad the array."
        assert chunks is not None, "Must input a valid chunk size."
        assert compression, "Must input a valid compression algorithm"
        assert compression_opts, "Must input a valid compression value."

        h5_group = self.get_group(group)

        if dtype is None:
            dtype = data.dtype

        h5_field = h5_group.create_dataset(
            name=field,
            data=data,
            shape=data.shape,
            dtype=dtype,
            chunks=chunks,
            compression=compression,
            compression_opts=compression_opts,
            fillvalue=fillvalue
        )

        return h5_field

    def get_group(self, group):
        if self.exists_group(group):
            return self.file[group]
        else:
            return self.create_group(group)
