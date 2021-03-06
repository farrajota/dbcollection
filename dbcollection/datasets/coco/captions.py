"""
COCO Captions 2015/2016 process functions.
"""


from __future__ import print_function, division
import os
from collections import OrderedDict
import numpy as np
import progressbar

from dbcollection.datasets import BaseTask
from dbcollection.utils.string_ascii import convert_str_to_ascii as str2ascii
from dbcollection.utils.pad import pad_list
from dbcollection.utils.file_load import load_json
from dbcollection.utils.hdf5 import hdf5_write_data

from .load_data_test import load_data_test


class Caption2015(BaseTask):
    """COCO Captions (2015) preprocessing functions."""

    # metadata filename
    filename_h5 = 'caption_2015'

    image_dir_path = {
        "train": 'train2014',
        "val": 'val2014',
        "test": 'test2014'
    }

    annotation_path = {
        "train": os.path.join('annotations', 'captions_train2014.json'),
        "val": os.path.join('annotations', 'captions_val2014.json'),
        "test": os.path.join('annotations', 'image_info_test2014.json')
    }

    def load_data_trainval(self, set_name, image_dir, annotation_path):
        """
        Load train+val data
        """
        data = {}

        # load annotations file
        if self.verbose:
            print('  > Loading annotation file: ' + annotation_path)
        annotations = load_json(annotation_path)

        # progressbar
        if self.verbose:
            prgbar = progressbar.ProgressBar(max_value=len(annotations['annotations']))

        # parse annotations
        # images
        if self.verbose:
            print('  > Processing image annotations... ')
        images = {}
        for i, annot in enumerate(annotations['images']):
            images[annot['id']] = {
                "file_name": os.path.join(image_dir, annot['file_name']),
                "width": annot['width'],
                "height": annot['height'],
                "id": annot['id'],
                "coco_url": annot['coco_url']
            }

        if self.verbose:
            print('  > Processing data annotations... ')
        for i, annot in enumerate(annotations['annotations']):
            img_id = annot['image_id']
            img_annotation = images[img_id]

            caption = annot["caption"]

            if img_id in data.keys():
                data[img_id]['captions'].append(caption)
            else:
                img_annotation = images[img_id]
                data[img_id] = {
                    "file_name": img_annotation['file_name'],
                    "width": img_annotation['width'],
                    "height": img_annotation['height'],
                    "id": img_annotation['id'],
                    "coco_url": img_annotation['coco_url'],
                    "captions": [caption]
                }

            # update progressbar
            if self.verbose:
                prgbar.update(i)

        # reset progressbar
        if self.verbose:
            prgbar.finish()

        return {set_name: [OrderedDict(sorted(data.items())),
                           annotations]}

    def load_data(self):
        """
        Load data of the dataset (create a generator).
        """
        for set_name in self.image_dir_path:
            if self.verbose:
                print('\n> Loading data files for the set: ' + set_name)

            # image dir
            image_dir = os.path.join(self.data_path, self.image_dir_path[set_name])

            # annotation file path
            annot_filepath = os.path.join(self.data_path, self.annotation_path[set_name])

            if 'test' in set_name:
                yield load_data_test(set_name, image_dir, annot_filepath, self.verbose)
            else:
                yield self.load_data_trainval(set_name, image_dir, annot_filepath)

    def process_set_metadata(self, data, set_name):
        """
        Saves the metadata of a set.
        """
        hdf5_handler = self.hdf5_manager.get_group(set_name)
        image_dir = os.path.join(self.data_path, self.image_dir_path[set_name])
        if "test" in set_name:
            is_test = True
            data_ = data[0]
            filename_ids = data[1]
            annotations = data[2]
            category = data[3]
            supercategory = data[4]
            category_id = data[5]
        else:
            is_test = False
            data_ = data[0]
            annotations = data[1]

        image_filenames = []
        width = []
        height = []
        coco_urls = []
        image_id = []
        caption = []
        object_id = []

        # coco id lists
        # These are order by entry like in the annotation files.
        # I.e., coco_images_ids[0] has the object_id with the file_name, id, height, etc.
        # as coco_annotation_file[set_name]["images"][0]
        coco_images_ids = []
        coco_categories_ids = []

        if is_test:
            object_fields = ["image_filenames", "coco_urls", "width", "height"]
        else:
            object_fields = ["image_filenames", "coco_urls", "width", "height", "captions"]

        list_captions_per_image = []
        list_object_ids_per_image = []

        if self.verbose:
            print('> Adding data to default group:')
            prgbar = progressbar.ProgressBar(max_value=len(data_))

        counter = 0
        for i, key in enumerate(data_):
            annotation = data_[key]
            image_filenames.append(annotation["file_name"])
            width.append(annotation["width"])
            height.append(annotation["height"])
            coco_urls.append(annotation["coco_url"])
            image_id.append(annotation["id"])

            if is_test:
                object_id.append([i, i, i, i])
                list_object_ids_per_image.append([i])
            else:
                captions_per_image = []
                for cap in annotation["captions"]:
                    caption.append(cap)

                    # object_id
                    # [filename, caption, width, height]
                    object_id.append([i, i, i, i, counter])

                    captions_per_image.append(counter)

                    # update counter
                    counter += 1

                list_captions_per_image.append(captions_per_image)
                list_object_ids_per_image.append(captions_per_image)

            # update progressbar
            if self.verbose:
                prgbar.update(i)

        # update progressbar
        if self.verbose:
            prgbar.finish()

        # set coco id lists
        if self.verbose:
            print('> Processing coco lists:')
            prgbar = progressbar.ProgressBar(max_value=len(annotations['images']))

        for i, annot in enumerate(annotations['images']):
            fname_id = image_filenames.index(os.path.join(image_dir, annot['file_name']))
            coco_images_ids.append(fname_id)

            # update progressbar
            if self.verbose:
                prgbar.update(i)

        # update progressbar
        if self.verbose:
            prgbar.finish()

        if is_test:
            coco_categories_ids = list(range(len(category)))

        hdf5_write_data(hdf5_handler, 'image_filenames',
                        str2ascii(image_filenames), dtype=np.uint8,
                        fillvalue=0)
        hdf5_write_data(hdf5_handler, 'coco_urls',
                        str2ascii(coco_urls), dtype=np.uint8,
                        fillvalue=0)
        hdf5_write_data(hdf5_handler, 'width',
                        np.array(width, dtype=np.int32),
                        fillvalue=-1)
        hdf5_write_data(hdf5_handler, 'height',
                        np.array(height, dtype=np.int32),
                        fillvalue=-1)
        hdf5_write_data(hdf5_handler, 'image_id',
                        np.array(image_id, dtype=np.int32),
                        fillvalue=-1)
        hdf5_write_data(hdf5_handler, 'coco_images_ids',
                        np.array(coco_images_ids, dtype=np.int32),
                        fillvalue=-1)
        hdf5_write_data(hdf5_handler, 'object_ids',
                        np.array(object_id, dtype=np.int32),
                        fillvalue=-1)
        hdf5_write_data(hdf5_handler, 'object_fields',
                        str2ascii(object_fields), dtype=np.uint8,
                        fillvalue=0)
        hdf5_write_data(hdf5_handler, 'list_object_ids_per_image',
                        np.array(pad_list(list_object_ids_per_image, -1), dtype=np.int32),
                        fillvalue=-1)

        if not is_test:
            hdf5_write_data(hdf5_handler, 'captions',
                            str2ascii(caption), dtype=np.uint8,
                            fillvalue=0)
            hdf5_write_data(hdf5_handler, 'list_captions_per_image',
                            np.array(pad_list(list_captions_per_image, -1), dtype=np.int32),
                            fillvalue=-1)
        else:
            hdf5_write_data(hdf5_handler, 'category',
                            str2ascii(category), dtype=np.uint8,
                            fillvalue=0)
            hdf5_write_data(hdf5_handler, 'supercategory',
                            str2ascii(supercategory), dtype=np.uint8,
                            fillvalue=0)
            hdf5_write_data(hdf5_handler, 'coco_categories_ids',
                            np.array(coco_categories_ids, dtype=np.int32),
                            fillvalue=-1)


# ---------------------------------------------------------
#  Captions 2016
# ---------------------------------------------------------

class Caption2016(Caption2015):
    """COCO Caption (2016) preprocessing functions."""

    # metadata filename
    filename_h5 = 'caption_2016'

    image_dir_path = {
        "train": 'train2014',
        "val": 'val2014',
        "test": 'test2015',
        "test_dev": "test2015"
    }

    annotation_path = {
        "train": os.path.join('annotations', 'captions_train2014.json'),
        "val": os.path.join('annotations', 'captions_val2014.json'),
        "test": os.path.join('annotations', 'image_info_test2015.json'),
        "test_dev": os.path.join('annotations', 'image_info_test-dev2015.json')
    }
