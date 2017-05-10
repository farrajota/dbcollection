"""
Datasets list.

All available datasets must be added in this file.
"""


#---------------------------------------------------------
# List of image processing datasets
#---------------------------------------------------------

from . import mscoco
from . import cifar, pascal, mnist, imagenet
from . import caltech, inria
from . import flic, leeds_sports_pose, mpii_pose
from . import ucf


human_action = {
    "ucf101" : ucf.ucf101.UCF101,
    "ucfsports" : ucf.ucfsports.UCFSports
}

human_pose = {
    "flic" : flic.Flic,
    "leeds_sports_pose" : leeds_sports_pose.lsp.LSP,
    "leeds_sports_pose_extended" : leeds_sports_pose.lsp_extended.LSPe,
    "mpii_pose" : mpii_pose.MPIIPose
}

object_classification = {
    "cifar10" : cifar.cifar10.Cifar10,
    "cifar100" : cifar.cifar100.Cifar100,
    "ilsvrc2012": imagenet.ILSVRC2012,
    'mnist': mnist.MNIST,
    "pascal_voc_2007" : pascal.voc_2007.PascalVOC2007,
    "mscoco" : mscoco.MSCOCO
}

pedestrian_detection = {
    "caltech_pedestrian" : caltech.pedestrian.Pedestrian,
    "inria_pedestrian" : inria.Pedestrian
}


#---------------------------------------------------------
# MAIN list
#---------------------------------------------------------

datasets = {}
datasets.update(object_classification) # object classification
datasets.update(human_action) # human action
datasets.update(pedestrian_detection) # pedestrian detection/recognition
datasets.update(human_pose) # human pose

# list of all dataset's names
available_datasets = list(datasets.keys())