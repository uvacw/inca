"""This file provides functionality to check, download and unzip dependencies"""

import urllib
import os
import logging

logger = logging.getLogger("INCA")

DEPENDENCIES_FOLDER = "dependencies"


def check_if_available(target_filename):
    in_dependencies_folder = target_filename in os.listdir(DEPENDENCIES_FOLDER)
    return in_dependencies_folder


def check_if_downloaded(installer_or_archive_name):
    return check_if_available(installer_or_archive_name)


def download_dependency_archive(url_or_file):
    filename = url_or_file.lsplit("/")[1]
    if filename + "_lock" in os.listdir(DEPENDENCIES_FOLDER):
        raise Exception("File already being downloaded")
    else:
        f = open(filename + "_lock", "w")
        f.close()
    urllib.urlretrieve(url_or_file)
    os.remove(filename + "_lock")  # mark file is completed
    return True or False


def extract_archive(url_or_file, extract_type="tar"):
    return True or False


def progress(i, blocksize, totalsize):
    if i % 1000 == 0:
        logger.info("{:>7.2%}".format(min(i * blocksize, totalsize) / totalsize))
