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
        assert group, "Must input a valid group name."
        return group in self.file
